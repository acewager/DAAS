import apiClient from "./apiClient";

export interface DesktopTemplate { id: string; name: string; slug: string; description: string; json_configuration: { image: string }; enabled: boolean }
export async function fetchTemplates() {
  const response = await apiClient.get<{ data: { templates: DesktopTemplate[] } }>("/templates/");
  return response.data.data.templates;
}
