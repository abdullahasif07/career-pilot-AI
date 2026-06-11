from app.agents.gemini_client import generate_json
from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead

SYSTEM_PROMPT = """You score how well a candidate's profile fits a job description.
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


def _format_profile(profile: ProfileRead) -> str:
    sections: list[str] = []

    if profile.name:
        sections.append(f"Name: {profile.name}")
    if profile.summary:
        sections.append(f"Summary: {profile.summary}")
    if profile.education:
        sections.append(f"Education: {profile.education}")
    if profile.location:
        sections.append(f"Location: {profile.location}")

    if profile.projects:
        project_lines = [
            f"- {p.title}: {p.summary or 'No summary'}" for p in profile.projects
        ]
        sections.append("Projects:\n" + "\n".join(project_lines))

    if not sections:
        return "Profile is empty — no summary, education, or projects on file."

    return "\n\n".join(sections)


def _format_job(job: JobRead) -> str:
    parts = [
        f"Company: {job.company}",
        f"Role: {job.role}",
    ]
    if job.requirements:
        parts.append("Requirements:\n" + "\n".join(f"- {r}" for r in job.requirements))
    if job.skills:
        parts.append("Skills:\n" + "\n".join(f"- {s}" for s in job.skills))
    if job.responsibilities:
        parts.append("Responsibilities:\n" + "\n".join(f"- {r}" for r in job.responsibilities))
    return "\n\n".join(parts)


def score_profile_against_job(profile: ProfileRead, job: JobRead) -> JobMatchScore:
    user_prompt = (
        "Score this candidate against the job.\n\n"
        f"=== CANDIDATE PROFILE ===\n{_format_profile(profile)}\n\n"
        f"=== JOB ===\n{_format_job(job)}"
    )

    data = generate_json(SYSTEM_PROMPT, user_prompt)
    return JobMatchScore.model_validate(data)
