import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteInstance, launchInstance, restartInstance, startInstance, stopInstance } from "@/services/instanceService";

interface InstanceActionsProps {
  instanceId: string;
  status: string;
}

/**
 * Instance lifecycle actions (Sprint 5, VS-035 through VS-038) plus the
 * Launch Desktop button (VS-034).
 *
 * Start/stop/restart run synchronously; delete is queued asynchronously.
 * Launch opens the hash-based subdomain in a new tab — session validation
 * before routing arrives in M6.
 */
export default function InstanceActions({ instanceId, status }: InstanceActionsProps) {
  const queryClient = useQueryClient();
  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["instances"] });
    void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const start = useMutation({ mutationFn: startInstance, onSuccess: invalidate });
  const stop = useMutation({ mutationFn: stopInstance, onSuccess: invalidate });
  const restart = useMutation({ mutationFn: restartInstance, onSuccess: invalidate });
  const remove = useMutation({
    mutationFn: deleteInstance,
    onSuccess: invalidate,
    onError: invalidate,
  });
  const launch = useMutation({ mutationFn: launchInstance });

  const button = "rounded border border-border px-3 py-1.5 text-xs disabled:opacity-40";
  const busy = start.isPending || stop.isPending || restart.isPending || remove.isPending;

  return (
    <div className="flex flex-wrap items-center gap-2">
      {status === "RUNNING" && (
        <button
          className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white disabled:opacity-40"
          disabled={launch.isPending}
          onClick={() => launch.mutate(instanceId)}
          type="button"
        >
          {launch.isPending ? "Launching…" : "Launch desktop"}
        </button>
      )}
      {status === "STOPPED" && (
        <button className="rounded bg-success/10 px-3 py-1.5 text-xs text-success disabled:opacity-40" disabled={busy} onClick={() => start.mutate(instanceId)} type="button">
          {start.isPending ? "Starting…" : "Start"}
        </button>
      )}
      {status === "RUNNING" && (
        <button className={button} disabled={busy} onClick={() => stop.mutate(instanceId)} type="button">
          {stop.isPending ? "Stopping…" : "Stop"}
        </button>
      )}
      {status === "RUNNING" && (
        <button className={button} disabled={busy} onClick={() => restart.mutate(instanceId)} type="button">
          {restart.isPending ? "Restarting…" : "Restart"}
        </button>
      )}
      {(status === "RUNNING" || status === "STOPPED" || status === "FAILED") && (
        <button
          className="rounded bg-danger/10 px-3 py-1.5 text-xs text-danger disabled:opacity-40"
          disabled={busy}
          onClick={() => {
            if (window.confirm("Delete this instance? Its persistent data will be retained until removal is confirmed in a later release.")) {
              remove.mutate(instanceId);
            }
          }}
          type="button"
        >
          {remove.isPending ? "Deleting…" : "Delete"}
        </button>
      )}
    </div>
  );
}
