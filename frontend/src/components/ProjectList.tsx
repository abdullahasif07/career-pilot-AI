import FormField from "./FormField";
import type { ProjectFormItem } from "../types/profile";
import { newProjectFormItem } from "../types/profile";

type ProjectListProps = {
  projects: ProjectFormItem[];
  onChange: (projects: ProjectFormItem[]) => void;
};

export default function ProjectList({ projects, onChange }: ProjectListProps) {
  function updateProject(clientId: string, patch: Partial<ProjectFormItem>) {
    onChange(
      projects.map((p) => (p.clientId === clientId ? { ...p, ...patch } : p)),
    );
  }

  function removeProject(clientId: string) {
    const next = projects.filter((p) => p.clientId !== clientId);
    onChange(next.length > 0 ? next : [newProjectFormItem()]);
  }

  function addProject() {
    onChange([...projects, newProjectFormItem()]);
  }

  return (
    <section className="card">
      <div className="card__header-row">
        <div>
          <h2 className="card__title">Projects</h2>
          <p className="card__desc">
            Summarize key projects — used when tailoring resumes and cover letters.
          </p>
        </div>
        <button type="button" className="btn btn--secondary btn--sm" onClick={addProject}>
          + Add project
        </button>
      </div>

      <div className="project-list">
        {projects.map((project, index) => (
          <article key={project.clientId} className="project-card">
            <div className="project-card__header">
              <span className="project-card__index">Project {index + 1}</span>
              {projects.length > 1 && (
                <button
                  type="button"
                  className="btn btn--ghost btn--sm"
                  onClick={() => removeProject(project.clientId)}
                >
                  Remove
                </button>
              )}
            </div>
            <FormField
              id={`project-title-${project.clientId}`}
              label="Title"
              value={project.title}
              onChange={(v) => updateProject(project.clientId, { title: v })}
              placeholder="CareerPilot AI"
            />
            <FormField
              id={`project-summary-${project.clientId}`}
              label="Summary"
              type="textarea"
              value={project.summary}
              onChange={(v) => updateProject(project.clientId, { summary: v })}
              placeholder="What you built, tech stack, and impact…"
              rows={3}
            />
          </article>
        ))}
      </div>
    </section>
  );
}
