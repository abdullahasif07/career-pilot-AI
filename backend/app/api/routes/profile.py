from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.schemas.resume_extraction import ResumeExtraction
from app.services import knowledge_base

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileRead)
def read_profile(db: Session = Depends(get_db)) -> ProfileRead:
    return knowledge_base.get_profile(db)


@router.put("", response_model=ProfileRead)
def upsert_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
) -> ProfileRead:
    return knowledge_base.update_profile(db, payload)


@router.post("/resume", response_model=ProfileRead)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ProfileRead:
    try:
        return await knowledge_base.upload_resume(db, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/resume", response_model=ProfileRead)
def remove_resume(db: Session = Depends(get_db)) -> ProfileRead:
    return knowledge_base.delete_resume(db)


@router.post("/resume/extract", response_model=ResumeExtraction)
def extract_resume(db: Session = Depends(get_db)) -> ResumeExtraction:
    try:
        return knowledge_base.extract_resume(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
