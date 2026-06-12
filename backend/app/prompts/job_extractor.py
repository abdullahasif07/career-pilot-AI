SYSTEM = """You extract structured data from a job description (JD).
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


def build_user_prompt(description: str) -> str:
    return f"Extract structured job data from this job description:\n\n{description[:15000]}"
