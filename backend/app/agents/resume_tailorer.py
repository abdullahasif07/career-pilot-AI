from app.agents.gemini_client import generate_json
from app.prompts import resume_tailorer as prompts
from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead
from app.schemas.tailored_resume import TailoredResumeContent


def tailor_resume_for_job(
    master_resume_text: str,
    profile: ProfileRead,
    job: JobRead,
    match: JobMatchScore | None = None,
) -> TailoredResumeContent:
    data = generate_json(
        prompts.SYSTEM,
        prompts.build_user_prompt(master_resume_text, profile, job, match),
    )
    return TailoredResumeContent.model_validate(data)
