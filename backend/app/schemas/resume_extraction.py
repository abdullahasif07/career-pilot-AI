from pydantic import BaseModel, Field

from app.schemas.project import ProjectInput


class ResumeExtraction(BaseModel):
    """Structured profile data parsed from a resume — not persisted until user saves."""

    name: str | None = None
    location: str | None = None
    education: str | None = None
    summary: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    projects: list[ProjectInput] = Field(default_factory=list)
