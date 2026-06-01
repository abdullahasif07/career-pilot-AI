import type { Profile, ProfileUpdate } from "../types/profile";

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
