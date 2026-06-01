import type { ProfileFormState, ProfileUpdate } from "./profile";
import { newProjectFormItem } from "./profile";

export type ResumeExtraction = ProfileUpdate;

export function mergeExtractionIntoForm(
  extracted: ProfileUpdate,
  current: ProfileFormState,
): ProfileFormState {
  const projects =
    extracted.projects && extracted.projects.length > 0
      ? extracted.projects.map((p) => ({
          clientId: crypto.randomUUID(),
          title: p.title,
          summary: p.summary ?? "",
        }))
      : current.projects.length > 0
        ? current.projects
        : [newProjectFormItem()];

  return {
    name: pick(extracted.name, current.name),
    location: pick(extracted.location, current.location),
    education: pick(extracted.education, current.education),
    summary: pick(extracted.summary, current.summary),
    linkedin_url: pick(extracted.linkedin_url, current.linkedin_url),
    portfolio_url: pick(extracted.portfolio_url, current.portfolio_url),
    github_url: pick(extracted.github_url, current.github_url),
    projects,
  };
}

function pick(extracted: string | null | undefined, current: string): string {
  if (extracted != null && extracted.trim() !== "") {
    return extracted.trim();
  }
  return current;
}
