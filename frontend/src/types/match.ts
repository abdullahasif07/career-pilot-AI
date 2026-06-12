export type JobMatchResult = {
  job_id: number;
  overall_score: number;
  strong: string[];
  missing: string[];
  summary: string | null;
  computed_at: string;
};

export type JobMatchRead = {
  computed: boolean;
  match: JobMatchResult | null;
};

export function matchScoreTier(score: number): "high" | "medium" | "low" {
  if (score >= 80) return "high";
  if (score >= 60) return "medium";
  return "low";
}

export function formatMatchDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
