
import logging

import requests

from config import PUSHOVER_APP_TOKEN, PUSHOVER_USER_KEY

logger = logging.getLogger(__name__)


class NotificationService:
    def is_configured(self) -> bool:
        return bool(PUSHOVER_USER_KEY and PUSHOVER_APP_TOKEN)

    def send(self, title: str, message: str) -> bool:
        if not self.is_configured():
            logger.warning("Pushover credentials are not configured")
            return False

        try:
            response = requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": PUSHOVER_APP_TOKEN,
                    "user": PUSHOVER_USER_KEY,
                    "title": title,
                    "message": message,
                },
                timeout=10,
            )
            if not response.ok:
                logger.error(
                    "Pushover request failed: %s %s",
                    response.status_code,
                    response.text,
                )
            return response.ok
        except requests.RequestException as exc:
            logger.error("Pushover request error: %s", exc)
            return False
