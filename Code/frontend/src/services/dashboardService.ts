import apiClient from "./apiClient";

export interface DashboardStatistics {
  instances: {
    total: number;
    running: number;
    stopped: number;
    failed: number;
    provisioning: number;
  };
  usage: {
    cpu_cores: number;
    memory_gb: number;
  };
  recent_activity: Array<{
    event_type: string;
    message: string;
    created_at: string;
  }>;
}

export async function fetchDashboard() {
  const response = await apiClient.get<{ data: DashboardStatistics }>("/analytics/dashboard/");
  return response.data.data;
}
