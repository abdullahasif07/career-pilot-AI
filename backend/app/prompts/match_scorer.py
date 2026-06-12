from app.prompts.formatters import format_job, format_profile
from app.schemas.job import JobRead
from app.schemas.profile import ProfileRead

SYSTEM = """You score how well a candidate's profile fits a job description.
Return JSON only with this exact shape:
{
  "overall_score": integer,
  "strong": [string],
  "missing": [string],
  "summary": string | null
}

Rules:
- overall_score: 0-100 integer reflecting fit for this specific role.
- strong: skills, experiences, or qualifications the candidate clearly has that match the job (short labels, e.g. "Python", "TDD", "Angular").
- missing: important requirements or skills from the job that the candidate lacks or cannot infer from their profile.
- summary: one concise sentence explaining the score (optional tone: direct, helpful).
- Base the score only on the candidate profile provided — do not assume unstated skills.
- If the profile is sparse, score lower and note gaps in missing.
- Compare against job requirements, skills, and responsibilities equally.
"""


def build_user_prompt(profile: ProfileRead, job: JobRead) -> str:
    return (
        "Score this candidate against the job.\n\n"
        f"=== CANDIDATE PROFILE ===\n"
        f"{format_profile(profile, empty_message='Profile is empty — no summary, education, or projects on file.')}\n\n"
        f"=== JOB ===\n{format_job(job)}"
    )
