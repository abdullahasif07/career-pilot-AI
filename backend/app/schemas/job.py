from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"
    GHOSTED = "ghosted"


class JobParseRequest(BaseModel):
    description: str = Field(min_length=20, max_length=50000)


class JobParsed(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    requirements: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


class JobCreate(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    raw_description: str = Field(min_length=20)
    status: JobStatus = JobStatus.INTERESTED
    requirements: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    job_url: str | None = None


class JobUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    status: JobStatus | None = None
    raw_description: str | None = None
    requirements: list[str] | None = None
    skills: list[str] | None = None
    responsibilities: list[str] | None = None
    job_url: str | None = None


class JobRead(BaseModel):
    id: int
    company: str
    role: str
    status: JobStatus
    raw_description: str
    requirements: list[str]
    skills: list[str]
    responsibilities: list[str]
    job_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
