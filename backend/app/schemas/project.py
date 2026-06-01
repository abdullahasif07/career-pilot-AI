from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = None


class ProjectInput(ProjectBase):
    id: int | None = None


class ProjectRead(ProjectBase):
    id: int
    sort_order: int

    model_config = ConfigDict(from_attributes=True)
