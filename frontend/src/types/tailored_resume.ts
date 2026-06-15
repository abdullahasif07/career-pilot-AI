export type TailoredResumeItem = {
  title: string | null;
  bullets: string[];
};

export type TailoredResumeSection = {
  heading: string;
  items: TailoredResumeItem[];
};

export type JobTailoredResumeResult = {
  job_id: number;
  summary: string | null;
  sections: TailoredResumeSection[];
  notes: string | null;
  generated_at: string;
};

export type JobTailoredResumeRead = {
  computed: boolean;
  resume: JobTailoredResumeResult | null;
};

export function formatTailoredResumeDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function tailoredResumeToText(result: JobTailoredResumeResult): string {
  const lines: string[] = [];

  if (result.summary) {
    lines.push(result.summary, "");
  }

  for (const section of result.sections) {
    lines.push(section.heading.toUpperCase());
    for (const item of section.items) {
      if (item.title) {
        lines.push(item.title);
      }
      for (const bullet of item.bullets) {
        lines.push(`• ${bullet}`);
      }
      lines.push("");
    }
  }

  return lines.join("\n").trim();
}
