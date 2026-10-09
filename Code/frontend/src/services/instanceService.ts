import apiClient from "./apiClient";

export interface Instance {
  id: string;
  name: string;
  template_name: string;
  status: string;
  subdomain?: string;
  cpu_limit: string;
  memory_limit: string;
  persistent?: boolean;
  auto_stop_minutes?: number;
  error_message: string;
  cpu_average: number;
  ram_average: number; // MB
  uptime_seconds: number;
}

export interface OrderInstanceInput {
  name: string;
  templateId: string;
  cpuLimit: string;
  memoryLimit: string;
  persistent: boolean;
  autoStopMinutes: number;
}

export async function fetchInstances() {
  const response = await apiClient.get<{ data: { instances: Instance[] } }>("/instances/");
  return response.data.data.instances;
}

export async function createInstance(input: OrderInstanceInput) {
  const response = await apiClient.post<{ data: { instance: Instance } }>("/instances/", {
    name: input.name,
    template_id: input.templateId,
    cpu_limit: input.cpuLimit,
    memory_limit: input.memoryLimit,
    persistent: input.persistent,
    auto_stop_minutes: input.autoStopMinutes,
  });
  return response.data.data.instance;
}

/** Returns the desktop launch URL for a running instance (VS-034). */
export async function launchInstance(id: string) {
  const response = await apiClient.get<{ data: { url: string } }>(`/instances/${id}/launch/`);
  return response.data.data.url;
}

/** Container operations (Sprint 5, VS-035 through VS-038). With deleteData
 * the persistent volume is removed too (VS-043); by default data is retained. */
export async function startInstance(id: string) {
  await apiClient.post(`/instances/${id}/start/`);
}

export async function stopInstance(id: string) {
  await apiClient.post(`/instances/${id}/stop/`);
}

export async function restartInstance(id: string) {
  await apiClient.post(`/instances/${id}/restart/`);
}

export async function deleteInstance(id: string, deleteData = false) {
  await apiClient.delete(`/instances/${id}/${deleteData ? "?delete_data=true" : ""}`);
}
