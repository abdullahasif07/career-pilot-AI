# CareerPilot AI

An AI-powered career copilot that turns your personal knowledge base into tailored applications, outreach, and interview prep — all from a single command.

Instead of generic ChatGPT output, CareerPilot AI knows your background, writing style, and goals. It reads your master resume, job descriptions, and stored context to produce documents and messages that sound like you and match what each role actually needs.

---

## Core Concept: Personal Knowledge Base

The knowledge base is the heart of the system. Everything the agent generates pulls from structured, persistent data about you — not one-off prompts.

### Profile

| Field | Description |
|-------|-------------|
| Name | Full name |
| Location | Current or preferred location |
| Education | Degrees, institutions, relevant coursework |
| LinkedIn | Profile URL |
| Portfolio | Personal site or portfolio link |
| GitHub | GitHub profile URL |

### Work Experience

| Field | Description |
|-------|-------------|
| Company | Employer name |
| Role | Job title |
| Duration | Start and end dates |
| Projects | Key projects at this role |
| Achievements | Quantifiable wins and impact |
| Technologies | Stack and tools used |

### Projects

| Field | Description |
|-------|-------------|
| Project | Name and brief description |
| Tech stack | Languages, frameworks, infra |
| Problem | What problem it solved |
| Impact | Outcomes and metrics |
| Challenges | Hard problems you tackled |

### Career Goals

| Field | Description |
|-------|-------------|
| Interested roles | Target job titles |
| Preferred industries | Sectors you want to work in |
| Locations | Geographic preferences |
| Salary expectations | Target compensation range |

### Writing Style

Store examples of your previous writing so the agent maintains your voice:

- Previous cover letters
- Previous recruiter messages
- Previous statements of purpose (SOPs)

---

## Main Use Cases

### 1. Save Job Description

**Trigger:** *"Save this job."*

The agent extracts structured data from a job posting and stores it in Notion or a local database.

**Example output:**

```
Company:  Sierra AI
Role:     AI Engineer
Status:   Interested
```

Also extracted: requirements, required skills, and key responsibilities.

---

### 2. Match Score

**Trigger:** *"How good of a fit am I?"*

Compares your skills and experience against the job requirements.

**Example output:**

```
Overall Match: 87%

Strong:
  ✓ Python
  ✓ LLMs
  ✓ RAG

Missing:
  ✗ Kubernetes
  ✗ AWS
```

---

### 3. Tailor Resume

**Trigger:** *"Tailor my resume for Sierra AI."*

The killer feature. The agent reads your master resume, knowledge base, and the job description — then reorders and rewrites bullets to emphasize what matters for that role.

**Before:**

> Built MERN auction app

**After (when AI experience is important):**

> Built AI-powered auction platform utilizing real-time event processing...

---

### 4. Generate Cover Letter

**Trigger:** *"Write a cover letter for Sierra AI."*

Uses company info, the job description, and your personal knowledge base. Avoids generic GPT fluff by grounding every claim in your actual experience.

**Example:**

> I was particularly interested in your focus on AI-native systems...

Because the agent knows your background, not just the job posting.

---

### 5. LinkedIn Outreach

**Trigger:** *"Find recruiter and draft message."*

The agent finds the relevant recruiter or hiring manager and generates a personalized connection or follow-up note.

**Example:**

> Hi Sarah,
>
> I recently applied for the AI Engineer role at Sierra AI and wanted to reach out directly...

---

### 6. Email Outreach

**Trigger:** *"Draft recruiter email."*

Generates a complete email based on your application status:

- Subject line
- Body copy
- Clear call to action (CTA)

---

### 7. Application Tracker

Track every application through its lifecycle:

| Status | Description |
|--------|-------------|
| Applied | Application submitted |
| Interview | In interview process |
| Rejected | Not moving forward |
| Offer | Received an offer |
| Ghosted | No response after follow-up |

**Trigger:** *"Show applications needing follow-up."*

Surfaces stale applications and suggests next steps.

---

### 8. Interview Preparation

**Trigger:** *"Prepare me for Sierra AI interview."*

The agent reads the job description and your tailored resume, then generates likely interview questions tailored to the role and your background.

**Example questions:**

- Explain your RAG architecture.
- Why did you choose LangGraph over alternatives?
- Walk me through a production LLM deployment you've shipped.

---

### 9. Application Package Generator

**Trigger:** *"Apply to Sierra AI."*

One command produces the full application package:

| Output | Description |
|--------|-------------|
| `Resume.pdf` | Tailored resume |
| `CoverLetter.pdf` | Role-specific cover letter |
| LinkedIn message | Recruiter or hiring manager outreach |
| Recruiter email | Subject, body, and CTA |
| Interview questions | Prep list for likely topics |

This is where the magic happens.

---

## MCP Servers

CareerPilot AI integrates with external services via MCP (Model Context Protocol) servers:

| Server | Purpose |
|--------|---------|
| **Notion MCP** | Store job descriptions, application status, and notes |
| **Google Drive MCP** | Store resumes, cover letters, and generated documents |
| **Gmail MCP** | Send recruiter emails directly from your inbox |
| **GitHub MCP** | Read project repos directly — no manual project descriptions needed |
| **Filesystem MCP** | Read and write local documents (master resume, templates, exports) |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CareerPilot AI                      │
│                                                         │
│  ┌──────────────┐    ┌─────────────────────────────┐  │
│  │  Knowledge   │    │         Agent Layer          │  │
│  │    Base      │◄──►│  Match · Tailor · Generate   │  │
│  │  (Profile,   │    │  Track · Prep · Package      │  │
│  │   Resume,    │    └──────────────┬──────────────┘  │
│  │   Writing)   │                   │                  │
│  └──────────────┘                   │                  │
└─────────────────────────────────────┼──────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────┐
          │                           │                       │
    ┌─────▼─────┐              ┌──────▼──────┐         ┌──────▼──────┐
    │  Notion   │              │ Google Drive │         │   GitHub    │
    │  (Jobs,   │              │  (Resumes,   │         │  (Projects) │
    │  Tracker) │              │  Documents)  │         └─────────────┘
    └───────────┘              └─────────────┘
                                      │
                               ┌──────▼──────┐
                               │    Gmail    │
                               │  (Outreach) │
                               └─────────────┘
```

---

## Getting Started

> **Status:** Early development — setup instructions will be added as the project is built out.

### Prerequisites

- [Cursor](https://cursor.com) with MCP server support
- API keys / OAuth for: Notion, Google Drive, Gmail, GitHub (as needed)
- A master resume (`.pdf` or `.docx`) stored locally or in Google Drive

### Setup (local development)

```bash
make install              # backend/.venv + npm deps
cp .env.example .env      # add GEMINI_API_KEY for resume extraction
make dev                  # FastAPI :8000 + Vite :5173
```

All config lives in the **project root** `.env` (backend + frontend read from there).

Backend uses an isolated virtualenv at `backend/.venv`. See `make help` for all commands.

### Planned Setup Steps

1. Clone this repository
2. Run `make install` and `make dev`
3. Configure MCP servers (Notion, Google Drive, Gmail, GitHub, Filesystem)
4. Populate your personal knowledge base (profile, experience, projects, writing samples)
5. Add your master resume
6. Start with: *"Save this job"* → *"How good of a fit am I?"* → *"Apply to [Company]"*

---

## Roadmap

- [ ] Personal knowledge base schema and storage
- [ ] Job description parser and saver
- [ ] Skills match scoring engine
- [ ] Resume tailoring pipeline
- [ ] Cover letter generator with writing style matching
- [ ] LinkedIn and email outreach drafts
- [ ] Application tracker with follow-up reminders
- [ ] Interview prep question generator
- [ ] One-command application package export
- [ ] MCP server integrations (Notion, Google Drive, Gmail, GitHub, Filesystem)

---

## License

TBD
