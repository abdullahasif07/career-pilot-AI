from app.schemas.profile import ProfileRead

SYSTEM = """You create a concise knowledge base summary for an AI career agent.
The summary will be used to tailor cover letters, resumes, and job applications.

Return plain text only (no JSON, no markdown code fences).

Include when available:
- Who the candidate is and their core expertise
- Key skills, technologies, and strengths
- Notable projects with brief impact
- Education and location
- Types of roles they are well suited for

Rules:
- Use only facts from the source material provided — never invent experience
- Write in a clear, scannable style: short paragraphs and bullet points
- Third person or neutral tone (e.g. "The candidate has…")
- Target roughly 150–400 words
- Omit sections with no source data
"""


def _format_source_profile(profile: ProfileRead) -> str:
    sections: list[str] = []

    if profile.name:
        sections.append(f"Name: {profile.name}")
    if profile.summary:
        sections.append(f"Profile summary: {profile.summary}")
    if profile.education:
        sections.append(f"Education: {profile.education}")
    if profile.location:
        sections.append(f"Location: {profile.location}")

    links: list[str] = []
    if profile.linkedin_url:
        links.append(f"LinkedIn: {profile.linkedin_url}")
    if profile.portfolio_url:
        links.append(f"Portfolio: {profile.portfolio_url}")
    if profile.github_url:
        links.append(f"GitHub: {profile.github_url}")
    if links:
        sections.append("\n".join(links))

    if profile.projects:
        project_lines = [
            f"- {p.title}: {p.summary or 'No summary'}" for p in profile.projects
        ]
        sections.append("Projects:\n" + "\n".join(project_lines))

    if not sections:
        return "No structured profile data on file."

    return "\n\n".join(sections)


def build_user_prompt(profile: ProfileRead, resume_text: str | None = None) -> str:
    parts = [
        "Create an agent-ready knowledge base summary from this source material.\n",
        f"=== PROFILE ===\n{_format_source_profile(profile)}",
    ]
    if resume_text:
        parts.append(f"=== MASTER RESUME ===\n{resume_text[:12000]}")
    else:
        parts.append("=== MASTER RESUME ===\nNot uploaded.")
    return "\n\n".join(parts)
