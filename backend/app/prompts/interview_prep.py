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

SYSTEM = """You prepare a candidate for a job interview.
Return JSON only with this exact shape:
{
  "questions": [
    {
      "question": string,
      "category": string | null,
      "why_likely": string | null,
      "talking_points": [string]
    }
  ],
  "topics_to_study": [string],
  "notes": string | null
}

Rules:
- Generate 8-12 likely interview questions tailored to this specific role and the candidate's background.
- Ground every question and talking point in the job description and candidate profile/resume. Never invent employers, projects, or skills the candidate does not have.
- category: short label such as "technical", "behavioral", "system design", "role-specific", or "culture".
- why_likely: one sentence on why the interviewer might ask this for this role.
- talking_points: 2-4 concrete bullets the candidate can use when answering, tied to their real experience.
- topics_to_study: 3-6 gaps or themes the candidate should review before the interview (skills from the JD they should brush up on, company/role context, etc.).
- notes: one short sentence on overall prep strategy (optional).
- Mix technical depth, behavioral, and role-fit questions appropriate to the seniority implied by the job.
- If match analysis shows gaps, include questions that probe those areas honestly — with talking points that acknowledge limits while showing learning ability.
- If a tailored resume is provided, stay consistent with what it claims.
- Prefer specific questions over generic ones (e.g. "Walk me through your RAG pipeline in CareerPilot AI" over "Tell me about yourself").
"""


def build_user_prompt(
    profile: ProfileRead,
    job: JobRead,
    match: JobMatchScore | None = None,
    tailored_resume: TailoredResumeContent | None = None,
) -> str:
    return (
        "Prepare interview questions for this job application.\n\n"
        f"=== CANDIDATE PROFILE ===\n"
        f"{format_profile(profile, empty_message='Profile is empty — use only what appears in the tailored resume if provided.')}\n\n"
        f"=== JOB ===\n{format_job(job)}\n\n"
        f"=== MATCH ANALYSIS ===\n{format_match(match)}\n\n"
        f"=== TAILORED RESUME ===\n{format_tailored_resume(tailored_resume)}"
    )
