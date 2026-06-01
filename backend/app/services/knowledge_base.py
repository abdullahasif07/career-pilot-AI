from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.resume_extractor import extract_profile_from_text
from app.core.config import settings
from app.models.profile import PROFILE_ID, ProfileModel
from app.models.project import ProjectModel
from app.schemas.profile import ProfileRead, ProfileUpdate, ResumeMeta
from app.schemas.project import ProjectInput
from app.schemas.resume_extraction import ResumeExtraction
from app.services.pdf_parser import extract_text_from_pdf

RESUME_STORAGE_NAME = "master_resume.pdf"
ALLOWED_RESUME_TYPES = {"application/pdf"}


def get_or_create_profile(db: Session) -> ProfileModel:
    profile = db.get(ProfileModel, PROFILE_ID)
    if profile is None:
        profile = ProfileModel(id=PROFILE_ID)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _resume_path() -> Path:
    return settings.upload_dir / RESUME_STORAGE_NAME


def _build_resume_meta(profile: ProfileModel) -> ResumeMeta | None:
    if not profile.resume_filename:
        return None
    path = _resume_path()
    size_bytes = path.stat().st_size if path.exists() else None
    return ResumeMeta(
        filename=profile.resume_filename,
        uploaded_at=profile.resume_uploaded_at or datetime.now(UTC),
        size_bytes=size_bytes,
    )


def _profile_to_read(profile: ProfileModel) -> ProfileRead:
    return ProfileRead(
        id=profile.id,
        name=profile.name,
        location=profile.location,
        education=profile.education,
        summary=profile.summary,
        linkedin_url=profile.linkedin_url,
        portfolio_url=profile.portfolio_url,
        github_url=profile.github_url,
        projects=profile.projects,
        resume=_build_resume_meta(profile),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def get_profile(db: Session) -> ProfileRead:
    profile = get_or_create_profile(db)
    db.refresh(profile, attribute_names=["projects"])
    return _profile_to_read(profile)


def _sync_projects(db: Session, profile: ProfileModel, projects: list[ProjectInput]) -> None:
    profile.projects.clear()
    for index, item in enumerate(projects):
        title = item.title.strip()
        if not title:
            continue
        profile.projects.append(
            ProjectModel(
                profile_id=PROFILE_ID,
                title=title,
                summary=(item.summary or "").strip() or None,
                sort_order=index,
            )
        )


def update_profile(db: Session, payload: ProfileUpdate) -> ProfileRead:
    profile = get_or_create_profile(db)
    data = payload.model_dump(exclude_unset=True)
    data.pop("projects", None)
    projects_payload = payload.projects

    for field, value in data.items():
        setattr(profile, field, value)

    if projects_payload is not None:
        _sync_projects(db, profile, projects_payload)

    db.commit()
    db.refresh(profile)
    db.refresh(profile, attribute_names=["projects"])
    return _profile_to_read(profile)


async def upload_resume(db: Session, file: UploadFile) -> ProfileRead:
    if file.content_type not in ALLOWED_RESUME_TYPES:
        msg = "Only PDF files are supported."
        raise ValueError(msg)

    content = await file.read()
    max_bytes = settings.max_resume_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        msg = f"Resume must be under {settings.max_resume_size_mb} MB."
        raise ValueError(msg)

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    _resume_path().write_bytes(content)

    profile = get_or_create_profile(db)
    profile.resume_filename = file.filename or RESUME_STORAGE_NAME
    profile.resume_uploaded_at = datetime.now(UTC)
    db.commit()
    db.refresh(profile)
    db.refresh(profile, attribute_names=["projects"])
    return _profile_to_read(profile)


def delete_resume(db: Session) -> ProfileRead:
    path = _resume_path()
    if path.exists():
        path.unlink()

    profile = get_or_create_profile(db)
    profile.resume_filename = None
    profile.resume_uploaded_at = None
    db.commit()
    db.refresh(profile)
    db.refresh(profile, attribute_names=["projects"])
    return _profile_to_read(profile)


def extract_resume(db: Session) -> ResumeExtraction:
    profile = get_or_create_profile(db)
    if not profile.resume_filename:
        msg = "Upload a resume PDF before running AI extraction."
        raise ValueError(msg)

    path = _resume_path()
    resume_text = extract_text_from_pdf(path)
    return extract_profile_from_text(resume_text)


def list_projects(db: Session) -> list[ProjectModel]:
    profile = get_or_create_profile(db)
    stmt = (
        select(ProjectModel)
        .where(ProjectModel.profile_id == profile.id)
        .order_by(ProjectModel.sort_order)
    )
    return list(db.scalars(stmt).all())
