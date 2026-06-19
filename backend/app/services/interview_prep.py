from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.interview_prep import generate_interview_prep_for_job
from app.models.job import JobModel
from app.schemas.interview_prep import (
    InterviewPrepContent,
    JobInterviewPrepRead,
    JobInterviewPrepResult,
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


def _content_from_job(job: JobModel) -> InterviewPrepContent | None:
    if job.interview_prep_generated_at is None or job.interview_prep is None:
        return None
    return InterviewPrepContent.model_validate(job.interview_prep)


def _to_result(job: JobModel) -> JobInterviewPrepResult | None:
    content = _content_from_job(job)
    if content is None:
        return None
    return JobInterviewPrepResult(
        job_id=job.id,
        questions=content.questions,
        topics_to_study=content.topics_to_study,
        notes=content.notes,
        generated_at=job.interview_prep_generated_at,  # type: ignore[arg-type]
    )


def get_saved_job_interview_prep(db: Session, job_id: int) -> JobInterviewPrepRead | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    saved = _to_result(job)
    return JobInterviewPrepRead(computed=saved is not None, interview_prep=saved)


def compute_and_save_job_interview_prep(
    db: Session,
    job_id: int,
) -> JobInterviewPrepResult | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    profile = knowledge_base.get_profile(db)
    job_read = jobs.get_job(db, job_id)
    assert job_read is not None

    content = generate_interview_prep_for_job(
        profile,
        job_read,
        _match_from_job(job),
        _tailored_resume_from_job(job),
    )

    job.interview_prep = content.model_dump(mode="json")
    job.interview_prep_generated_at = datetime.now(UTC)
    db.commit()
    db.refresh(job)

    saved = _to_result(job)
    assert saved is not None
    return saved
