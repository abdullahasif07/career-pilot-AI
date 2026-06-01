from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.profile import ProfileRead, ProfileUpdate
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
