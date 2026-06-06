"""WSGI entry point for gunicorn (Render / Docker)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app import app  # noqa: E402
