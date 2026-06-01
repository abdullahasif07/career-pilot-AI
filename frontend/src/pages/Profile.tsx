import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, getProfile, updateProfile } from "../api/client";
import FormField from "../components/FormField";
import ProjectList from "../components/ProjectList";
import ResumeUpload from "../components/ResumeUpload";
import type { ProfileFormState, ResumeMeta } from "../types/profile";
import { formToUpdate, profileToForm } from "../types/profile";

const emptyForm: ProfileFormState = {
  name: "",
  location: "",
  education: "",
  summary: "",
  linkedin_url: "",
  portfolio_url: "",
  github_url: "",
  projects: [],
};

type PageState =
  | { kind: "loading" }
  | { kind: "ready" }
  | { kind: "error"; message: string };

type SaveState =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "success" }
  | { kind: "error"; message: string };

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function Profile() {
  const [pageState, setPageState] = useState<PageState>({ kind: "loading" });
  const [saveState, setSaveState] = useState<SaveState>({ kind: "idle" });
  const [form, setForm] = useState<ProfileFormState>(emptyForm);
  const [resume, setResume] = useState<ResumeMeta | null>(null);
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getProfile()
      .then((profile) => {
        if (!cancelled) {
          setForm(profileToForm(profile));
          setResume(profile.resume);
          setUpdatedAt(profile.updated_at);
          setPageState({ kind: "ready" });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message =
            error instanceof ApiError
              ? `Could not load profile (${error.status})`
              : "Could not reach the backend. Is it running on port 8000?";
          setPageState({ kind: "error", message });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  function updateField<K extends keyof ProfileFormState>(key: K, value: ProfileFormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (saveState.kind === "success") {
      setSaveState({ kind: "idle" });
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaveState({ kind: "saving" });

    try {
      const profile = await updateProfile(formToUpdate(form));
      setForm(profileToForm(profile));
      setResume(profile.resume);
      setUpdatedAt(profile.updated_at);
      setSaveState({ kind: "success" });
    } catch (error: unknown) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Could not save profile. Check your connection.";
      setSaveState({ kind: "error", message });
    }
  }

  if (pageState.kind === "loading") {
    return (
      <main className="page">
        <div className="page__loading">
          <div className="spinner" aria-hidden="true" />
          <p>Loading your knowledge base…</p>
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

  return (
    <main className="page page--wide">
      <header className="page__header">
        <div>
          <p className="page__eyebrow">Knowledge Base</p>
          <h1>Profile</h1>
          <p className="page__subtitle">
            Your core identity, project highlights, and master resume — everything
            agents use to tailor applications.
          </p>
        </div>
        {updatedAt && (
          <p className="page__meta">Last saved {formatDate(updatedAt)}</p>
        )}
      </header>

      <ResumeUpload resume={resume} onResumeChange={setResume} />

      <form className="profile-form" onSubmit={handleSubmit}>
        <section className="card">
          <h2 className="card__title">Profile summary</h2>
          <p className="card__desc">
            A short professional summary — who you are, what you specialize in, and
            what you&apos;re looking for.
          </p>
          <FormField
            id="summary"
            label="Summary"
            type="textarea"
            value={form.summary}
            onChange={(v) => updateField("summary", v)}
            placeholder="AI engineer with 3+ years building production LLM systems, RAG pipelines, and agent workflows…"
            rows={4}
          />
        </section>

        <section className="card">
          <h2 className="card__title">Basic info</h2>
          <div className="form-grid">
            <FormField
              id="name"
              label="Full name"
              value={form.name}
              onChange={(v) => updateField("name", v)}
              placeholder="Abdullah Asif"
            />
            <FormField
              id="location"
              label="Location"
              value={form.location}
              onChange={(v) => updateField("location", v)}
              placeholder="Toronto, ON"
            />
          </div>
          <FormField
            id="education"
            label="Education"
            type="textarea"
            hint="Degrees, institutions, relevant coursework"
            value={form.education}
            onChange={(v) => updateField("education", v)}
            placeholder="BSc Computer Science — University of …"
            rows={3}
          />
        </section>

        <ProjectList
          projects={form.projects}
          onChange={(projects) => updateField("projects", projects)}
        />

        <section className="card">
          <h2 className="card__title">Links</h2>
          <div className="form-grid form-grid--single">
            <FormField
              id="linkedin_url"
              label="LinkedIn"
              type="url"
              value={form.linkedin_url}
              onChange={(v) => updateField("linkedin_url", v)}
              placeholder="https://linkedin.com/in/yourhandle"
            />
            <FormField
              id="portfolio_url"
              label="Portfolio"
              type="url"
              value={form.portfolio_url}
              onChange={(v) => updateField("portfolio_url", v)}
              placeholder="https://yourportfolio.com"
            />
            <FormField
              id="github_url"
              label="GitHub"
              type="url"
              value={form.github_url}
              onChange={(v) => updateField("github_url", v)}
              placeholder="https://github.com/yourhandle"
            />
          </div>
        </section>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn--primary"
            disabled={saveState.kind === "saving"}
          >
            {saveState.kind === "saving" ? "Saving…" : "Save profile"}
          </button>

          {saveState.kind === "success" && (
            <p className="form-actions__feedback form-actions__feedback--ok" role="status">
              Profile saved successfully.
            </p>
          )}
          {saveState.kind === "error" && (
            <p className="form-actions__feedback form-actions__feedback--error" role="alert">
              {saveState.message}
            </p>
          )}
        </div>
      </form>
    </main>
  );
}
