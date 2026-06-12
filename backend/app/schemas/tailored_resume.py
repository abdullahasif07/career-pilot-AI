from datetime import datetime

from pydantic import BaseModel, Field


class TailoredResumeItem(BaseModel):
    title: str | None = None
    bullets: list[str] = Field(default_factory=list)


class TailoredResumeSection(BaseModel):
    heading: str
    items: list[TailoredResumeItem] = Field(default_factory=list)


class TailoredResumeContent(BaseModel):
    summary: str | None = None
    sections: list[TailoredResumeSection] = Field(default_factory=list)
    notes: str | None = None


class JobTailoredResumeResult(TailoredResumeContent):
    job_id: int
    generated_at: datetime


class JobTailoredResumeRead(BaseModel):
    computed: bool
    resume: JobTailoredResumeResult | None = None
