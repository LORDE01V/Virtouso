
from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

load_dotenv(ROOT_DIR / ".env")
load_dotenv()

# Secrets — never commit .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY", "")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Public contact — set on the server, not in source control
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
CONTACT_PHONE = os.getenv("CONTACT_PHONE", "")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "")
LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://www.linkedin.com/in/kgothatso-mokgashi/")
GITHUB_URL = os.getenv("GITHUB_URL", "https://github.com/LORDE01V")

# Resume — local file, Render secret file, or Cloudinary
RESUME_FILENAME = os.getenv("RESUME_FILENAME", "Kgothatso_Mokgashi_Resume.pdf")

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "").strip()
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "").strip()
CLOUDINARY_RESUME_PUBLIC_ID = os.getenv("CLOUDINARY_RESUME_PUBLIC_ID", "").strip()


def _cloudinary_resume_url() -> str:
    if not CLOUDINARY_CLOUD_NAME or not CLOUDINARY_RESUME_PUBLIC_ID:
        return ""
    public_id = CLOUDINARY_RESUME_PUBLIC_ID.strip().lstrip("/")
    return f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/raw/upload/{public_id}"


RESUME_URL = os.getenv("RESUME_URL", "").strip() or _cloudinary_resume_url()


def _resolve_resume_path() -> Path:
    override = os.getenv("RESUME_PATH", "").strip()
    if override:
        return Path(override)

    local = BASE_DIR / "me" / RESUME_FILENAME
    if local.exists():
        return local

    secret = Path("/etc/secrets") / RESUME_FILENAME
    if secret.exists():
        return secret

    return local


RESUME_PATH = _resolve_resume_path()
