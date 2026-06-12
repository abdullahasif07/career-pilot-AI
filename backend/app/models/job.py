import enum
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base


class JobStatus(str, enum.Enum):
    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"
    GHOSTED = "ghosted"


class JobModel(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(32),
        default=JobStatus.INTERESTED.value,
    )
    raw_description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    responsibilities: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    job_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    match_overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    match_strong: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    match_missing: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    match_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_computed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    tailored_resume: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tailored_resume_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
