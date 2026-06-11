export type JobStatus =
  | "interested"
  | "applied"
  | "interview"
  | "rejected"
  | "offer"
  | "ghosted";

export type Job = {
  id: number;
  company: string;
  role: string;
  status: JobStatus;
  raw_description: string;
  requirements: string[];
  skills: string[];
  responsibilities: string[];
  job_url: string | null;
  created_at: string;
  updated_at: string;
};

export type JobParsed = {
  company: string;
  role: string;
  requirements: string[];
  skills: string[];
  responsibilities: string[];
};

export type JobCreate = {
  company: string;
  role: string;
  raw_description: string;
  status?: JobStatus;
  requirements?: string[];
  skills?: string[];
  responsibilities?: string[];
  job_url?: string | null;
};

export type JobUpdate = {
  company?: string;
  role?: string;
  status?: JobStatus;
  raw_description?: string;
  requirements?: string[];
  skills?: string[];
  responsibilities?: string[];
  job_url?: string | null;
};

export const JOB_STATUSES: JobStatus[] = [
  "interested",
  "applied",
  "interview",
  "rejected",
  "offer",
  "ghosted",
];

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  interested: "Interested",
  applied: "Applied",
  interview: "Interview",
  rejected: "Rejected",
  offer: "Offer",
  ghosted: "Ghosted",
};

export function formatJobDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
