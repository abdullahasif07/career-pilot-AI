from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.project import ProjectInput, ProjectRead


class ResumeMeta(BaseModel):
    filename: str
    uploaded_at: datetime
    size_bytes: int | None = None


class ProfileBase(BaseModel):
    name: str | None = None
    location: str | None = None
    education: str | None = None
    summary: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None


class ProfileUpdate(ProfileBase):
    projects: list[ProjectInput] | None = None


class ProfileRead(ProfileBase):
    id: int
    projects: list[ProjectRead]
    resume: ResumeMeta | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
