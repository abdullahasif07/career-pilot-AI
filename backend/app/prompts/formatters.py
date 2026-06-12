from app.schemas.job import JobRead
from app.schemas.match import JobMatchScore
from app.schemas.profile import ProfileRead


def format_profile(profile: ProfileRead, *, empty_message: str) -> str:
    sections: list[str] = []

    if profile.name:
        sections.append(f"Name: {profile.name}")
    if profile.summary:
        sections.append(f"Summary: {profile.summary}")
    if profile.education:
        sections.append(f"Education: {profile.education}")
    if profile.location:
        sections.append(f"Location: {profile.location}")

    if profile.projects:
        project_lines = [
            f"- {p.title}: {p.summary or 'No summary'}" for p in profile.projects
        ]
        sections.append("Projects:\n" + "\n".join(project_lines))

    if not sections:
        return empty_message

    return "\n\n".join(sections)


def format_job(job: JobRead) -> str:
    parts = [
        f"Company: {job.company}",
        f"Role: {job.role}",
    ]
    if job.requirements:
        parts.append("Requirements:\n" + "\n".join(f"- {r}" for r in job.requirements))
    if job.skills:
        parts.append("Skills:\n" + "\n".join(f"- {s}" for s in job.skills))
    if job.responsibilities:
        parts.append("Responsibilities:\n" + "\n".join(f"- {r}" for r in job.responsibilities))
    return "\n\n".join(parts)


def format_match(match: JobMatchScore | None) -> str:
    if match is None:
        return "No prior match analysis available."

    lines = [f"Overall fit score: {match.overall_score}/100"]
    if match.strong:
        lines.append("Strong matches:\n" + "\n".join(f"- {s}" for s in match.strong))
    if match.missing:
        lines.append("Gaps:\n" + "\n".join(f"- {m}" for m in match.missing))
    if match.summary:
        lines.append(f"Summary: {match.summary}")
    return "\n\n".join(lines)
