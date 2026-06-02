from app.agents.gemini_client import generate_json
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


def extract_profile_from_text(resume_text: str) -> ResumeExtraction:
    data = generate_json(
        SYSTEM_PROMPT,
        f"Extract profile fields from this resume:\n\n{resume_text[:12000]}",
    )
    return ResumeExtraction.model_validate(data)
