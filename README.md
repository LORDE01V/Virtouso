# Virtuoso

An AI-powered portfolio platform where recruiters can explore experience, chat with an assistant, download a resume, and schedule interviews.

Built with a **Flask API** (`backend/`) and a **single-page frontend** (`frontend/`), served from one origin in development and production.

## Features

- Animated splash screen with profile card and availability status
- WhatsApp-style chat assistant powered by OpenAI
- Context-aware answers from profile summary and resume (PDF or DOCX)
- Interview scheduling via form or natural language in chat
- Pushover notifications for new interview requests (optional)
- Resume hosted locally or via Cloudinary URL
- Responsive layout for mobile, tablet, and desktop
- Address autocomplete via OpenStreetMap Nominatim

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | HTML, CSS, JavaScript, Tailwind CSS (CDN) |
| Backend | Python, Flask |
| AI | OpenAI API (`gpt-4o-mini`) |
| Documents | pypdf, python-docx |
| Notifications | Pushover (optional) |
| Testing | pytest |

## Project Structure

```
virtuoso/
├── README.md
├── .env.example          # Safe template — copy to .env locally
├── .gitignore
├── Dockerfile
├── render.yaml           # Render Blueprint (Docker deploy)
├── .dockerignore
├── backend/
│   ├── app.py            # Entry point
│   ├── server.py         # Flask app factory and routes
│   ├── config.py         # Environment configuration
│   ├── requirements.txt
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── portfolio_service.py
│   │   ├── interview_service.py
│   │   ├── interview_store.py
│   │   ├── notification_service.py
│   │   └── resume_loader.py
│   ├── me/
│   │   ├── summary.txt   # AI profile context
│   │   └── kgothatso_BG.png
│   ├── data/             # Gitignored — interview logs
│   └── tests/
│       └── test_app.py
└── frontend/
    └── index.html        # Portfolio UI
```

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- Pushover credentials (optional)

### Installation

```bash
git clone <your-repo-url>
cd virtuoso

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r backend/requirements-dev.txt
cp .env.example .env
```

Fill in `.env` at the project root (never commit it).

### Run Locally

```bash
python backend/app.py
```

Open **http://127.0.0.1:7860**

### Verify

```bash
curl http://127.0.0.1:7860/health
```

### Run Tests

```bash
pytest backend/tests/test_app.py
```

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | Chat assistant |
| `RESUME_URL` | No | Public resume URL (Cloudinary, R2, etc.) |
| `PROFILE_IMAGE_URL` | No | Profile photo URL (Cloudinary) |
| `CONTACT_EMAIL` | No | Footer contact (production) |
| `CONTACT_PHONE` | No | Footer contact (production) |
| `WHATSAPP_NUMBER` | No | WhatsApp button (digits with country code) |
| `LINKEDIN_URL` | No | Nav link |
| `GITHUB_URL` | No | Nav link |
| `PUSHOVER_USER_KEY` | No | Interview alerts |
| `PUSHOVER_APP_TOKEN` | No | Interview alerts |

See `.env.example` for the full list.

## Resume Hosting (Cloudinary)

1. Upload your resume to [Cloudinary](https://cloudinary.com) as a **Raw** file (PDF or DOCX).
2. Copy the delivery URL from Media Library.
3. Set in `.env` or on your host:

```env
RESUME_URL=https://res.cloudinary.com/your-cloud/raw/upload/v1234567890/your-resume.docx
```

The app downloads the file on startup for chat context. The download button serves the cached copy.

For local dev, you can also place a resume in `backend/me/` — that takes priority when present.

## Privacy

**Do not commit to GitHub:**

- `.env` and API keys
- Resume files in `backend/me/*.pdf` or `*.docx`
- Profile images in `backend/me/*.png` (use `PROFILE_IMAGE_URL` on Cloudinary)
- `backend/data/` (visitor scheduling logs)
- Hardcoded personal contact details in source files

Contact info is injected at runtime via environment variables on your host.

## Deploy on Render

### Option A — Docker (recommended)

The repo includes a production `Dockerfile` and `render.yaml` blueprint.

1. Push the repo to GitHub.
2. On Render: **New → Blueprint** → connect the repo (uses `render.yaml`),  
   **or** **New → Web Service → Docker** and point to `./Dockerfile`.
3. In the Render dashboard, set secret environment variables:
   - `OPENAI_API_KEY` (required)
   - `RESUME_URL` (your Cloudinary link)
   - `CONTACT_EMAIL`, `CONTACT_PHONE`, `WHATSAPP_NUMBER` (optional)
4. Deploy. Health check hits `/health`.

Docker runs **gunicorn** on the port Render assigns (`PORT`).

### Option B — Native Python (no Docker)

| Setting | Value |
|---------|--------|
| Root directory | *(leave blank)* |
| Build command | `pip install -r backend/requirements.txt` |
| Start command | `gunicorn --chdir backend --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 app:app` |

Add the same environment variables as above.

### Local production-style run

```bash
pip install -r backend/requirements.txt
gunicorn --chdir backend --bind 0.0.0.0:7860 --workers 2 --threads 4 app:app
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Portfolio frontend |
| `GET` | `/health` | Health check |
| `GET` | `/api/config` | Public runtime config |
| `GET` | `/me/<filename>` | Profile assets |
| `POST` | `/api/chat` | Chat assistant |
| `POST` | `/api/schedule-interview` | Schedule an interview |
| `GET` | `/api/download-resume` | Download resume |

## Author

**Kgothatso Mokgashi**  
Software Engineer | Johannesburg, South Africa

- LinkedIn: [kgothatso-mokgashi](https://www.linkedin.com/in/kgothatso-mokgashi/)
- GitHub: [LORDE01V](https://github.com/LORDE01V)

## License

Personal portfolio project — fork and adapt for your own use.
