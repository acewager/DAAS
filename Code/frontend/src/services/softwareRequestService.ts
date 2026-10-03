import apiClient from "./apiClient";

import type { ApiSuccessResponse } from "@/types/auth";

export type SoftwareRequestStatus = "PENDING" | "APPROVED" | "REJECTED" | "INSTALLING" | "INSTALLED" | "FAILED";

export interface SoftwareRequest {
  id: string;
  instance: string;
  instance_name: string;
  software_name: string;
  justification: string;
  status: SoftwareRequestStatus;
  reviewer_name: string;
  reviewed_at: string | null;
  created_at: string;
}

export interface SubmitSoftwareRequestInput {
  instanceId: string;
  softwareName: string;
  justification?: string;
}

export async function fetchSoftwareRequests(status?: SoftwareRequestStatus) {
  const query = status ? `?status=${status}` : "";
  const response = await apiClient.get<{ data: { requests: SoftwareRequest[] } }>(`/software-requests/${query}`);
  return response.data.data.requests;
}

export async function submitSoftwareRequest(input: SubmitSoftwareRequestInput) {
  const response = await apiClient.post<ApiSuccessResponse<{ request: SoftwareRequest }>>("/software-requests/", {
    instance_id: input.instanceId,
    software_name: input.softwareName,
    justification: input.justification ?? "",
  });
  return response.data.data.request;
}

export async function approveSoftwareRequest(id: string) {
  await apiClient.post(`/software-requests/${id}/approve/`);
}

export async function rejectSoftwareRequest(id: string) {
  await apiClient.post(`/software-requests/${id}/reject/`);
}
