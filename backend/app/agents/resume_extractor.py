from app.agents.gemini_client import generate_json
from app.prompts import resume_extractor as prompts
from app.schemas.resume_extraction import ResumeExtraction


def extract_profile_from_text(resume_text: str) -> ResumeExtraction:
    data = generate_json(
        prompts.SYSTEM,
        prompts.build_user_prompt(resume_text),
    )
    return ResumeExtraction.model_validate(data)
