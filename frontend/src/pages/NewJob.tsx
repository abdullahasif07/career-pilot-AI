import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError, createJob, parseJob } from "../api/client";
import FormField from "../components/FormField";
import TagList from "../components/TagList";
import type { JobParsed } from "../types/job";

type Step = "paste" | "review";

type ActionState =
  | { kind: "idle" }
  | { kind: "parsing" }
  | { kind: "saving" }
  | { kind: "error"; message: string };

export default function NewJob() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>("paste");
  const [description, setDescription] = useState("");
  const [jobUrl, setJobUrl] = useState("");
  const [parsed, setParsed] = useState<JobParsed | null>(null);
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [requirements, setRequirements] = useState<string[]>([]);
  const [skills, setSkills] = useState<string[]>([]);
  const [responsibilities, setResponsibilities] = useState<string[]>([]);
  const [action, setAction] = useState<ActionState>({ kind: "idle" });

  async function handleParse(event: FormEvent) {
    event.preventDefault();
    if (description.trim().length < 20) {
      setAction({ kind: "error", message: "Paste at least 20 characters of job description." });
      return;
    }

    setAction({ kind: "parsing" });
    try {
      const result = await parseJob(description.trim());
      setParsed(result);
      setCompany(result.company);
      setRole(result.role);
      setRequirements(result.requirements);
      setSkills(result.skills);
      setResponsibilities(result.responsibilities);
      setStep("review");
      setAction({ kind: "idle" });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not parse job. Check GEMINI_API_KEY in .env.";
      setAction({ kind: "error", message });
    }
  }

  async function handleSave(event: FormEvent) {
    event.preventDefault();
    setAction({ kind: "saving" });
    try {
      const job = await createJob({
        company: company.trim(),
        role: role.trim(),
        raw_description: description.trim(),
        requirements,
        skills,
        responsibilities,
        job_url: jobUrl.trim() || null,
        status: "interested",
      });
      navigate(`/jobs/${job.id}`);
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Could not save job.";
      setAction({ kind: "error", message });
    }
  }

  function handleBack() {
    setStep("paste");
    setParsed(null);
    setAction({ kind: "idle" });
  }

  const busy = action.kind === "parsing" || action.kind === "saving";

  return (
    <main className="page page--wide">
      <header className="page__header">
        <div>
          <p className="page__eyebrow">Jobs</p>
          <h1>{step === "paste" ? "Save a job" : "Review & save"}</h1>
          <p className="page__subtitle">
            {step === "paste"
              ? "Paste the full job description. AI will extract company, role, and skills."
              : "Review AI-extracted fields, edit anything, then save to your tracker."}
          </p>
        </div>
        <Link to="/jobs" className="btn btn--ghost">
          ← Back to jobs
        </Link>
      </header>

      {step === "paste" && (
        <form className="profile-form" onSubmit={handleParse}>
          <section className="card">
            <FormField
              id="job-url"
              label="Job URL (optional)"
              type="url"
              value={jobUrl}
              onChange={setJobUrl}
              placeholder="https://company.com/careers/ai-engineer"
            />
            <FormField
              id="job-description"
              label="Job description"
              type="textarea"
              hint="Paste the full posting — requirements, responsibilities, and skills"
              value={description}
              onChange={setDescription}
              placeholder="Senior AI Engineer at Sierra AI&#10;&#10;We are looking for..."
              rows={14}
            />
          </section>

          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={busy}>
              {action.kind === "parsing" ? "Parsing with AI…" : "Parse with AI"}
            </button>
          </div>
        </form>
      )}

      {step === "review" && parsed && (
        <form className="profile-form" onSubmit={handleSave}>
          <div className="alert alert--info" role="status">
            AI extracted the fields below from your job description. Edit anything
            before saving.
          </div>

          <section className="card">
            <div className="form-grid">
              <FormField
                id="company"
                label="Company"
                value={company}
                onChange={setCompany}
              />
              <FormField
                id="role"
                label="Role"
                value={role}
                onChange={setRole}
              />
            </div>
          </section>

          <section className="card">
            <TagList title="Requirements" items={requirements} />
            <TagList title="Skills" items={skills} />
            <TagList title="Responsibilities" items={responsibilities} />
          </section>

          <section className="card card--muted">
            <h2 className="card__title">Original description</h2>
            <p className="jd-preview">{description}</p>
          </section>

          <div className="form-actions">
            <button type="button" className="btn btn--ghost" onClick={handleBack} disabled={busy}>
              ← Edit description
            </button>
            <button type="submit" className="btn btn--primary" disabled={busy}>
              {action.kind === "saving" ? "Saving…" : "Save job"}
            </button>
          </div>
        </form>
      )}

      {action.kind === "error" && (
        <p className="form-actions__feedback form-actions__feedback--error" role="alert">
          {action.message}
        </p>
      )}
    </main>
  );
}
