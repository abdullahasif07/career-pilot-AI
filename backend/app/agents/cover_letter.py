from app.agents.gemini_client import generate_json
from app.prompts import cover_letter as prompts
from app.schemas.cover_letter import CoverLetterContent
from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead
from app.schemas.tailored_resume import TailoredResumeContent


def generate_cover_letter_for_job(
    profile: ProfileRead,
    job: JobRead,
    match: JobMatchScore | None = None,
    tailored_resume: TailoredResumeContent | None = None,
) -> CoverLetterContent:
    data = generate_json(
        prompts.SYSTEM,
        prompts.build_user_prompt(profile, job, match, tailored_resume),
    )
    return CoverLetterContent.model_validate(data)
