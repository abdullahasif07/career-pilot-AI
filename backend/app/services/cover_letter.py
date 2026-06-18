from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.cover_letter import generate_cover_letter_for_job
from app.models.job import JobModel
from app.schemas.cover_letter import (
    CoverLetterContent,
    JobCoverLetterRead,
    JobCoverLetterResult,
)
from app.schemas.match import JobMatchScore
from app.schemas.tailored_resume import TailoredResumeContent
from app.services import jobs, knowledge_base


def _match_from_job(job: JobModel) -> JobMatchScore | None:
    if job.match_computed_at is None or job.match_overall_score is None:
        return None
    return JobMatchScore(
        overall_score=job.match_overall_score,
        strong=job.match_strong or [],
        missing=job.match_missing or [],
        summary=job.match_summary,
    )


def _tailored_resume_from_job(job: JobModel) -> TailoredResumeContent | None:
    if job.tailored_resume_generated_at is None or job.tailored_resume is None:
        return None
    return TailoredResumeContent.model_validate(job.tailored_resume)


def _content_from_job(job: JobModel) -> CoverLetterContent | None:
    if job.cover_letter_generated_at is None or job.cover_letter is None:
        return None
    return CoverLetterContent.model_validate(job.cover_letter)


def _to_result(job: JobModel) -> JobCoverLetterResult | None:
    content = _content_from_job(job)
    if content is None:
        return None
    return JobCoverLetterResult(
        job_id=job.id,
        subject=content.subject,
        body=content.body,
        notes=content.notes,
        generated_at=job.cover_letter_generated_at,  # type: ignore[arg-type]
    )


def get_saved_job_cover_letter(db: Session, job_id: int) -> JobCoverLetterRead | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    saved = _to_result(job)
    return JobCoverLetterRead(computed=saved is not None, cover_letter=saved)


def compute_and_save_job_cover_letter(
    db: Session,
    job_id: int,
) -> JobCoverLetterResult | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    profile = knowledge_base.get_profile(db)
    job_read = jobs.get_job(db, job_id)
    assert job_read is not None

    match = _match_from_job(job)
    tailored_resume = _tailored_resume_from_job(job)

    profile_model = knowledge_base.get_or_create_profile(db)
    content = generate_cover_letter_for_job(
        profile,
        job_read,
        match,
        tailored_resume,
        system_prompt=profile_model.cover_letter_system_prompt,
    )

    job.cover_letter = content.model_dump(mode="json")
    job.cover_letter_generated_at = datetime.now(UTC)
    db.commit()
    db.refresh(job)

    saved = _to_result(job)
    assert saved is not None
    return saved
