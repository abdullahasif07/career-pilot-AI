from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.resume_tailorer import tailor_resume_for_job
from app.models.job import JobModel
from app.schemas.match import JobMatchScore
from app.schemas.tailored_resume import (
    JobTailoredResumeRead,
    JobTailoredResumeResult,
    TailoredResumeContent,
)
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


def _content_from_job(job: JobModel) -> TailoredResumeContent | None:
    if job.tailored_resume_generated_at is None or job.tailored_resume is None:
        return None
    return TailoredResumeContent.model_validate(job.tailored_resume)


def _to_result(job: JobModel) -> JobTailoredResumeResult | None:
    content = _content_from_job(job)
    if content is None:
        return None
    return JobTailoredResumeResult(
        job_id=job.id,
        summary=content.summary,
        sections=content.sections,
        notes=content.notes,
        generated_at=job.tailored_resume_generated_at,  # type: ignore[arg-type]
    )


def get_saved_job_tailored_resume(db: Session, job_id: int) -> JobTailoredResumeRead | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    saved = _to_result(job)
    return JobTailoredResumeRead(computed=saved is not None, resume=saved)


def compute_and_save_job_tailored_resume(
    db: Session,
    job_id: int,
) -> JobTailoredResumeResult | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    profile = knowledge_base.get_profile(db)
    job_read = jobs.get_job(db, job_id)
    assert job_read is not None

    master_resume_text = knowledge_base.get_master_resume_text(db)
    match = _match_from_job(job)

    content = tailor_resume_for_job(master_resume_text, profile, job_read, match)

    job.tailored_resume = content.model_dump(mode="json")
    job.tailored_resume_generated_at = datetime.now(UTC)
    db.commit()
    db.refresh(job)

    saved = _to_result(job)
    assert saved is not None
    return saved
