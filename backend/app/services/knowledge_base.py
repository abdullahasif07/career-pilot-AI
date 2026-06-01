from sqlalchemy.orm import Session

from app.models.profile import PROFILE_ID, ProfileModel
from app.schemas.profile import ProfileRead, ProfileUpdate


def get_or_create_profile(db: Session) -> ProfileModel:
    profile = db.get(ProfileModel, PROFILE_ID)
    if profile is None:
        profile = ProfileModel(id=PROFILE_ID)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_profile(db: Session) -> ProfileRead:
    profile = get_or_create_profile(db)
    return ProfileRead.model_validate(profile)


def update_profile(db: Session, payload: ProfileUpdate) -> ProfileRead:
    profile = get_or_create_profile(db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return ProfileRead.model_validate(profile)
