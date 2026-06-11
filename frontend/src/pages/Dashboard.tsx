import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, getHealth, getProfile, listJobs } from "../api/client";
import type { Profile } from "../types/profile";

type ConnectionState =
  | { kind: "loading" }
  | { kind: "connected"; status: string }
  | { kind: "error"; message: string };

export default function Dashboard() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "loading" });
  const [profile, setProfile] = useState<Profile | null>(null);
  const [jobCount, setJobCount] = useState(0);

  useEffect(() => {
    let cancelled = false;

    Promise.all([getHealth(), getProfile(), listJobs()])
      .then(([health, profileData, jobs]) => {
        if (!cancelled) {
          setConnection({ kind: "connected", status: health.status });
          setProfile(profileData);
          setJobCount(jobs.length);
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message =
            error instanceof ApiError
              ? `Backend returned ${error.status}`
              : "Could not reach the backend. Is it running on port 8000?";
          setConnection({ kind: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const hasProfile = Boolean(profile?.name?.trim());

  return (
    <main className="page dashboard">
      <header className="page__header">
        <p className="page__eyebrow">Dashboard</p>
        <h1>Welcome back</h1>
        <p className="page__subtitle">
          CareerPilot AI uses your knowledge base to tailor every application.
        </p>
      </header>

      <section className="card" aria-live="polite">
        <h2 className="card__title">System status</h2>
        {connection.kind === "loading" && <p className="muted">Checking connection…</p>}
        {connection.kind === "connected" && (
          <p className="status-pill status-pill--ok">
            Backend connected · <code>{connection.status}</code>
          </p>
        )}
        {connection.kind === "error" && (
          <p className="status-pill status-pill--error">{connection.message}</p>
        )}
      </section>

      <section className="quick-actions">
        <Link to="/profile" className="action-card">
          <span className="action-card__icon" aria-hidden="true">
            KB
          </span>
          <div>
            <h2 className="action-card__title">Knowledge Base</h2>
            <p className="action-card__desc">
              {hasProfile
                ? `Profile set for ${profile?.name}`
                : "Add your profile — name, links, education"}
            </p>
          </div>
          <span className="action-card__arrow" aria-hidden="true">
            →
          </span>
        </Link>

        <Link to="/jobs" className="action-card">
          <span className="action-card__icon" aria-hidden="true">
            JD
          </span>
          <div>
            <h2 className="action-card__title">Jobs</h2>
            <p className="action-card__desc">
              {jobCount > 0
                ? `${jobCount} saved job${jobCount === 1 ? "" : "s"} — paste & parse new JDs`
                : "Save & parse job descriptions with AI"}
            </p>
          </div>
          <span className="action-card__arrow" aria-hidden="true">
            →
          </span>
        </Link>
      </section>

      <section className="card card--muted">
        <h2 className="card__title">Phase 2 — Jobs</h2>
        <ul className="checklist">
          <li>
            <code>POST /jobs/parse</code> extracts company, role, skills from a JD
          </li>
          <li>
            <code>POST /jobs</code> saves to your application tracker
          </li>
          <li>Update status: interested → applied → interview → offer</li>
        </ul>
      </section>
    </main>
  );
}
