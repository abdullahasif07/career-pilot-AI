import type { Job, JobCreate, JobParsed, JobUpdate } from "../types/job";
import type { Profile, ProfileUpdate } from "../types/profile";
import type { ResumeExtraction } from "../types/resume";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  const isFormData = init?.body instanceof FormData;
  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let message = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      /* use statusText */
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export type HealthResponse = {
  status: string;
};

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function getProfile(): Promise<Profile> {
  return request<Profile>("/profile");
}

export function updateProfile(payload: ProfileUpdate): Promise<Profile> {
  return request<Profile>("/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function uploadResume(file: File): Promise<Profile> {
  const formData = new FormData();
  formData.append("file", file);
  return request<Profile>("/profile/resume", {
    method: "POST",
    body: formData,
  });
}

export function deleteResume(): Promise<Profile> {
  return request<Profile>("/profile/resume", { method: "DELETE" });
}

export function extractResume(): Promise<ResumeExtraction> {
  return request<ResumeExtraction>("/profile/resume/extract", { method: "POST" });
}

export function parseJob(description: string): Promise<JobParsed> {
  return request<JobParsed>("/jobs/parse", {
    method: "POST",
    body: JSON.stringify({ description }),
  });
}

export function listJobs(): Promise<Job[]> {
  return request<Job[]>("/jobs");
}

export function getJob(id: number): Promise<Job> {
  return request<Job>(`/jobs/${id}`);
}

export function createJob(payload: JobCreate): Promise<Job> {
  return request<Job>("/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateJob(id: number, payload: JobUpdate): Promise<Job> {
  return request<Job>(`/jobs/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteJob(id: number): Promise<void> {
  return request<void>(`/jobs/${id}`, { method: "DELETE" });
}
