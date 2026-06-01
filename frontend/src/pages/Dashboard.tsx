import { useEffect, useState } from "react";
import { ApiError, getHealth } from "../api/client";

type ConnectionState =
  | { kind: "loading" }
  | { kind: "connected"; status: string }
  | { kind: "error"; message: string };

export default function Dashboard() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;

    getHealth()
      .then((data) => {
        if (!cancelled) {
          setConnection({ kind: "connected", status: data.status });
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

  return (
    <main className="dashboard">
      <header className="dashboard__header">
        <p className="dashboard__eyebrow">Phase 0</p>
        <h1>CareerPilot AI</h1>
        <p className="dashboard__subtitle">
          Your career copilot — frontend connected to FastAPI backend.
        </p>
      </header>

      <section className="status-card" aria-live="polite">
        <h2>Backend status</h2>
        {connection.kind === "loading" && <p>Checking connection…</p>}
        {connection.kind === "connected" && (
          <p className="status-card__ok">
            Connected — API responded with status: <code>{connection.status}</code>
          </p>
        )}
        {connection.kind === "error" && (
          <p className="status-card__error">{connection.message}</p>
        )}
      </section>

      <section className="next-steps">
        <h2>What this proves</h2>
        <ul>
          <li>
            <code>frontend/src/api/client.ts</code> calls <code>GET /health</code>
          </li>
          <li>
            <code>backend/app/api/routes/health.py</code> responds with{" "}
            <code>{`{"status": "ok"}`}</code>
          </li>
          <li>CORS is configured so the Vite dev server can talk to FastAPI</li>
        </ul>
      </section>
    </main>
  );
}
