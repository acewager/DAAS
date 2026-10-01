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
