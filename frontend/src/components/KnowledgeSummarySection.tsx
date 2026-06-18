import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  computeKnowledgeSummary,
  getKnowledgeSummary,
  getKnowledgeSummaryPrompt,
  updateKnowledgeSummary,
  updateKnowledgeSummaryPrompt,
} from "../api/client";
import type { KnowledgeSummaryPromptConfig } from "../types/knowledge_summary";
import { formatKnowledgeSummaryDate } from "../types/knowledge_summary";

type KnowledgeSummarySectionProps = {
  onSummarySaved?: () => void;
};

type SummaryState =
  | { kind: "loading" }
  | { kind: "ready"; summary: string; generatedAt: string | null; hasSummary: boolean }
  | { kind: "error"; message: string };

type PromptState =
  | { kind: "loading" }
  | { kind: "ready"; config: KnowledgeSummaryPromptConfig; draft: string }
  | { kind: "error"; message: string };

export default function KnowledgeSummarySection({
  onSummarySaved,
}: KnowledgeSummarySectionProps) {
  const [summaryState, setSummaryState] = useState<SummaryState>({ kind: "loading" });
  const [promptState, setPromptState] = useState<PromptState>({ kind: "loading" });
  const [draftSummary, setDraftSummary] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSavingSummary, setIsSavingSummary] = useState(false);
  const [isSavingPrompt, setIsSavingPrompt] = useState(false);
  const [summaryFeedback, setSummaryFeedback] = useState<string | null>(null);
  const [promptFeedback, setPromptFeedback] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    setSummaryState({ kind: "loading" });
    try {
      const data = await getKnowledgeSummary();
      setSummaryState({
        kind: "ready",
        summary: data.summary ?? "",
        generatedAt: data.generated_at,
        hasSummary: data.has_summary,
      });
      setDraftSummary(data.summary ?? "");
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not load agent knowledge summary.";
      setSummaryState({ kind: "error", message });
    }
  }, []);

  const loadPrompt = useCallback(async () => {
    setPromptState({ kind: "loading" });
    try {
      const config = await getKnowledgeSummaryPrompt();
      setPromptState({
        kind: "ready",
        config,
        draft: config.custom_system_prompt ?? config.default_system_prompt,
      });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not load summary prompt.";
      setPromptState({ kind: "error", message });
    }
  }, []);

  useEffect(() => {
    loadSummary();
    loadPrompt();
  }, [loadSummary, loadPrompt]);

  async function handleGenerate() {
    setIsGenerating(true);
    setSummaryFeedback(null);
    try {
      const result = await computeKnowledgeSummary();
      setSummaryState({
        kind: "ready",
        summary: result.summary,
        generatedAt: result.generated_at,
        hasSummary: true,
      });
      setDraftSummary(result.summary);
      setSummaryFeedback("Summary generated");
      onSummarySaved?.();
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not generate knowledge summary.";
      setSummaryFeedback(message);
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleSaveSummary() {
    setIsSavingSummary(true);
    setSummaryFeedback(null);
    try {
      const trimmed = draftSummary.trim();
      const data = await updateKnowledgeSummary({
        summary: trimmed || null,
      });
      setSummaryState({
        kind: "ready",
        summary: data.summary ?? "",
        generatedAt: data.generated_at,
        hasSummary: data.has_summary,
      });
      setDraftSummary(data.summary ?? "");
      setSummaryFeedback(data.has_summary ? "Summary saved" : "Summary cleared");
      onSummarySaved?.();
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Could not save summary.";
      setSummaryFeedback(message);
    } finally {
      setIsSavingSummary(false);
    }
  }

  async function handleSavePrompt() {
    if (promptState.kind !== "ready") return;

    setIsSavingPrompt(true);
    setPromptFeedback(null);
    try {
      const trimmed = promptState.draft.trim();
      const isDefault = trimmed === promptState.config.default_system_prompt.trim();
      const config = await updateKnowledgeSummaryPrompt({
        system_prompt: isDefault || !trimmed ? null : trimmed,
      });
      setPromptState({
        kind: "ready",
        config,
        draft: config.custom_system_prompt ?? config.default_system_prompt,
      });
      setPromptFeedback(
        config.uses_custom ? "Custom prompt saved" : "Using default prompt",
      );
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Could not save prompt.";
      setPromptFeedback(message);
    } finally {
      setIsSavingPrompt(false);
    }
  }

  function handleResetPrompt() {
    if (promptState.kind !== "ready") return;
    setPromptState({
      ...promptState,
      draft: promptState.config.default_system_prompt,
    });
    setPromptFeedback(null);
  }

  const usesCustomPrompt =
    promptState.kind === "ready" && promptState.config.uses_custom;

  const summaryDirty =
    summaryState.kind === "ready" &&
    draftSummary.trim() !== (summaryState.summary ?? "").trim();

  const promptDirty =
    promptState.kind === "ready" &&
    promptState.draft.trim() !==
      (promptState.config.custom_system_prompt ??
        promptState.config.default_system_prompt).trim();

  return (
    <section className="card knowledge-summary-card">
      <div className="card__header-row">
        <div>
          <h2 className="card__title">Agent knowledge summary</h2>
          <p className="card__desc">
            A condensed view of your knowledge base that agents use for cover
            letters, match scoring, and resume tailoring. Edit directly or
            regenerate from your profile and resume.
          </p>
        </div>
        <div className="knowledge-summary-card__actions">
          <button
            type="button"
            className="btn btn--secondary btn--sm"
            onClick={handleGenerate}
            disabled={isGenerating || isSavingSummary}
          >
            {isGenerating ? "Generating…" : "Generate summary"}
          </button>
        </div>
      </div>

      {summaryState.kind === "loading" && (
        <p className="muted">Loading agent knowledge summary…</p>
      )}

      {summaryState.kind === "error" && (
        <div className="alert alert--error" role="alert">
          {summaryState.message}
        </div>
      )}

      {summaryState.kind === "ready" && (
        <>
          {summaryState.generatedAt && summaryState.hasSummary && (
            <p className="knowledge-summary__generated">
              Last generated {formatKnowledgeSummaryDate(summaryState.generatedAt)}
            </p>
          )}

          <div className="form-field">
            <label className="form-field__label" htmlFor="agent-knowledge-summary">
              Summary text
            </label>
            <p className="form-field__hint">
              This is what agents see instead of raw profile fields when set.
            </p>
            <textarea
              id="agent-knowledge-summary"
              className="form-field__input form-field__input--textarea knowledge-summary__textarea"
              value={draftSummary}
              onChange={(e) => {
                setDraftSummary(e.target.value);
                setSummaryFeedback(null);
              }}
              rows={12}
              placeholder="Generate a summary or write your own agent-ready briefing…"
              disabled={isGenerating}
            />
          </div>

          <div className="knowledge-summary-card__actions">
            <button
              type="button"
              className="btn btn--primary btn--sm"
              onClick={handleSaveSummary}
              disabled={isSavingSummary || isGenerating || !draftSummary.trim()}
            >
              {isSavingSummary ? "Saving…" : "Save summary"}
            </button>
          </div>

          {summaryFeedback && (
            <p
              className={`knowledge-summary__feedback${
                summaryFeedback.includes("Could not")
                  ? " knowledge-summary__feedback--error"
                  : ""
              }`}
              role="status"
            >
              {summaryFeedback}
            </p>
          )}

          {summaryDirty && !summaryFeedback && (
            <p className="knowledge-summary__feedback knowledge-summary__feedback--warn">
              Unsaved summary changes.
            </p>
          )}
        </>
      )}

      <details className="knowledge-summary-prompt">
        <summary className="knowledge-summary-prompt__summary">
          <span>Customize summary prompt</span>
          {usesCustomPrompt && (
            <span className="knowledge-summary-prompt__badge">Custom</span>
          )}
        </summary>

        <div className="knowledge-summary-prompt__body">
          {promptState.kind === "loading" && (
            <p className="muted">Loading prompt settings…</p>
          )}

          {promptState.kind === "error" && (
            <div className="alert alert--error" role="alert">
              {promptState.message}
            </div>
          )}

          {promptState.kind === "ready" && (
            <>
              <p className="form-field__hint">
                Controls how the summary is generated from your profile and
                resume. Plain text output is fine.
              </p>

              <textarea
                className="form-field__input form-field__input--textarea knowledge-summary-prompt__textarea"
                value={promptState.draft}
                onChange={(e) => {
                  setPromptState({ ...promptState, draft: e.target.value });
                  setPromptFeedback(null);
                }}
                rows={10}
                spellCheck={false}
              />

              <div className="knowledge-summary-prompt__actions">
                <button
                  type="button"
                  className="btn btn--primary btn--sm"
                  onClick={handleSavePrompt}
                  disabled={isSavingPrompt || !promptState.draft.trim()}
                >
                  {isSavingPrompt ? "Saving…" : "Save prompt"}
                </button>
                <button
                  type="button"
                  className="btn btn--ghost btn--sm"
                  onClick={handleResetPrompt}
                  disabled={isSavingPrompt}
                >
                  Reset to default
                </button>
              </div>

              {promptFeedback && (
                <p
                  className={`knowledge-summary__feedback${
                    promptFeedback.includes("Could not")
                      ? " knowledge-summary__feedback--error"
                      : ""
                  }`}
                  role="status"
                >
                  {promptFeedback}
                </p>
              )}

              {promptDirty && !promptFeedback && (
                <p className="knowledge-summary__feedback knowledge-summary__feedback--warn">
                  Unsaved prompt changes — save before generating.
                </p>
              )}
            </>
          )}
        </div>
      </details>
    </section>
  );
}
