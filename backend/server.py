
import logging

from flask import Flask, jsonify, redirect, request, send_file, send_from_directory

from config import (
    BASE_DIR,
    CONTACT_EMAIL,
    CONTACT_PHONE,
    FRONTEND_DIR,
    GITHUB_URL,
    GOOGLE_PLACES_API_KEY,
    LINKEDIN_URL,
    RESUME_URL,
    WHATSAPP_NUMBER,
)
from services.interview_service import InterviewService
from services.portfolio_service import PortfolioService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROFILE_IMAGE = "kgothatso_BG.png"


def create_app():
    app = Flask(__name__)
    portfolio = PortfolioService(BASE_DIR)
    interview = InterviewService(BASE_DIR)

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/me/<path:filename>")
    def profile_assets(filename):
        return send_from_directory(BASE_DIR / "me", filename)

    @app.get("/api/profile-image")
    def profile_image():
        image_path = BASE_DIR / "me" / PROFILE_IMAGE
        if not image_path.exists():
            return jsonify({"error": "Profile image not found"}), 404
        return send_from_directory(BASE_DIR / "me", PROFILE_IMAGE)

    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "Virtuoso Portfolio API",
            "version": "2.2",
        })

    @app.get("/api/config")
    def public_config():
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}" if WHATSAPP_NUMBER else ""

        return jsonify({
            "profile_image": f"/me/{PROFILE_IMAGE}",
            "google_places_api_key": GOOGLE_PLACES_API_KEY or None,
            "contact_email": CONTACT_EMAIL or None,
            "contact_phone": CONTACT_PHONE or None,
            "whatsapp_url": whatsapp_url or None,
            "linkedin_url": LINKEDIN_URL or None,
            "github_url": GITHUB_URL or None,
            "resume_filename": portfolio.resume_path.name
            if portfolio.resume_path.exists()
            else None,
        })

    @app.post("/api/chat")
    def chat():
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "message is required"}), 400

        return jsonify(portfolio.process_message(message))

    @app.post("/api/schedule-interview")
    def schedule_interview():
        data = request.get_json(silent=True) or {}
        result, status = interview.schedule(
            date=data.get("date", "").strip(),
            time=data.get("time", "").strip(),
            topic=data.get("topic", "").strip(),
            link=data.get("link", "").strip(),
            address=data.get("address", "").strip(),
            timezone=data.get("timezone", "Africa/Johannesburg").strip(),
            source="form",
        )
        return jsonify(result), status

    @app.get("/api/download-resume")
    def resume():
        if portfolio.resume_path.exists():
            return send_file(
                portfolio.resume_path,
                as_attachment=True,
                download_name=portfolio.resume_path.name,
            )
        if RESUME_URL:
            return redirect(RESUME_URL, code=302)
        return jsonify({"error": "Resume not found"}), 404

    logger.info("Resume path: %s", portfolio.resume_path)
    logger.info("Frontend: %s", FRONTEND_DIR)
    logger.info("Profile image: %s/me/%s", BASE_DIR, PROFILE_IMAGE)

    return app
