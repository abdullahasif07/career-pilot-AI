export type KnowledgeSummaryRead = {
  summary: string | null;
  generated_at: string | null;
  has_summary: boolean;
};

export type KnowledgeSummaryUpdate = {
  summary: string | null;
};

export type KnowledgeSummaryResult = {
  summary: string;
  generated_at: string;
};

export type KnowledgeSummaryPromptConfig = {
  default_system_prompt: string;
  custom_system_prompt: string | null;
  uses_custom: boolean;
};

export type KnowledgeSummaryPromptUpdate = {
  system_prompt: string | null;
};

export function formatKnowledgeSummaryDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
