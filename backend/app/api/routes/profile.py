from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.schemas.resume_extraction import ResumeExtraction
from app.schemas.cover_letter import CoverLetterPromptConfig, CoverLetterPromptUpdate
from app.schemas.knowledge_summary import (
    KnowledgeSummaryPromptConfig,
    KnowledgeSummaryPromptUpdate,
    KnowledgeSummaryRead,
    KnowledgeSummaryResult,
    KnowledgeSummaryUpdate,
)
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


@router.get("/cover-letter/prompt", response_model=CoverLetterPromptConfig)
def read_cover_letter_prompt(db: Session = Depends(get_db)) -> CoverLetterPromptConfig:
    return knowledge_base.get_cover_letter_prompt_config(db)


@router.put("/cover-letter/prompt", response_model=CoverLetterPromptConfig)
def update_cover_letter_prompt(
    payload: CoverLetterPromptUpdate,
    db: Session = Depends(get_db),
) -> CoverLetterPromptConfig:
    return knowledge_base.update_cover_letter_prompt(db, payload)


@router.get("/knowledge-summary", response_model=KnowledgeSummaryRead)
def read_knowledge_summary(db: Session = Depends(get_db)) -> KnowledgeSummaryRead:
    return knowledge_base.get_knowledge_summary(db)


@router.put("/knowledge-summary", response_model=KnowledgeSummaryRead)
def update_knowledge_summary(
    payload: KnowledgeSummaryUpdate,
    db: Session = Depends(get_db),
) -> KnowledgeSummaryRead:
    return knowledge_base.update_knowledge_summary(db, payload)


@router.post("/knowledge-summary/compute", response_model=KnowledgeSummaryResult)
def compute_knowledge_summary(db: Session = Depends(get_db)) -> KnowledgeSummaryResult:
    try:
        return knowledge_base.compute_knowledge_summary(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/knowledge-summary/prompt", response_model=KnowledgeSummaryPromptConfig)
def read_knowledge_summary_prompt(
    db: Session = Depends(get_db),
) -> KnowledgeSummaryPromptConfig:
    return knowledge_base.get_knowledge_summary_prompt_config(db)


@router.put("/knowledge-summary/prompt", response_model=KnowledgeSummaryPromptConfig)
def update_knowledge_summary_prompt(
    payload: KnowledgeSummaryPromptUpdate,
    db: Session = Depends(get_db),
) -> KnowledgeSummaryPromptConfig:
    return knowledge_base.update_knowledge_summary_prompt(db, payload)


@router.post("/resume/extract", response_model=ResumeExtraction)
def extract_resume(db: Session = Depends(get_db)) -> ResumeExtraction:
    try:
        return knowledge_base.extract_resume(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
