import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.resume_extraction import ResumeExtraction

SYSTEM_PROMPT = """You extract structured career profile data from resume text.
Return JSON only with this exact shape:
{
  "name": string | null,
  "location": string | null,
  "education": string | null,
  "summary": string | null,
  "linkedin_url": string | null,
  "portfolio_url": string | null,
  "github_url": string | null,
  "projects": [{"title": string, "summary": string | null}]
}

Rules:
- Use null for fields not found in the resume.
- summary: 2-4 sentence professional summary inferred from the resume.
- education: degrees, schools, graduation years if present.
- projects: up to 8 notable projects or products; summary should mention tech and impact when available.
- URLs must be full https links when present.
- Do not invent employers, projects, or credentials not supported by the resume text.
"""


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        msg = "GEMINI_API_KEY is not configured. Add it to the project root .env file."
        raise RuntimeError(msg)
    return genai.Client(api_key=settings.gemini_api_key)


def extract_profile_from_text(resume_text: str) -> ResumeExtraction:
    client = _client()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=(
            f"{SYSTEM_PROMPT}\n\n"
            f"Extract profile fields from this resume:\n\n{resume_text[:12000]}"
        ),
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    content = response.text
    if not content:
        msg = "Gemini returned an empty response."
        raise RuntimeError(msg)

    data = json.loads(content)
    return ResumeExtraction.model_validate(data)
