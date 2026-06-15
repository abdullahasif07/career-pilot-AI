import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ApiError,
  computeJobTailoredResume,
  getJobTailoredResume,
} from "../api/client";
import type { JobTailoredResumeResult } from "../types/tailored_resume";
import {
  formatTailoredResumeDate,
  tailoredResumeToText,
} from "../types/tailored_resume";

type TailoredResumeCardProps = {
  jobId: number;
};

type TailoredResumeState =
  | { kind: "loading" }
  | { kind: "empty" }
  | { kind: "ready"; result: JobTailoredResumeResult }
  | { kind: "error"; message: string };

export default function TailoredResumeCard({ jobId }: TailoredResumeCardProps) {
  const [state, setState] = useState<TailoredResumeState>({ kind: "loading" });
  const [isGenerating, setIsGenerating] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);

  const loadSaved = useCallback(async () => {
    setState({ kind: "loading" });
    try {
      const data = await getJobTailoredResume(jobId);
      if (data.computed && data.resume) {
        setState({ kind: "ready", result: data.resume });
      } else {
        setState({ kind: "empty" });
      }
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not load tailored resume.";
      setState({ kind: "error", message });
    }
  }, [jobId]);

  const runGenerate = useCallback(async () => {
    setIsGenerating(true);
    setCopyFeedback(null);
    try {
      const result = await computeJobTailoredResume(jobId);
      setState({ kind: "ready", result });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not generate tailored resume.";
      setState({ kind: "error", message });
    } finally {
      setIsGenerating(false);
    }
  }, [jobId]);

  useEffect(() => {
    loadSaved();
  }, [loadSaved]);

  const hasResult = state.kind === "ready";
  const isLoading = state.kind === "loading";
  const needsMasterResume =
    state.kind === "error" &&
    state.message.toLowerCase().includes("master resume");
  const needsResumeReupload =
    state.kind === "error" &&
    (state.message.toLowerCase().includes("corrupted") ||
      state.message.toLowerCase().includes("re-upload"));

  async function handleCopy(result: JobTailoredResumeResult) {
    try {
      await navigator.clipboard.writeText(tailoredResumeToText(result));
      setCopyFeedback("Copied to clipboard");
    } catch {
      setCopyFeedback("Could not copy to clipboard");
    }
  }

  return (
    <section className="card tailored-resume-card">
      <div className="card__header-row">
        <div>
          <h2 className="card__title">Tailored resume</h2>
          <p className="card__desc">
            Rewrites your master resume for this role. Results are saved until you
            generate again.
          </p>
        </div>
        {hasResult && (
          <div className="tailored-resume-card__actions">
            <button
              type="button"
              className="btn btn--ghost btn--sm"
              onClick={() => handleCopy(state.result)}
              disabled={isGenerating}
            >
              Copy text
            </button>
            <button
              type="button"
              className="btn btn--secondary btn--sm"
              onClick={runGenerate}
              disabled={isGenerating}
            >
              {isGenerating ? "Generating…" : "Generate again"}
            </button>
          </div>
        )}
      </div>

      {isLoading && (
        <div className="tailored-resume-card__loading">
          <div className="spinner" aria-hidden="true" />
          <p>Loading saved tailored resume…</p>
        </div>
      )}

      {state.kind === "empty" && (
        <div className="tailored-resume-card__empty">
          <p className="muted">
            No tailored resume yet. Generate one from your master resume and
            knowledge base.
          </p>
          <button
            type="button"
            className="btn btn--primary btn--sm"
            onClick={runGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? "Generating…" : "Generate tailored resume"}
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
          {needsMasterResume && (
            <span>
              {" "}
              Upload your PDF on the{" "}
              <Link to="/profile">Knowledge Base</Link> page first.
            </span>
          )}
          {needsResumeReupload && !needsMasterResume && (
            <span>
              {" "}
              <Link to="/profile">Re-upload your resume PDF</Link> on the Knowledge Base
              page.
            </span>
          )}
        </div>
      )}

      {copyFeedback && hasResult && (
        <p className="tailored-resume-card__copy-feedback" role="status">
          {copyFeedback}
        </p>
      )}

      {hasResult && (
        <TailoredResumeView result={state.result} isGenerating={isGenerating} />
      )}
    </section>
  );
}

function TailoredResumeView({
  result,
  isGenerating,
}: {
  result: JobTailoredResumeResult;
  isGenerating: boolean;
}) {
  return (
    <div
      className={`tailored-resume${isGenerating ? " tailored-resume--busy" : ""}`}
    >
      <p className="tailored-resume__generated">
        Generated {formatTailoredResumeDate(result.generated_at)}
        {isGenerating && " · updating…"}
      </p>

      {result.notes && (
        <p className="tailored-resume__notes">{result.notes}</p>
      )}

      {result.summary && (
        <div className="tailored-resume__summary">
          <h3 className="tailored-resume__section-title">Summary</h3>
          <p>{result.summary}</p>
        </div>
      )}

      {result.sections.map((section) => (
        <div key={section.heading} className="tailored-resume__section">
          <h3 className="tailored-resume__section-title">{section.heading}</h3>
          {section.items.length > 0 ? (
            section.items.map((item, index) => (
              <div
                key={`${section.heading}-${item.title ?? "item"}-${index}`}
                className="tailored-resume__item"
              >
                {item.title && (
                  <p className="tailored-resume__item-title">{item.title}</p>
                )}
                {item.bullets.length > 0 && (
                  <ul className="tailored-resume__bullets">
                    {item.bullets.map((bullet) => (
                      <li key={bullet}>{bullet}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))
          ) : (
            <p className="muted">No items in this section.</p>
          )}
        </div>
      ))}

      <p className="tailored-resume__hint">
        Updated your{" "}
        <Link to="/profile">master resume or knowledge base</Link>? Click{" "}
        <strong>Generate again</strong> to refresh.
      </p>
    </div>
  );
}
