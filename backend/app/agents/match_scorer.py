from app.agents.gemini_client import generate_json
from app.prompts import match_scorer as prompts
from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead


def score_profile_against_job(profile: ProfileRead, job: JobRead) -> JobMatchScore:
    data = generate_json(
        prompts.SYSTEM,
        prompts.build_user_prompt(profile, job),
    )
    return JobMatchScore.model_validate(data)
