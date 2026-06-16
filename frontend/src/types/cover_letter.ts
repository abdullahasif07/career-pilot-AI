export type JobCoverLetterResult = {
  job_id: number;
  subject: string | null;
  body: string;
  notes: string | null;
  generated_at: string;
};

export type JobCoverLetterRead = {
  computed: boolean;
  cover_letter: JobCoverLetterResult | null;
};

export function formatCoverLetterDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function coverLetterToText(
  subject: string | null,
  body: string,
): string {
  if (subject?.trim()) {
    return `Subject: ${subject.trim()}\n\n${body}`;
  }
  return body;
}
