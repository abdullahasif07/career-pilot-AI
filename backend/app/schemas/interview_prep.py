from datetime import datetime

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    question: str = Field(min_length=1)
    category: str | None = None
    why_likely: str | None = None
    talking_points: list[str] = Field(default_factory=list)


class InterviewPrepContent(BaseModel):
    questions: list[InterviewQuestion] = Field(min_length=1)
    topics_to_study: list[str] = Field(default_factory=list)
    notes: str | None = None


class JobInterviewPrepResult(InterviewPrepContent):
    job_id: int
    generated_at: datetime


class JobInterviewPrepRead(BaseModel):
    computed: bool
    interview_prep: JobInterviewPrepResult | None = None
