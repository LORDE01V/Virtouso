
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
        text = message.lower()

        if "resume" in text or "cv" in text:
            return {"action": "download_resume"}

        if "linkedin" in text:
            return {"action": "open_link", "url": LINKEDIN_URL}

        if self._should_open_github(text):
            return {"action": "open_link", "url": GITHUB_URL}

        if "whatsapp" in text:
            url = _whatsapp_url()
            if url:
                return {"action": "open_link", "url": url}

        if any(keyword in text for keyword in INTERVIEW_KEYWORDS):
            return self.interview.handle_chat_request(message, self.ai)

        answer = self.ai.generate_response(self.context, message)
        return {"action": "chat", "message": answer}

    @staticmethod
    def _should_open_github(text: str) -> bool:
        link_intent = ("view", "open", "show me", "see his", "see my", "take me", "link to")
        github_terms = ("github", "repo", "repos")
        project_terms = ("project", "projects")

        wants_link = any(term in text for term in link_intent)
        mentions_github = any(term in text for term in github_terms)
        mentions_projects = any(term in text for term in project_terms)

        return wants_link and (mentions_github or mentions_projects)
