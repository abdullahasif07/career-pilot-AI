import { useRef, useState } from "react";
import { ApiError, deleteResume, extractResume, uploadResume } from "../api/client";
import type { ProfileUpdate } from "../types/profile";
import type { ResumeMeta } from "../types/profile";
import { formatFileSize } from "../types/profile";

type ResumeUploadProps = {
  resume: ResumeMeta | null;
  onResumeChange: (resume: ResumeMeta | null) => void;
  onExtracted: (data: ProfileUpdate) => void;
};

type UploadState =
  | { kind: "idle" }
  | { kind: "uploading" }
  | { kind: "extracting" }
  | { kind: "error"; message: string };

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function ResumeUpload({
  resume,
  onResumeChange,
  onExtracted,
}: ResumeUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploadState, setUploadState] = useState<UploadState>({ kind: "idle" });
  const [offerExtract, setOfferExtract] = useState(false);

  async function runExtraction() {
    setOfferExtract(false);
    setUploadState({ kind: "extracting" });
    try {
      const extracted = await extractResume();
      onExtracted(extracted);
      setUploadState({ kind: "idle" });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "AI extraction failed. Check GEMINI_API_KEY in the project root .env file.";
      setUploadState({ kind: "error", message });
    }
  }

  async function handleFileChange(file: File | undefined) {
    if (!file) return;

    if (file.type !== "application/pdf") {
      setUploadState({ kind: "error", message: "Please upload a PDF file." });
      return;
    }

    setUploadState({ kind: "uploading" });
    setOfferExtract(false);
    try {
      const profile = await uploadResume(file);
      onResumeChange(profile.resume);
      setUploadState({ kind: "idle" });
      setOfferExtract(true);
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Upload failed. Try again.";
      setUploadState({ kind: "error", message });
    }
  }

  async function handleRemove() {
    setUploadState({ kind: "uploading" });
    setOfferExtract(false);
    try {
      await deleteResume();
      onResumeChange(null);
      setUploadState({ kind: "idle" });
      if (inputRef.current) inputRef.current.value = "";
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Could not remove resume.";
      setUploadState({ kind: "error", message });
    }
  }

  const busy = uploadState.kind === "uploading" || uploadState.kind === "extracting";

  return (
    <section className="card">
      <h2 className="card__title">Master resume (PDF)</h2>
      <p className="card__desc">
        Upload your resume, then use AI to fill profile fields below. Review and
        edit anything before saving — nothing is persisted until you click Save profile.
      </p>

      {resume ? (
        <div className="resume-file">
          <div className="resume-file__icon" aria-hidden="true">
            PDF
          </div>
          <div className="resume-file__info">
            <p className="resume-file__name">{resume.filename}</p>
            <p className="resume-file__meta">
              Uploaded {formatDate(resume.uploaded_at)}
              {resume.size_bytes ? ` · ${formatFileSize(resume.size_bytes)}` : ""}
            </p>
          </div>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={handleRemove}
            disabled={busy}
          >
            Remove
          </button>
        </div>
      ) : (
        <label className="upload-zone">
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="upload-zone__input"
            disabled={busy}
            onChange={(e) => handleFileChange(e.target.files?.[0])}
          />
          <span className="upload-zone__icon" aria-hidden="true">
            ↑
          </span>
          <span className="upload-zone__label">
            {uploadState.kind === "uploading"
              ? "Uploading…"
              : "Click or drag to upload PDF"}
          </span>
          <span className="upload-zone__hint">Max 10 MB · PDF only</span>
        </label>
      )}

      {resume && (
        <div className="resume-actions">
          <button
            type="button"
            className="btn btn--primary btn--sm"
            onClick={runExtraction}
            disabled={busy}
          >
            {uploadState.kind === "extracting"
              ? "Extracting with AI…"
              : "Fill fields with AI"}
          </button>
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={() => inputRef.current?.click()}
            disabled={busy}
          >
            Replace PDF
          </button>
          <input
            type="file"
            accept="application/pdf,.pdf"
            className="upload-zone__input"
            hidden
            ref={inputRef}
            onChange={(e) => handleFileChange(e.target.files?.[0])}
          />
        </div>
      )}

      {offerExtract && uploadState.kind === "idle" && (
        <p className="resume-prompt" role="status">
          Resume uploaded.{" "}
          <button type="button" className="link-btn" onClick={runExtraction}>
            Fill fields with AI now
          </button>
        </p>
      )}

      {uploadState.kind === "error" && (
        <p className="form-actions__feedback form-actions__feedback--error" role="alert">
          {uploadState.message}
        </p>
      )}
    </section>
  );
}
