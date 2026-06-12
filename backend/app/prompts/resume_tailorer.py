from app.prompts.formatters import format_job, format_match, format_profile
from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead

SYSTEM = """You tailor a candidate's resume for a specific job description.
Return JSON only with this exact shape:
{
  "summary": string | null,
  "sections": [
    {
      "heading": string,
      "items": [
        {
          "title": string | null,
          "bullets": [string]
        }
      ]
    }
  ],
  "notes": string | null
}

Rules:
- Use ONLY facts from the master resume and candidate profile — never invent employers, titles, dates, or skills.
- Rewrite and reorder bullets to emphasize experience that matches the job requirements, skills, and responsibilities.
- Deprioritize or omit irrelevant bullets; do not fabricate replacements.
- summary: a concise professional summary tailored to this role (null if the source resume has no summary section).
- sections: logical resume sections (e.g. Experience, Projects, Education, Skills). Preserve real employers/project names.
- items.title: role, company, degree, or project name when applicable.
- bullets: achievement-focused bullet points, rewritten for this job where truthful.
- notes: one short sentence on what you emphasized or changed (optional).
- If match analysis is provided, lean into strong areas and address gaps only with honest framing — do not claim missing skills.
"""


def build_user_prompt(
    master_resume_text: str,
    profile: ProfileRead,
    job: JobRead,
    match: JobMatchScore | None = None,
) -> str:
    return (
        "Tailor this resume for the job.\n\n"
        f"=== MASTER RESUME ===\n{master_resume_text}\n\n"
        f"=== CANDIDATE PROFILE (supplement) ===\n"
        f"{format_profile(profile, empty_message='No additional profile details on file.')}\n\n"
        f"=== JOB ===\n{format_job(job)}\n\n"
        f"=== MATCH ANALYSIS ===\n{format_match(match)}"
    )
