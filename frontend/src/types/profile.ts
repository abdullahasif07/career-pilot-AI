export type Project = {
  id: number;
  title: string;
  summary: string | null;
  sort_order: number;
};

export type ProjectInput = {
  id?: number | null;
  title: string;
  summary?: string | null;
};

export type ResumeMeta = {
  filename: string;
  uploaded_at: string;
  size_bytes: number | null;
};

export type Profile = {
  id: number;
  name: string | null;
  location: string | null;
  education: string | null;
  summary: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  github_url: string | null;
  projects: Project[];
  resume: ResumeMeta | null;
  created_at: string;
  updated_at: string;
};

export type ProfileUpdate = {
  name?: string | null;
  location?: string | null;
  education?: string | null;
  summary?: string | null;
  linkedin_url?: string | null;
  portfolio_url?: string | null;
  github_url?: string | null;
  projects?: ProjectInput[];
};

export type ProjectFormItem = {
  clientId: string;
  title: string;
  summary: string;
};

export type ProfileFormState = {
  name: string;
  location: string;
  education: string;
  summary: string;
  linkedin_url: string;
  portfolio_url: string;
  github_url: string;
  projects: ProjectFormItem[];
};

export function newProjectFormItem(): ProjectFormItem {
  return {
    clientId: crypto.randomUUID(),
    title: "",
    summary: "",
  };
}

export function profileToForm(profile: Profile): ProfileFormState {
  return {
    name: profile.name ?? "",
    location: profile.location ?? "",
    education: profile.education ?? "",
    summary: profile.summary ?? "",
    linkedin_url: profile.linkedin_url ?? "",
    portfolio_url: profile.portfolio_url ?? "",
    github_url: profile.github_url ?? "",
    projects:
      profile.projects.length > 0
        ? profile.projects.map((p) => ({
            clientId: String(p.id),
            title: p.title,
            summary: p.summary ?? "",
          }))
        : [newProjectFormItem()],
  };
}

export function formToUpdate(form: ProfileFormState): ProfileUpdate {
  const projects = form.projects
    .filter((p) => p.title.trim())
    .map((p) => ({
      title: p.title.trim(),
      summary: p.summary.trim() || null,
    }));

  return {
    name: form.name.trim() || null,
    location: form.location.trim() || null,
    education: form.education.trim() || null,
    summary: form.summary.trim() || null,
    linkedin_url: form.linkedin_url.trim() || null,
    portfolio_url: form.portfolio_url.trim() || null,
    github_url: form.github_url.trim() || null,
    projects,
  };
}

export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
