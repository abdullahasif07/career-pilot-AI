from datetime import datetime

from pydantic import BaseModel, Field


class CoverLetterContent(BaseModel):
    subject: str | None = None
    body: str = Field(min_length=1)
    notes: str | None = None


class JobCoverLetterResult(CoverLetterContent):
    job_id: int
    generated_at: datetime


class JobCoverLetterRead(BaseModel):
    computed: bool
    cover_letter: JobCoverLetterResult | None = None
