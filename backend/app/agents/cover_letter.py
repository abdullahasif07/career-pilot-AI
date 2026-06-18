import json

from app.agents.cover_letter_parser import parse_cover_letter_content
from app.agents.gemini_client import generate_json, generate_text
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
    system_prompt: str | None = None,
) -> CoverLetterContent:
    effective_prompt = (
        system_prompt.strip()
        if system_prompt and system_prompt.strip()
        else prompts.SYSTEM
    )
    user_prompt = prompts.build_user_prompt(profile, job, match, tailored_resume)

    try:
        data = generate_json(effective_prompt, user_prompt)
        return parse_cover_letter_content(data)
    except (ValueError, json.JSONDecodeError):
        pass

    text = generate_text(effective_prompt, user_prompt)
    return parse_cover_letter_content(text)
