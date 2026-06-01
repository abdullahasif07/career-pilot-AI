from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    name: str | None = None
    location: str | None = None
    education: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
