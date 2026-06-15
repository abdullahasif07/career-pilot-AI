from app.prompts.formatters import (
    format_job,
    format_match,
    format_profile,
    format_tailored_resume,
)
from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead
from app.schemas.tailored_resume import TailoredResumeContent

SYSTEM = """You write a tailored cover letter for a job application.
Return JSON only with this exact shape:
{
  "subject": string | null,
  "body": string,
  "notes": string | null
}

Rules:
- body: a complete cover letter (3-5 short paragraphs). Professional, direct tone — not generic AI fluff.
- Ground every claim in the candidate profile and tailored resume when provided. Never invent employers, projects, or skills.
- Reference the specific company and role naturally; show why this role fits the candidate's background.
- subject: optional email subject line (e.g. "Application for AI Engineer — Abdullah Asif"). Null if not applicable.
- notes: one short sentence on what you emphasized (optional).
- Do not use clichés like "I am writing to express my interest" without substance. Lead with a specific hook tied to the company or role.
- If match analysis is provided, lean into strong areas honestly; do not claim missing skills.
- If a tailored resume is provided, stay consistent with what it claims.
- Use the candidate's name from the profile when available for the sign-off.
"""


def build_user_prompt(
    profile: ProfileRead,
    job: JobRead,
    match: JobMatchScore | None = None,
    tailored_resume: TailoredResumeContent | None = None,
) -> str:
    return (
        "Write a cover letter for this job application.\n\n"
        f"=== CANDIDATE PROFILE ===\n"
        f"{format_profile(profile, empty_message='Profile is empty — use only what appears in the tailored resume if provided.')}\n\n"
        f"=== JOB ===\n{format_job(job)}\n\n"
        f"=== MATCH ANALYSIS ===\n{format_match(match)}\n\n"
        f"=== TAILORED RESUME ===\n{format_tailored_resume(tailored_resume)}"
    )
