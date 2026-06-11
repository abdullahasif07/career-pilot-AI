import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, listJobs } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import type { Job } from "../types/job";
import { formatJobDate } from "../types/job";

type PageState =
  | { kind: "loading" }
  | { kind: "ready"; jobs: Job[] }
  | { kind: "error"; message: string };

export default function JobsList() {
  const [pageState, setPageState] = useState<PageState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;

    listJobs()
      .then((jobs) => {
        if (!cancelled) setPageState({ kind: "ready", jobs });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message =
            error instanceof ApiError
              ? `Could not load jobs (${error.status})`
              : "Could not reach the backend.";
          setPageState({ kind: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (pageState.kind === "loading") {
    return (
      <main className="page">
        <div className="page__loading">
          <div className="spinner" aria-hidden="true" />
          <p>Loading jobs…</p>
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
      </main>
    );
  }

  const { jobs } = pageState;

  return (
    <main className="page page--wide">
      <header className="page__header">
        <div>
          <p className="page__eyebrow">Jobs</p>
          <h1>Saved job descriptions</h1>
          <p className="page__subtitle">
            Paste a JD, let AI extract company, role, and skills, then track status
            through your pipeline.
          </p>
        </div>
        <Link to="/jobs/new" className="btn btn--primary">
          + Save new job
        </Link>
      </header>

      {jobs.length === 0 ? (
        <section className="card card--empty">
          <h2 className="card__title">No jobs saved yet</h2>
          <p className="card__desc">
            Paste a job description from LinkedIn, company site, or email — Gemini
            will extract the key details for you.
          </p>
          <Link to="/jobs/new" className="btn btn--primary">
            Save your first job
          </Link>
        </section>
      ) : (
        <div className="job-grid">
          {jobs.map((job) => (
            <Link key={job.id} to={`/jobs/${job.id}`} className="job-card">
              <div className="job-card__header">
                <div>
                  <h2 className="job-card__company">{job.company}</h2>
                  <p className="job-card__role">{job.role}</p>
                </div>
                <StatusBadge status={job.status} />
              </div>
              {job.skills.length > 0 && (
                <div className="job-card__skills">
                  {job.skills.slice(0, 5).map((skill) => (
                    <span key={skill} className="skill-chip">
                      {skill}
                    </span>
                  ))}
                  {job.skills.length > 5 && (
                    <span className="skill-chip skill-chip--more">
                      +{job.skills.length - 5}
                    </span>
                  )}
                </div>
              )}
              <p className="job-card__meta">Updated {formatJobDate(job.updated_at)}</p>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
