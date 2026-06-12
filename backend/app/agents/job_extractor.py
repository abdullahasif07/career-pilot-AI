from app.agents.gemini_client import generate_json
from app.prompts import job_extractor as prompts
from app.schemas.job import JobParsed


def parse_job_description(description: str) -> JobParsed:
    data = generate_json(
        prompts.SYSTEM,
        prompts.build_user_prompt(description),
    )
    return JobParsed.model_validate(data)
