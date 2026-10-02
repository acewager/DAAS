import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { launchInstance } from "@/services/instanceService";

interface LaunchButtonProps {
  instanceId: string;
  status: string;
}

/**
 * Launch Desktop button (VS-034, Sprint 4).
 *
 * Fetches the desktop launch URL from the backend and opens it in a new
 * tab, where Traefik routes the hash-based subdomain to the container's
 * desktop UI. Session validation before routing arrives in M6.
 */
export default function LaunchButton({ instanceId, status }: LaunchButtonProps) {
  const [error, setError] = useState(false);
  const mutation = useMutation({
    mutationFn: launchInstance,
    onSuccess: (url) => window.open(url, "_blank", "noopener"),
    onError: () => setError(true),
  });

  const running = status === "RUNNING";
  return (
    <span className="inline-flex flex-col items-start gap-1">
      <button
        className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white disabled:opacity-40"
        disabled={!running || mutation.isPending}
        onClick={() => mutation.mutate(instanceId)}
        type="button"
      >
        {mutation.isPending ? "Launching…" : "Launch desktop"}
      </button>
      {!running && <span className="text-[10px] text-slate-400">Available when running</span>}
      {error && <span className="text-[10px] text-red-600">Unable to launch.</span>}
    </span>
  );
}
