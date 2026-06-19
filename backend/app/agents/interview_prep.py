import json

from app.agents.gemini_client import generate_json, generate_text
from app.agents.interview_prep_parser import parse_interview_prep_content
from app.prompts import interview_prep as prompts
from app.schemas.interview_prep import InterviewPrepContent
from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead
from app.schemas.tailored_resume import TailoredResumeContent


def generate_interview_prep_for_job(
    profile: ProfileRead,
    job: JobRead,
    match: JobMatchScore | None = None,
    tailored_resume: TailoredResumeContent | None = None,
) -> InterviewPrepContent:
    user_prompt = prompts.build_user_prompt(profile, job, match, tailored_resume)

    try:
        data = generate_json(prompts.SYSTEM, user_prompt)
        return parse_interview_prep_content(data)
    except (ValueError, json.JSONDecodeError):
        pass

    text = generate_text(prompts.SYSTEM, user_prompt)
    return parse_interview_prep_content(text)
