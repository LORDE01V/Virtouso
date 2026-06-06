
from openai import OpenAI

import json

from config import OPENAI_API_KEY

SYSTEM_PROMPT = """You are Virtuoso, the professional assistant on Kgothatso Mokgashi's portfolio website.

Tone and style:
- Be warm, polite, and professional.
- Greet visitors naturally when the conversation starts.
- Keep answers clear and concise unless more detail is requested.

Scheduling:
- Do NOT write email templates or tell visitors to email someone else to schedule.
- If they want to book a meeting, ask for date, time, topic, and a meeting link or address.
- The website handles scheduling directly once those details are provided.

Knowledge:
- Answer using the profile summary and resume provided below.
- If information is not in the context, say you do not have that detail rather than guessing.
- When asked about projects, explain them in chat.

External links:
- This site can open LinkedIn, GitHub, WhatsApp, and resume downloads when visitors ask (e.g. "open LinkedIn", "view GitHub").
- Never say you are unable to open websites or external links.
- If they want a profile opened, tell them to ask with phrases like "open LinkedIn" or "open GitHub".

Role accuracy:
- Describe Kgothatso as a Full Stack Developer who works with AI — not an "AI Specialist" or "AI Engineer".
- At Khonology, he was Team Lead for a team of four developers.
- He owned delivery of all AI features, but his title was Team Lead, not "AI Lead".
- Never describe him as "AI Lead", "AI Specialist", or say he led five developers.

Profile summary:
{summary}

Resume:
{resume}
"""

EXTRACT_PROMPT = """Extract interview scheduling details from the visitor message.
Return JSON only with these keys:
- date: YYYY-MM-DD or null
- time: HH:MM in 24-hour format or null
- topic: short string or null
- link: meeting URL or null
- address: physical address or null
- timezone: IANA timezone or null

Use null for anything not clearly stated. Do not invent details."""


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def build_system_prompt(self, summary: str, resume: str) -> str:
        return SYSTEM_PROMPT.format(
            summary=summary.strip() or "Not available.",
            resume=resume.strip() or "Not available.",
        )

    def generate_response(self, context: str, message: str) -> str:
        if not self.client:
            return "AI is not configured. Add OPENAI_API_KEY to your environment."

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    def extract_interview_details(self, message: str) -> dict | None:
        if not self.client:
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": EXTRACT_PROMPT},
                    {"role": "user", "content": message},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            data = json.loads(response.choices[0].message.content)
            cleaned = {
                key: (value.strip() if isinstance(value, str) else value)
                for key, value in data.items()
                if value not in (None, "", "null")
            }
            if cleaned.get("date") and (
                cleaned.get("link") or cleaned.get("address")
            ):
                return cleaned
        except Exception:
            return None

        return None
