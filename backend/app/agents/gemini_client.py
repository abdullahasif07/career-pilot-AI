import json

from google import genai
from google.genai import types

from app.core.config import settings


def get_client() -> genai.Client:
    if not settings.gemini_api_key:
        msg = "GEMINI_API_KEY is not configured. Add it to the project root .env file."
        raise RuntimeError(msg)
    return genai.Client(api_key=settings.gemini_api_key)


def generate_json(system_prompt: str, user_prompt: str) -> dict:
    client = get_client()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=f"{system_prompt}\n\n{user_prompt}",
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    content = response.text
    if not content:
        msg = "Gemini returned an empty response."
        raise RuntimeError(msg)

    return json.loads(content)
