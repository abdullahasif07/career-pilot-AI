import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ApiError,
  computeJobCoverLetter,
  getCoverLetterPrompt,
  getJobCoverLetter,
  updateCoverLetterPrompt,
} from "../api/client";
import type { CoverLetterPromptConfig, JobCoverLetterResult } from "../types/cover_letter";
import {
  coverLetterToText,
  formatCoverLetterDate,
} from "../types/cover_letter";

type CoverLetterCardProps = {
  jobId: number;
};

type CoverLetterState =
  | { kind: "loading" }
  | { kind: "empty" }
  | { kind: "ready"; result: JobCoverLetterResult }
  | { kind: "error"; message: string };

type PromptEditorState =
  | { kind: "loading" }
  | { kind: "ready"; config: CoverLetterPromptConfig; draft: string }
  | { kind: "error"; message: string };

export default function CoverLetterCard({ jobId }: CoverLetterCardProps) {
  const [state, setState] = useState<CoverLetterState>({ kind: "loading" });
  const [promptState, setPromptState] = useState<PromptEditorState>({
    kind: "loading",
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSavingPrompt, setIsSavingPrompt] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
  const [promptFeedback, setPromptFeedback] = useState<string | null>(null);
  const [editedSubject, setEditedSubject] = useState("");
  const [editedBody, setEditedBody] = useState("");

  const loadSaved = useCallback(async () => {
    setState({ kind: "loading" });
    try {
      const data = await getJobCoverLetter(jobId);
      if (data.computed && data.cover_letter) {
        setState({ kind: "ready", result: data.cover_letter });
      } else {
        setState({ kind: "empty" });
      }
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not load cover letter.";
      setState({ kind: "error", message });
    }
  }, [jobId]);

  const loadPrompt = useCallback(async () => {
    setPromptState({ kind: "loading" });
    try {
      const config = await getCoverLetterPrompt();
      setPromptState({
        kind: "ready",
        config,
        draft: config.custom_system_prompt ?? config.default_system_prompt,
      });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not load cover letter prompt.";
      setPromptState({ kind: "error", message });
    }
  }, []);

  const runGenerate = useCallback(async () => {
    setIsGenerating(true);
    setCopyFeedback(null);
    try {
      const result = await computeJobCoverLetter(jobId);
      setState({ kind: "ready", result });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not generate cover letter.";
      setState({ kind: "error", message });
    } finally {
      setIsGenerating(false);
    }
  }, [jobId]);

  useEffect(() => {
    loadSaved();
    loadPrompt();
  }, [loadSaved, loadPrompt]);

  useEffect(() => {
    if (state.kind === "ready") {
      setEditedSubject(state.result.subject ?? "");
      setEditedBody(state.result.body);
    }
  }, [state]);

  const hasResult = state.kind === "ready";
  const isLoading = state.kind === "loading";

  async function handleCopy() {
    try {
      const subject = editedSubject.trim() || null;
      await navigator.clipboard.writeText(coverLetterToText(subject, editedBody));
      setCopyFeedback("Copied to clipboard");
    } catch {
      setCopyFeedback("Could not copy to clipboard");
    }
  }

  async function handleSavePrompt() {
    if (promptState.kind !== "ready") return;

    setIsSavingPrompt(true);
    setPromptFeedback(null);
    try {
      const trimmed = promptState.draft.trim();
      const isDefault = trimmed === promptState.config.default_system_prompt.trim();
      const config = await updateCoverLetterPrompt({
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
        error instanceof ApiError
          ? error.message
          : "Could not save prompt.";
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

  function handleDraftChange(draft: string) {
    if (promptState.kind !== "ready") return;
    setPromptState({ ...promptState, draft });
    setPromptFeedback(null);
  }

  const usesCustomPrompt =
    promptState.kind === "ready" && promptState.config.uses_custom;

  return (
    <section className="card cover-letter-card">
      <div className="card__header-row">
        <div>
          <h2 className="card__title">Cover letter</h2>
          <p className="card__desc">
            Role-specific letter grounded in your profile and tailored resume.
            Saved until you generate again.
          </p>
        </div>
        {hasResult && (
          <div className="cover-letter-card__actions">
            <button
              type="button"
              className="btn btn--ghost btn--sm"
              onClick={handleCopy}
              disabled={isGenerating || !editedBody.trim()}
            >
              Copy letter
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

      <CoverLetterPromptEditor
        state={promptState}
        isSaving={isSavingPrompt}
        feedback={promptFeedback}
        usesCustom={usesCustomPrompt}
        onDraftChange={handleDraftChange}
        onSave={handleSavePrompt}
        onReset={handleResetPrompt}
      />

      {isLoading && (
        <div className="cover-letter-card__loading">
          <div className="spinner" aria-hidden="true" />
          <p>Loading saved cover letter…</p>
        </div>
      )}

      {state.kind === "empty" && (
        <div className="cover-letter-card__empty">
          <p className="muted">
            No cover letter yet. Generate one from your knowledge base and this
            job. A tailored resume improves consistency if you generate one first.
          </p>
          <button
            type="button"
            className="btn btn--primary btn--sm"
            onClick={runGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? "Generating…" : "Generate cover letter"}
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

      {copyFeedback && hasResult && (
        <p className="cover-letter-card__copy-feedback" role="status">
          {copyFeedback}
        </p>
      )}

      {hasResult && (
        <CoverLetterView
          result={state.result}
          isGenerating={isGenerating}
          editedSubject={editedSubject}
          editedBody={editedBody}
          onSubjectChange={setEditedSubject}
          onBodyChange={setEditedBody}
        />
      )}
    </section>
  );
}

function CoverLetterPromptEditor({
  state,
  isSaving,
  feedback,
  usesCustom,
  onDraftChange,
  onSave,
  onReset,
}: {
  state: PromptEditorState;
  isSaving: boolean;
  feedback: string | null;
  usesCustom: boolean;
  onDraftChange: (value: string) => void;
  onSave: () => void;
  onReset: () => void;
}) {
  if (state.kind === "loading") {
    return (
      <p className="cover-letter-prompt__loading muted">Loading prompt settings…</p>
    );
  }

  if (state.kind === "error") {
    return (
      <div className="alert alert--error" role="alert">
        {state.message}
      </div>
    );
  }

  const draftDiffersFromSaved =
    state.draft.trim() !==
    (state.config.custom_system_prompt ?? state.config.default_system_prompt).trim();

  return (
    <details className="cover-letter-prompt">
      <summary className="cover-letter-prompt__summary">
        <span>Customize system prompt</span>
        {usesCustom && (
          <span className="cover-letter-prompt__badge">Custom</span>
        )}
      </summary>

      <div className="cover-letter-prompt__body">
        <p className="form-field__hint">
          Controls tone, style, and rules for every cover letter you generate.
          JSON output is optional — plain text letters work too.
        </p>

        <textarea
          className="form-field__input form-field__input--textarea cover-letter-prompt__textarea"
          value={state.draft}
          onChange={(e) => onDraftChange(e.target.value)}
          rows={12}
          spellCheck={false}
        />

        <div className="cover-letter-prompt__actions">
          <button
            type="button"
            className="btn btn--primary btn--sm"
            onClick={onSave}
            disabled={isSaving || !state.draft.trim()}
          >
            {isSaving ? "Saving…" : "Save prompt"}
          </button>
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={onReset}
            disabled={isSaving}
          >
            Reset to default
          </button>
        </div>

        {feedback && (
          <p
            className={`cover-letter-prompt__feedback${
              feedback.includes("Could not") ? " cover-letter-prompt__feedback--error" : ""
            }`}
            role="status"
          >
            {feedback}
          </p>
        )}

        {draftDiffersFromSaved && !feedback && (
          <p className="cover-letter-prompt__feedback cover-letter-prompt__feedback--warn">
            Unsaved changes — save before generating to apply your prompt.
          </p>
        )}
      </div>
    </details>
  );
}

function CoverLetterView({
  result,
  isGenerating,
  editedSubject,
  editedBody,
  onSubjectChange,
  onBodyChange,
}: {
  result: JobCoverLetterResult;
  isGenerating: boolean;
  editedSubject: string;
  editedBody: string;
  onSubjectChange: (value: string) => void;
  onBodyChange: (value: string) => void;
}) {
  return (
    <div
      className={`cover-letter${isGenerating ? " cover-letter--busy" : ""}`}
    >
      <p className="cover-letter__generated">
        Generated {formatCoverLetterDate(result.generated_at)}
        {isGenerating && " · updating…"}
      </p>

      {result.notes && (
        <p className="cover-letter__notes">{result.notes}</p>
      )}

      <div className="form-field">
        <label className="form-field__label" htmlFor="cover-letter-subject">
          Subject line
        </label>
        <p className="form-field__hint">Optional — for email applications.</p>
        <input
          id="cover-letter-subject"
          type="text"
          className="form-field__input"
          value={editedSubject}
          onChange={(e) => onSubjectChange(e.target.value)}
          placeholder="Application for …"
          disabled={isGenerating}
        />
      </div>

      <div className="form-field">
        <label className="form-field__label" htmlFor="cover-letter-body">
          Letter body
        </label>
        <p className="form-field__hint">
          Edit before copying — local changes are not saved to the server.
        </p>
        <textarea
          id="cover-letter-body"
          className="form-field__input form-field__input--textarea cover-letter__body"
          value={editedBody}
          onChange={(e) => onBodyChange(e.target.value)}
          rows={14}
          disabled={isGenerating}
        />
      </div>

      <p className="cover-letter__hint">
        Updated your{" "}
        <Link to="/profile">knowledge base</Link> or tailored resume? Click{" "}
        <strong>Generate again</strong> to refresh.
      </p>
    </div>
  );
}
