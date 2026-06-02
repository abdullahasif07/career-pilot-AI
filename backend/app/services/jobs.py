from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import JobModel
from app.schemas.job import JobCreate, JobParsed, JobRead, JobUpdate


def _to_read(job: JobModel) -> JobRead:
    return JobRead(
        id=job.id,
        company=job.company,
        role=job.role,
        status=job.status,
        raw_description=job.raw_description,
        requirements=job.requirements or [],
        skills=job.skills or [],
        responsibilities=job.responsibilities or [],
        job_url=job.job_url,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def list_jobs(db: Session) -> list[JobRead]:
    stmt = select(JobModel).order_by(JobModel.updated_at.desc())
    jobs = db.scalars(stmt).all()
    return [_to_read(job) for job in jobs]


def get_job(db: Session, job_id: int) -> JobRead | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None
    return _to_read(job)


def create_job(db: Session, payload: JobCreate) -> JobRead:
    job = JobModel(
        company=payload.company.strip(),
        role=payload.role.strip(),
        status=payload.status.value,
        raw_description=payload.raw_description.strip(),
        requirements=payload.requirements,
        skills=payload.skills,
        responsibilities=payload.responsibilities,
        job_url=(payload.job_url or "").strip() or None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _to_read(job)


def update_job(db: Session, job_id: int, payload: JobUpdate) -> JobRead | None:
    job = db.get(JobModel, job_id)
    if job is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        data["status"] = data["status"].value

    for field, value in data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return _to_read(job)


def delete_job(db: Session, job_id: int) -> bool:
    job = db.get(JobModel, job_id)
    if job is None:
        return False
    db.delete(job)
    db.commit()
    return True


def parse_job_description(description: str) -> JobParsed:
    from app.agents.job_extractor import parse_job_description as extract

    return extract(description)
