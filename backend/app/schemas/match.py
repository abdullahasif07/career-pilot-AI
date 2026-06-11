from pydantic import BaseModel, Field


class JobMatchResult(BaseModel):
    job_id: int
    overall_score: int = Field(ge=0, le=100)
    strong: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    summary: str | None = None
