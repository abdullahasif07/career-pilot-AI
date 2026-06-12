import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, computeJobMatch, getJobMatch } from "../api/client";
import type { JobMatchResult } from "../types/match";
import { formatMatchDate, matchScoreTier } from "../types/match";

type MatchScoreCardProps = {
  jobId: number;
};

type MatchState =
  | { kind: "loading" }
  | { kind: "empty" }
  | { kind: "ready"; result: JobMatchResult }
  | { kind: "error"; message: string };

export default function MatchScoreCard({ jobId }: MatchScoreCardProps) {
  const [state, setState] = useState<MatchState>({ kind: "loading" });
  const [isComputing, setIsComputing] = useState(false);

  const loadSaved = useCallback(async () => {
    setState({ kind: "loading" });
    try {
      const data = await getJobMatch(jobId);
      if (data.computed && data.match) {
        setState({ kind: "ready", result: data.match });
      } else {
        setState({ kind: "empty" });
      }
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not load match score.";
      setState({ kind: "error", message });
    }
  }, [jobId]);

  const runCompute = useCallback(async () => {
    setIsComputing(true);
    try {
      const result = await computeJobMatch(jobId);
      setState({ kind: "ready", result });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not compute match score.";
      setState({ kind: "error", message });
    } finally {
      setIsComputing(false);
    }
  }, [jobId]);

  useEffect(() => {
    loadSaved();
  }, [loadSaved]);

  const hasResult = state.kind === "ready";
  const isLoading = state.kind === "loading";

  return (
    <section className="card match-card">
      <div className="card__header-row">
        <div>
          <h2 className="card__title">Match score</h2>
          <p className="card__desc">
            Compares your knowledge base to this role. Scores are saved until you
            compute again.
          </p>
        </div>
        {hasResult && (
          <button
            type="button"
            className="btn btn--secondary btn--sm"
            onClick={runCompute}
            disabled={isComputing}
          >
            {isComputing ? "Computing…" : "Compute again"}
          </button>
        )}
      </div>

      {isLoading && (
        <div className="match-card__loading">
          <div className="spinner" aria-hidden="true" />
          <p>Loading saved match score…</p>
        </div>
      )}

      {state.kind === "empty" && (
        <div className="match-card__empty">
          <p className="muted">
            No match score yet. Compute once to compare your profile against this job.
          </p>
          <button
            type="button"
            className="btn btn--primary btn--sm"
            onClick={runCompute}
            disabled={isComputing}
          >
            {isComputing ? "Computing…" : "Compute match"}
          </button>
        </div>
      )}

      {state.kind === "error" && (
        <div className="alert alert--error" role="alert">
          {state.message}
          {state.message.includes("GEMINI") && (
            <span>
              {" "}
              Add <code>GEMINI_API_KEY</code> to your root <code>.env</code> file.
            </span>
          )}
        </div>
      )}

      {hasResult && (
        <MatchResultView result={state.result} isComputing={isComputing} />
      )}
    </section>
  );
}

function MatchResultView({
  result,
  isComputing,
}: {
  result: JobMatchResult;
  isComputing: boolean;
}) {
  const tier = matchScoreTier(result.overall_score);

  return (
    <div className={`match-result${isComputing ? " match-result--busy" : ""}`}>
      <div className={`match-score match-score--${tier}`}>
        <span className="match-score__value">{result.overall_score}%</span>
        <span className="match-score__label">Overall match</span>
      </div>

      <p className="match-result__computed">
        Computed {formatMatchDate(result.computed_at)}
        {isComputing && " · updating…"}
      </p>

      {result.summary && (
        <p className="match-result__summary">{result.summary}</p>
      )}

      <div className="match-columns">
        <div className="match-column match-column--strong">
          <h3 className="match-column__title">Strong</h3>
          {result.strong.length > 0 ? (
            <ul className="match-column__list">
              {result.strong.map((item) => (
                <li key={item}>
                  <span className="match-icon match-icon--ok" aria-hidden="true">✓</span>
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">No clear matches found — enrich your profile.</p>
          )}
        </div>

        <div className="match-column match-column--missing">
          <h3 className="match-column__title">Missing</h3>
          {result.missing.length > 0 ? (
            <ul className="match-column__list">
              {result.missing.map((item) => (
                <li key={item}>
                  <span className="match-icon match-icon--gap" aria-hidden="true">✗</span>
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">No major gaps identified.</p>
          )}
        </div>
      </div>

      <p className="match-result__hint">
        Updated your{" "}
        <Link to="/profile">knowledge base</Link>? Click <strong>Compute again</strong>{" "}
        to refresh this score.
      </p>
    </div>
  );
}
