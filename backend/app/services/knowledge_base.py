from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.resume_extractor import extract_profile_from_text
from app.agents.knowledge_summarizer import summarize_knowledge_base
from app.core.config import settings
from app.models.profile import PROFILE_ID, ProfileModel
from app.models.project import ProjectModel
from app.prompts import cover_letter as cover_letter_prompts
from app.prompts import knowledge_summary as knowledge_summary_prompts
from app.schemas.cover_letter import CoverLetterPromptConfig, CoverLetterPromptUpdate
from app.schemas.knowledge_summary import (
    KnowledgeSummaryPromptConfig,
    KnowledgeSummaryPromptUpdate,
    KnowledgeSummaryRead,
    KnowledgeSummaryResult,
    KnowledgeSummaryUpdate,
)
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
        agent_knowledge_summary=profile.agent_knowledge_summary,
        agent_knowledge_summary_generated_at=profile.agent_knowledge_summary_generated_at,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def get_profile(db: Session) -> ProfileRead:
    profile = get_or_create_profile(db)
    db.refresh(profile, attribute_names=["projects"])
    return _profile_to_read(profile)


def get_cover_letter_prompt_config(db: Session) -> CoverLetterPromptConfig:
    profile = get_or_create_profile(db)
    custom = profile.cover_letter_system_prompt
    return CoverLetterPromptConfig(
        default_system_prompt=cover_letter_prompts.SYSTEM,
        custom_system_prompt=custom,
        uses_custom=bool(custom and custom.strip()),
    )


def update_cover_letter_prompt(
    db: Session,
    payload: CoverLetterPromptUpdate,
) -> CoverLetterPromptConfig:
    profile = get_or_create_profile(db)
    raw = payload.system_prompt
    profile.cover_letter_system_prompt = (
        raw.strip() if raw and raw.strip() else None
    )
    db.commit()
    db.refresh(profile)
    return get_cover_letter_prompt_config(db)


def get_knowledge_summary(db: Session) -> KnowledgeSummaryRead:
    profile = get_or_create_profile(db)
    summary = profile.agent_knowledge_summary
    return KnowledgeSummaryRead(
        summary=summary,
        generated_at=profile.agent_knowledge_summary_generated_at,
        has_summary=bool(summary and summary.strip()),
    )


def update_knowledge_summary(
    db: Session,
    payload: KnowledgeSummaryUpdate,
) -> KnowledgeSummaryRead:
    profile = get_or_create_profile(db)
    raw = payload.summary
    profile.agent_knowledge_summary = raw.strip() if raw and raw.strip() else None
    if profile.agent_knowledge_summary is None:
        profile.agent_knowledge_summary_generated_at = None
    db.commit()
    db.refresh(profile)
    return get_knowledge_summary(db)


def get_knowledge_summary_prompt_config(db: Session) -> KnowledgeSummaryPromptConfig:
    profile = get_or_create_profile(db)
    custom = profile.agent_knowledge_summary_prompt
    return KnowledgeSummaryPromptConfig(
        default_system_prompt=knowledge_summary_prompts.SYSTEM,
        custom_system_prompt=custom,
        uses_custom=bool(custom and custom.strip()),
    )


def update_knowledge_summary_prompt(
    db: Session,
    payload: KnowledgeSummaryPromptUpdate,
) -> KnowledgeSummaryPromptConfig:
    profile = get_or_create_profile(db)
    raw = payload.system_prompt
    profile.agent_knowledge_summary_prompt = (
        raw.strip() if raw and raw.strip() else None
    )
    db.commit()
    db.refresh(profile)
    return get_knowledge_summary_prompt_config(db)


def _optional_resume_text(db: Session) -> str | None:
    profile = get_or_create_profile(db)
    if not profile.resume_filename:
        return None
    path = _resume_path()
    if not path.exists():
        return None
    try:
        return extract_text_from_pdf(path)
    except ValueError:
        return None


def compute_knowledge_summary(db: Session) -> KnowledgeSummaryResult:
    profile = get_or_create_profile(db)
    db.refresh(profile, attribute_names=["projects"])
    profile_read = _profile_to_read(profile)

    if not profile_read.name and not profile_read.summary and not profile_read.projects:
        msg = "Add profile details or projects before generating a knowledge summary."
        raise ValueError(msg)

    resume_text = _optional_resume_text(db)
    summary = summarize_knowledge_base(
        profile_read,
        resume_text,
        system_prompt=profile.agent_knowledge_summary_prompt,
    )

    profile.agent_knowledge_summary = summary
    profile.agent_knowledge_summary_generated_at = datetime.now(UTC)
    db.commit()
    db.refresh(profile)

    assert profile.agent_knowledge_summary_generated_at is not None
    return KnowledgeSummaryResult(
        summary=summary,
        generated_at=profile.agent_knowledge_summary_generated_at,
    )


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

    if not content.startswith(b"%PDF-"):
        msg = "Only valid PDF files are supported."
        raise ValueError(msg)

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    path = _resume_path()
    path.write_bytes(content)

    try:
        extract_text_from_pdf(path)
    except ValueError:
        path.unlink(missing_ok=True)
        raise

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


def get_master_resume_text(db: Session) -> str:
    profile = get_or_create_profile(db)
    if not profile.resume_filename:
        msg = "Upload a master resume PDF before tailoring."
        raise ValueError(msg)

    return extract_text_from_pdf(_resume_path())


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
