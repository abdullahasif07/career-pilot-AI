from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agents.match_scorer import score_profile_against_job
from app.models.job import JobModel
from app.schemas.job import JobRead
from app.schemas.match import JobMatchRead, JobMatchResult
from app.services import jobs, knowledge_base


def _to_match_result(job: JobModel) -> JobMatchResult | None:
    if job.match_computed_at is None or job.match_overall_score is None:
        return None
    return JobMatchResult(
        job_id=job.id,
        overall_score=job.match_overall_score,
        strong=job.match_strong or [],
        missing=job.match_missing or [],
        summary=job.match_summary,
        computed_at=job.match_computed_at,
    )


def get_saved_job_match(db: Session, job_id: int) -> JobMatchRead | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    saved = _to_match_result(job)
    return JobMatchRead(computed=saved is not None, match=saved)


def compute_and_save_job_match(db: Session, job_id: int) -> JobMatchResult | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    profile = knowledge_base.get_profile(db)
    job_read = jobs.get_job(db, job_id)
    assert job_read is not None

    result = score_profile_against_job(profile, job_read)

    job.match_overall_score = result.overall_score
    job.match_strong = result.strong
    job.match_missing = result.missing
    job.match_summary = result.summary
    job.match_computed_at = datetime.now(UTC)
    db.commit()
    db.refresh(job)

    saved = _to_match_result(job)
    assert saved is not None
    return saved
