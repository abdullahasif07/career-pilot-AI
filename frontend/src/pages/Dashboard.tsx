import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, getHealth, getProfile } from "../api/client";
import type { Profile } from "../types/profile";

type ConnectionState =
  | { kind: "loading" }
  | { kind: "connected"; status: string }
  | { kind: "error"; message: string };

export default function Dashboard() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "loading" });
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    let cancelled = false;

    Promise.all([getHealth(), getProfile()])
      .then(([health, profileData]) => {
        if (!cancelled) {
          setConnection({ kind: "connected", status: health.status });
          setProfile(profileData);
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

        <div className="action-card action-card--disabled">
          <span className="action-card__icon" aria-hidden="true">
            JD
          </span>
          <div>
            <h2 className="action-card__title">Jobs</h2>
            <p className="action-card__desc">Coming in Phase 2 — save & match job descriptions</p>
          </div>
        </div>
      </section>

      <section className="card card--muted">
        <h2 className="card__title">Phase 1 complete</h2>
        <ul className="checklist">
          <li>
            <code>GET /profile</code> loads your knowledge base from SQLite
          </li>
          <li>
            <code>PUT /profile</code> persists changes from the Profile page
          </li>
          <li>Frontend ↔ FastAPI full stack loop is working</li>
        </ul>
      </section>
    </main>
  );
}
