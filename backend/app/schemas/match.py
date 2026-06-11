from datetime import datetime

from pydantic import BaseModel, Field


class JobMatchScore(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    strong: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    summary: str | None = None


class JobMatchResult(JobMatchScore):
    job_id: int
    computed_at: datetime


class JobMatchRead(BaseModel):
    computed: bool
    match: JobMatchResult | None = None
