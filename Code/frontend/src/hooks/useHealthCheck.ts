import { useQuery } from "@tanstack/react-query";

import { getPlatformHealth } from "@/services/healthService";

// Confirms frontend <-> backend connectivity (M1 acceptance criteria).
export function useHealthCheck() {
  return useQuery({
    queryKey: ["platform-health"],
    queryFn: getPlatformHealth,
  });
}
