
import logging
from pathlib import Path

from config import GITHUB_URL, LINKEDIN_URL
from services.ai_service import AIService
from services.interview_service import INTERVIEW_KEYWORDS, InterviewService
from services.resume_loader import ensure_resume, extract_resume_text

logger = logging.getLogger(__name__)


def _whatsapp_url() -> str:
    from config import WHATSAPP_NUMBER
    return f"https://wa.me/{WHATSAPP_NUMBER}" if WHATSAPP_NUMBER else ""


def _normalize_link_text(text: str) -> str:
    return (
        text.lower()
        .replace("linked-in", "linkedin")
        .replace("linked in", "linkedin")
        .replace("git hub", "github")
    )


def _wants_to_open(text: str) -> bool:
    intents = (
        "open",
        "view",
        "show",
        "see",
        "visit",
        "take me",
        "go to",
        "check",
        "browse",
        "navigate",
        "link to",
        "bring up",
        "pull up",
    )
    return any(term in text for term in intents)


def _match_open_link(text: str) -> str | None:
    normalized = _normalize_link_text(text)

    platforms = (
        (("linkedin",), LINKEDIN_URL),
        (("github", "git hub"), GITHUB_URL),
        (("whatsapp", "whats app"), _whatsapp_url()),
    )

    for keywords, url in platforms:
        if not url or not any(keyword in normalized for keyword in keywords):
            continue
        if _wants_to_open(normalized) or normalized.strip() in keywords:
            return url

    return None


class PortfolioService:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.ai = AIService()
        self.interview = InterviewService(base_dir)
        self.resume_path = ensure_resume()
        self.profile_image_path = base_dir / "me" / "kgothatso_BG.png"
        self.context = self._load_context()

    def _load_context(self) -> str:
        summary_path = self.base_dir / "me" / "summary.txt"
        summary = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
        resume = self._load_resume_text()
        return self.ai.build_system_prompt(summary, resume)

    def _load_resume_text(self) -> str:
        return extract_resume_text(self.resume_path)

    def process_message(self, message: str) -> dict:
        text = _normalize_link_text(message)

        if ("resume" in text or "cv" in text) and (
            _wants_to_open(text)
            or "download" in text
            or text.strip() in {"resume", "cv"}
        ):
            return {"action": "download_resume"}

        link = _match_open_link(text)
        if link:
            return {"action": "open_link", "url": link}

        if any(keyword in text for keyword in INTERVIEW_KEYWORDS):
            return self.interview.handle_chat_request(message, self.ai)

        answer = self.ai.generate_response(self.context, message)
        return {"action": "chat", "message": answer}
