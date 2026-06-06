
import logging
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from docx import Document
from pypdf import PdfReader

from config import BASE_DIR, RESUME_FILENAME, RESUME_PATH, RESUME_URL

logger = logging.getLogger(__name__)


def _cache_path() -> Path:
    if RESUME_URL:
        url_path = unquote(urlparse(RESUME_URL).path)
        name = Path(url_path).name
        if name:
            return BASE_DIR / "me" / name
    return BASE_DIR / "me" / RESUME_FILENAME


def ensure_resume() -> Path:
    """Return a local resume path, downloading from RESUME_URL when configured."""
    if RESUME_URL:
        target = _cache_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            try:
                response = requests.get(RESUME_URL, timeout=30)
                response.raise_for_status()
                target.write_bytes(response.content)
                logger.info("Resume downloaded from RESUME_URL to %s", target)
            except Exception as exc:
                logger.error("Failed to download resume from RESUME_URL: %s", exc)
        if target.exists():
            return target

    if RESUME_PATH.exists():
        return RESUME_PATH

    secret = Path("/etc/secrets") / RESUME_FILENAME
    if secret.exists():
        return secret

    return RESUME_PATH


def extract_resume_text(path: Path) -> str:
    if not path.exists():
        logger.warning("Resume file not found at %s", path)
        return ""

    suffix = path.suffix.lower()
    try:
        if suffix == ".docx":
            document = Document(str(path))
            paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
            return "\n".join(paragraphs).strip()

        if suffix == ".pdf":
            reader = PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages).strip()

        logger.warning("Unsupported resume format: %s", suffix)
        return ""
    except Exception as exc:
        logger.error("Failed to read resume at %s: %s", path, exc)
        return ""
