
import json
import logging
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from services.interview_store import InterviewStore
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

SA_TIMEZONE = ZoneInfo("Africa/Johannesburg")

INTERVIEW_KEYWORDS = (
    "meet",
    "interview",
    "schedule",
    "meeting",
    "book a call",
    "set up a call",
    "availability",
)


class InterviewService:
    def __init__(self, base_dir=None):
        self.notifications = NotificationService()
        self.store = InterviewStore(base_dir) if base_dir else None

    def schedule(
        self,
        date: str,
        time: str,
        topic: str,
        link: str = "",
        address: str = "",
        timezone: str = "Africa/Johannesburg",
        source: str = "form",
    ) -> tuple[dict, int]:
        if not date or not topic:
            return {"error": "Date and topic are required"}, 400

        if not link and not address:
            return {
                "error": "Provide a meeting link or a physical address"
            }, 400

        if not time:
            time = "12:00"

        try:
            sa_datetime = self._to_sa_datetime(date, time, timezone)
        except (ValueError, KeyError) as exc:
            logger.error("Invalid schedule input: %s", exc)
            return {"error": "Invalid date, time, or timezone"}, 400

        payload = {
            "date": date,
            "time": time,
            "topic": topic,
            "link": link,
            "address": address,
            "timezone": timezone,
            "source": source,
            "sa_datetime": sa_datetime.isoformat(),
        }

        if self.store:
            self.store.save(payload)

        body = self._format_notification(payload, sa_datetime)
        notified = self.notifications.send("New Interview Request", body)

        if not notified:
            logger.warning("Pushover notification was not delivered")

        sa_label = sa_datetime.strftime("%d %b %Y at %H:%M")
        return {
            "action": "notification",
            "message": (
                "Your interview request has been received. "
                f"Kgothatso has been notified for {sa_label} SAST."
            ),
        }, 200

    def handle_chat_request(self, message: str, ai_service) -> dict:
        details = ai_service.extract_interview_details(message)

        if details:
            result, status = self.schedule(
                date=details.get("date", ""),
                time=details.get("time", "12:00"),
                topic=details.get("topic") or "Interview request via chat",
                link=details.get("link", ""),
                address=details.get("address", ""),
                timezone=details.get("timezone") or "Africa/Johannesburg",
                source="chat",
            )
            if status == 200:
                return result

        fallback = self._parse_simple_details(message)
        if fallback:
            result, status = self.schedule(
                date=fallback["date"],
                time=fallback.get("time", "12:00"),
                topic=fallback.get("topic") or "Interview request via chat",
                link=fallback.get("link", ""),
                address=fallback.get("address", ""),
                timezone=fallback.get("timezone") or "Africa/Johannesburg",
                source="chat",
            )
            if status == 200:
                return result

        if self.store:
            self.store.save({"source": "chat", "raw_message": message})
        self.notifications.send("Interview Request via Chat", message)

        missing = self._missing_fields(details or fallback or {})
        if missing:
            return {
                "action": "chat",
                "message": (
                    "I would be happy to help schedule that interview. "
                    f"Please also share: {missing}. "
                    "Or use the Set Interview button on this page."
                ),
            }

        return {
            "action": "notification",
            "message": (
                "Thanks for reaching out. I have passed your meeting request "
                "to Kgothatso."
            ),
        }

    def _format_notification(self, payload: dict, sa_datetime: datetime) -> str:
        lines = [
            f"Source: {payload.get('source', 'form')}",
            f"Date (SAST): {sa_datetime.strftime('%A, %d %B %Y')}",
            f"Time (SAST): {sa_datetime.strftime('%H:%M')}",
            f"Topic: {payload['topic']}",
        ]
        if payload.get("link"):
            lines.append(f"Link: {payload['link']}")
        if payload.get("address"):
            lines.append(f"Address: {payload['address']}")
        if payload.get("timezone") and payload["timezone"] != "Africa/Johannesburg":
            lines.append(f"Visitor timezone: {payload['timezone']}")
        return "\n".join(lines)

    def _parse_simple_details(self, message: str) -> dict | None:
        if not any(keyword in message.lower() for keyword in INTERVIEW_KEYWORDS):
            return None

        details: dict = {}

        date_match = re.search(
            r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
            r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|"
            r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{4})\b",
            message,
            re.I,
        )
        if date_match:
            raw_date = date_match.group(1)
            try:
                if "-" in raw_date:
                    details["date"] = raw_date
                else:
                    details["date"] = datetime.strptime(
                        raw_date.title(), "%d %B %Y"
                    ).strftime("%Y-%m-%d")
            except ValueError:
                pass

        time_match = re.search(
            r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b|\b(\d{1,2}):(\d{2})\b",
            message,
            re.I,
        )
        if time_match:
            if time_match.group(4):
                details["time"] = f"{int(time_match.group(4)):02d}:{time_match.group(5)}"
            else:
                hour = int(time_match.group(1))
                minute = time_match.group(2) or "00"
                meridiem = time_match.group(3).lower()
                if meridiem == "pm" and hour != 12:
                    hour += 12
                if meridiem == "am" and hour == 12:
                    hour = 0
                details["time"] = f"{hour:02d}:{minute}"

        address_match = re.search(
            r"\bat\s+(\d{1,6}\s+[A-Za-z0-9\s,'.-]+(?:street|st|road|rd|avenue|ave|"
            r"district|ext|pretoria|johannesburg)[A-Za-z0-9\s,'.-]*)",
            message,
            re.I,
        )
        if address_match:
            details["address"] = address_match.group(1).strip(" .,")

        topic_match = re.search(
            r"(?:for|about|regarding)\s+(?:a\s+)?(.{3,80}?)(?:\s+on\s+|\s+at\s+|$)",
            message,
            re.I,
        )
        if topic_match:
            details["topic"] = topic_match.group(1).strip(" .,")

        if details.get("date") and (details.get("address") or details.get("link")):
            return details
        return None

    def _missing_fields(self, details: dict) -> str:
        missing = []
        if not details.get("date"):
            missing.append("the date")
        if not details.get("time"):
            missing.append("the time")
        if not details.get("link") and not details.get("address"):
            missing.append("a meeting link or physical address")
        return ", ".join(missing)

    def _to_sa_datetime(self, date: str, time: str, timezone: str) -> datetime:
        local_tz = ZoneInfo(timezone)
        naive = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        localized = naive.replace(tzinfo=local_tz)
        return localized.astimezone(SA_TIMEZONE)

    @staticmethod
    def normalize_submission(date: str, time_value: float) -> tuple[str, str]:
        hours = int(time_value)
        minutes = "30" if time_value % 1 else "00"

        if hours >= 24:
            next_day = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
            date = next_day.strftime("%Y-%m-%d")
            hours -= 24

        time = f"{hours:02d}:{minutes}"
        return date, time

    @staticmethod
    def is_scheduling_message(message: str) -> bool:
        text = message.lower()
        return any(keyword in text for keyword in INTERVIEW_KEYWORDS)
