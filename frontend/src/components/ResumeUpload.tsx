import { useRef, useState } from "react";
import { ApiError, deleteResume, uploadResume } from "../api/client";
import type { ResumeMeta } from "../types/profile";
import { formatFileSize } from "../types/profile";

type ResumeUploadProps = {
  resume: ResumeMeta | null;
  onResumeChange: (resume: ResumeMeta | null) => void;
};

type UploadState =
  | { kind: "idle" }
  | { kind: "uploading" }
  | { kind: "error"; message: string };

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function ResumeUpload({ resume, onResumeChange }: ResumeUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploadState, setUploadState] = useState<UploadState>({ kind: "idle" });

  async function handleFileChange(file: File | undefined) {
    if (!file) return;

    if (file.type !== "application/pdf") {
      setUploadState({ kind: "error", message: "Please upload a PDF file." });
      return;
    }

    setUploadState({ kind: "uploading" });
    try {
      const profile = await uploadResume(file);
      onResumeChange(profile.resume);
      setUploadState({ kind: "idle" });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError ? error.message : "Upload failed. Try again.";
      setUploadState({ kind: "error", message });
    }
  }

  async function handleRemove() {
    setUploadState({ kind: "uploading" });
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

  return (
    <section className="card">
      <h2 className="card__title">Master resume (PDF)</h2>
      <p className="card__desc">
        Upload your master resume. AI extraction from PDF is coming soon — for now
        we store the file so agents can use it in later phases.
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
            disabled={uploadState.kind === "uploading"}
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
            disabled={uploadState.kind === "uploading"}
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
        <div className="resume-replace">
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={() => inputRef.current?.click()}
            disabled={uploadState.kind === "uploading"}
          >
            Replace PDF
          </button>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="upload-zone__input"
            hidden
            onChange={(e) => handleFileChange(e.target.files?.[0])}
          />
        </div>
      )}

      {uploadState.kind === "error" && (
        <p className="form-actions__feedback form-actions__feedback--error" role="alert">
          {uploadState.message}
        </p>
      )}
    </section>
  );
}
