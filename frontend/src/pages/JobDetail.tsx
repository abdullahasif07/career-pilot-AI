import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ApiError, deleteJob, getJob, updateJob } from "../api/client";
import MatchScoreCard from "../components/MatchScoreCard";
import StatusBadge from "../components/StatusBadge";
import TagList from "../components/TagList";
import type { Job, JobStatus } from "../types/job";
import { JOB_STATUSES, JOB_STATUS_LABELS, formatJobDate } from "../types/job";

type PageState =
  | { kind: "loading" }
  | { kind: "ready"; job: Job }
  | { kind: "error"; message: string };

type ActionState =
  | { kind: "idle" }
  | { kind: "updating" }
  | { kind: "deleting" }
  | { kind: "error"; message: string };

export default function JobDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const jobId = Number(id);

  const [pageState, setPageState] = useState<PageState>({ kind: "loading" });
  const [action, setAction] = useState<ActionState>({ kind: "idle" });

  useEffect(() => {
    if (!Number.isFinite(jobId)) {
      setPageState({ kind: "error", message: "Invalid job ID." });
      return;
    }

    let cancelled = false;

    getJob(jobId)
      .then((job) => {
        if (!cancelled) setPageState({ kind: "ready", job });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message =
            error instanceof ApiError && error.status === 404
              ? "Job not found."
              : error instanceof ApiError
                ? `Could not load job (${error.status})`
                : "Could not reach the backend.";
          setPageState({ kind: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  async function handleStatusChange(status: JobStatus) {
    if (pageState.kind !== "ready") return;
    setAction({ kind: "updating" });
    try {
      const updated = await updateJob(pageState.job.id, { status });
      setPageState({ kind: "ready", job: updated });
      setAction({ kind: "idle" });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Could not update status.";
      setAction({ kind: "error", message });
    }
  }

  async function handleDelete() {
    if (pageState.kind !== "ready") return;
    if (!window.confirm(`Delete ${pageState.job.company} — ${pageState.job.role}?`)) return;

    setAction({ kind: "deleting" });
    try {
      await deleteJob(pageState.job.id);
      navigate("/jobs");
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Could not delete job.";
      setAction({ kind: "error", message });
    }
  }

  if (pageState.kind === "loading") {
    return (
      <main className="page">
        <div className="page__loading">
          <div className="spinner" aria-hidden="true" />
          <p>Loading job…</p>
        </div>
      </main>
    );
  }

  if (pageState.kind === "error") {
    return (
      <main className="page">
        <div className="alert alert--error" role="alert">
          {pageState.message}
        </div>
        <Link to="/jobs" className="btn btn--ghost" style={{ marginTop: "1rem" }}>
          ← Back to jobs
        </Link>
      </main>
    );
  }

  const { job } = pageState;
  const busy = action.kind === "updating" || action.kind === "deleting";

  return (
    <main className="page page--wide">
      <header className="page__header">
        <div>
          <p className="page__eyebrow">Job detail</p>
          <h1>{job.company}</h1>
          <p className="page__subtitle">{job.role}</p>
        </div>
        <div className="page__header-actions">
          <StatusBadge status={job.status} />
          <Link to="/jobs" className="btn btn--ghost">
            ← All jobs
          </Link>
        </div>
      </header>

      <section className="card">
        <h2 className="card__title">Application status</h2>
        <div className="status-select-row">
          {JOB_STATUSES.map((status) => (
            <button
              key={status}
              type="button"
              className={`status-select-btn${job.status === status ? " status-select-btn--active" : ""}`}
              onClick={() => handleStatusChange(status)}
              disabled={busy || job.status === status}
            >
              {JOB_STATUS_LABELS[status]}
            </button>
          ))}
        </div>
        <p className="page__meta">
          Saved {formatJobDate(job.created_at)} · Updated {formatJobDate(job.updated_at)}
        </p>
        {job.job_url && (
          <p className="job-url">
            <a href={job.job_url} target="_blank" rel="noreferrer">
              View original posting →
            </a>
          </p>
        )}
      </section>

      <MatchScoreCard jobId={job.id} />

      <section className="card">
        <TagList title="Requirements" items={job.requirements} />
        <TagList title="Skills" items={job.skills} />
        <TagList title="Responsibilities" items={job.responsibilities} />
      </section>

      <section className="card card--muted">
        <h2 className="card__title">Full job description</h2>
        <p className="jd-preview">{job.raw_description}</p>
      </section>

      <div className="form-actions">
        <button
          type="button"
          className="btn btn--ghost btn--danger"
          onClick={handleDelete}
          disabled={busy}
        >
          {action.kind === "deleting" ? "Deleting…" : "Delete job"}
        </button>
      </div>

      {action.kind === "error" && (
        <p className="form-actions__feedback form-actions__feedback--error" role="alert">
          {action.message}
        </p>
      )}
    </main>
  );
}
