import type { JobStatus } from "../types/job";
import { JOB_STATUS_LABELS } from "../types/job";

type StatusBadgeProps = {
  status: JobStatus;
};

const STATUS_CLASS: Record<JobStatus, string> = {
  interested: "job-status--interested",
  applied: "job-status--applied",
  interview: "job-status--interview",
  rejected: "job-status--rejected",
  offer: "job-status--offer",
  ghosted: "job-status--ghosted",
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`job-status ${STATUS_CLASS[status]}`}>
      {JOB_STATUS_LABELS[status]}
    </span>
  );
}
