import apiClient from "./apiClient";

export interface HealthResponse {
  success: boolean;
  data: {
    status: "healthy" | "warning" | "critical";
    checks: Record<string, string>;
  };
  message: string;
}

export async function getPlatformHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/health/");
  return response.data;
}
