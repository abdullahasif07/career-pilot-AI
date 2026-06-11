from sqlalchemy.orm import Session

from app.agents.match_scorer import score_profile_against_job
from app.schemas.match import JobMatchResult
from app.services import jobs, knowledge_base


def get_job_match(db: Session, job_id: int) -> JobMatchResult | None:
    job = jobs.get_job(db, job_id)
    if job is None:
        return None

    profile = knowledge_base.get_profile(db)
    return score_profile_against_job(profile, job)
