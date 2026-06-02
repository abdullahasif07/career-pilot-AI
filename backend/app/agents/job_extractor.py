from app.agents.gemini_client import generate_json
from app.schemas.job import JobParsed

SYSTEM_PROMPT = """You extract structured data from a job description (JD).
Return JSON only with this exact shape:
{
  "company": string,
  "role": string,
  "requirements": [string],
  "skills": [string],
  "responsibilities": [string]
}

Rules:
- company: employer name (required).
- role: job title (required).
- requirements: qualifications, must-haves, years of experience, education (bullet phrases).
- skills: technologies, tools, languages, frameworks mentioned.
- responsibilities: main duties and what the person will do (bullet phrases).
- Use concise bullet-style strings; 3-12 items per list when present.
- Do not invent details not supported by the job description text.
- If company name is unclear, infer from context or use "Unknown Company".
"""


def parse_job_description(description: str) -> JobParsed:
    data = generate_json(
        SYSTEM_PROMPT,
        f"Extract structured job data from this job description:\n\n{description[:15000]}",
    )
    return JobParsed.model_validate(data)
