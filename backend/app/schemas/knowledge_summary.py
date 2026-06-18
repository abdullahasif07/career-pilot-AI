from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeSummaryRead(BaseModel):
    summary: str | None = None
    generated_at: datetime | None = None
    has_summary: bool


class KnowledgeSummaryUpdate(BaseModel):
    summary: str | None = None


class KnowledgeSummaryPromptConfig(BaseModel):
    default_system_prompt: str
    custom_system_prompt: str | None = None
    uses_custom: bool


class KnowledgeSummaryPromptUpdate(BaseModel):
    system_prompt: str | None = None


class KnowledgeSummaryResult(BaseModel):
    summary: str = Field(min_length=1)
    generated_at: datetime
