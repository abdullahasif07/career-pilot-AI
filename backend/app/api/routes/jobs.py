from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.job import JobCreate, JobParseRequest, JobParsed, JobRead, JobUpdate
from app.schemas.match import JobMatchRead, JobMatchResult
from app.schemas.tailored_resume import JobTailoredResumeRead, JobTailoredResumeResult
from app.services import jobs, match, resume_tailor

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[JobRead]:
    return jobs.list_jobs(db)


@router.post("/parse", response_model=JobParsed)
def parse_job(payload: JobParseRequest) -> JobParsed:
    try:
        return jobs.parse_job_description(payload.description)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> JobRead:
    return jobs.create_job(db, payload)


@router.get("/{job_id}/match", response_model=JobMatchRead)
def read_job_match(job_id: int, db: Session = Depends(get_db)) -> JobMatchRead:
    result = match.get_saved_job_match(db, job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.post("/{job_id}/match/compute", response_model=JobMatchResult)
def compute_job_match(job_id: int, db: Session = Depends(get_db)) -> JobMatchResult:
    try:
        result = match.compute_and_save_job_match(db, job_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.get("/{job_id}/resume/tailor", response_model=JobTailoredResumeRead)
def read_job_tailored_resume(
    job_id: int,
    db: Session = Depends(get_db),
) -> JobTailoredResumeRead:
    result = resume_tailor.get_saved_job_tailored_resume(db, job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.post("/{job_id}/resume/tailor/compute", response_model=JobTailoredResumeResult)
def compute_job_tailored_resume(
    job_id: int,
    db: Session = Depends(get_db),
) -> JobTailoredResumeResult:
    try:
        result = resume_tailor.compute_and_save_job_tailored_resume(db, job_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.get("/{job_id}", response_model=JobRead)
def read_job(job_id: int, db: Session = Depends(get_db)) -> JobRead:
    job = jobs.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    payload: JobUpdate,
    db: Session = Depends(get_db),
) -> JobRead:
    job = jobs.update_job(db, job_id, payload)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)) -> None:
    deleted = jobs.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
