import apiClient from "./apiClient";

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  role: "USER" | "ADMIN" | "SUPER_ADMIN";
  is_active: boolean;
  date_joined: string;
  instance_count: number;
}

export interface AdminInstance {
  id: string;
  name: string;
  username: string;
  template_name: string;
  status: string;
  subdomain?: string;
  cpu_limit: string;
  memory_limit: string;
  container_name: string;
  error_message: string;
}

export interface AdminEvent {
  id: string;
  event_type: string;
  message: string;
  created_at: string;
  actor_name: string;
}

export interface Pagination {
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface PlatformAnalytics {
  users: { total: number; active: number };
  instances: { total: number; running: number; stopped: number; failed: number; deleted: number };
  software_requests: { total: number; pending: number; approved: number; rejected: number; installed: number; failed: number };
  recent_events: Array<{ event_type: string; message: string; actor: string | null; created_at: string }>;
}

export async function fetchAdminUsers(params: { search?: string; role?: string; page?: number; pageSize?: number } = {}) {
  const query = new URLSearchParams();
  if (params.search) query.set("search", params.search);
  if (params.role) query.set("role", params.role);
  if (params.page) query.set("page", String(params.page));
  if (params.pageSize) query.set("page_size", String(params.pageSize));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  const response = await apiClient.get<{ data: { users: AdminUser[]; pagination: Pagination } }>(`/admin/users/${suffix}`);
  return response.data.data;
}

export async function updateAdminUser(id: string, changes: { role?: string; is_active?: boolean }) {
  const response = await apiClient.patch<{ data: { user: AdminUser } }>(`/admin/users/${id}/`, changes);
  return response.data.data.user;
}

export async function fetchAdminInstances(params: { status?: string; search?: string; page?: number; pageSize?: number } = {}) {
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.search) query.set("search", params.search);
  if (params.page) query.set("page", String(params.page));
  if (params.pageSize) query.set("page_size", String(params.pageSize));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  const response = await apiClient.get<{ data: { instances: AdminInstance[]; pagination: Pagination } }>(`/admin/instances/${suffix}`);
  return response.data.data;
}

export async function fetchAdminEvents(params: { eventType?: string; search?: string; page?: number; pageSize?: number } = {}) {
  const query = new URLSearchParams();
  if (params.eventType) query.set("event_type", params.eventType);
  if (params.search) query.set("search", params.search);
  if (params.page) query.set("page", String(params.page));
  if (params.pageSize) query.set("page_size", String(params.pageSize));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  const response = await apiClient.get<{ data: { events: AdminEvent[]; pagination: Pagination } }>(`/admin/events/${suffix}`);
  return response.data.data;
}

export async function fetchAdminAnalytics() {
  const response = await apiClient.get<{ data: PlatformAnalytics }>("/admin/analytics/");
  return response.data.data;
}

export async function fetchAdminHealth() {
  const response = await apiClient.get<{ data: { status: string; checks: Record<string, string> } }>("/admin/health/");
  return response.data.data;
}
