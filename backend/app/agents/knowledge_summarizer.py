from app.agents.gemini_client import generate_text
from app.prompts import knowledge_summary as prompts
from app.schemas.profile import ProfileRead


def summarize_knowledge_base(
    profile: ProfileRead,
    resume_text: str | None = None,
    system_prompt: str | None = None,
) -> str:
    effective_prompt = (
        system_prompt.strip()
        if system_prompt and system_prompt.strip()
        else prompts.SYSTEM
    )
    text = generate_text(
        effective_prompt,
        prompts.build_user_prompt(profile, resume_text),
    )
    summary = text.strip()
    if not summary:
        msg = "Model returned an empty knowledge base summary."
        raise ValueError(msg)
    return summary
