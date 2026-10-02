import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import DeleteConfirmModal from "@/components/instance/DeleteConfirmModal";
import { deleteInstance, launchInstance, restartInstance, startInstance, stopInstance } from "@/services/instanceService";

interface InstanceActionsProps {
  instanceId: string;
  status: string;
  instanceName?: string;
  persistent?: boolean;
}

/**
 * Instance lifecycle actions (Sprint 5, VS-035 through VS-038) plus the
 * Launch Desktop button (VS-034) and the delete confirmation workflow
 * with the Retain/Delete data option (Sprint 6, VS-042/VS-043).
 *
 * Start/stop/restart run synchronously; delete is queued asynchronously
 * after confirmation. Launch navigates the current tab: browsers block
 * window.open() called from an async callback (outside the user gesture),
 * so a new tab would silently fail.
 */
export default function InstanceActions({ instanceId, status, instanceName = "this instance", persistent = false }: InstanceActionsProps) {
  const queryClient = useQueryClient();
  const [confirming, setConfirming] = useState(false);
  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["instances"] });
    void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const start = useMutation({ mutationFn: startInstance, onSuccess: invalidate });
  const stop = useMutation({ mutationFn: stopInstance, onSuccess: invalidate });
  const restart = useMutation({ mutationFn: restartInstance, onSuccess: invalidate });
  const remove = useMutation({
    mutationFn: ({ id, deleteData }: { id: string; deleteData: boolean }) => deleteInstance(id, deleteData),
    onSuccess: () => {
      setConfirming(false);
      invalidate();
    },
    onError: () => {
      setConfirming(false);
      invalidate();
    },
  });
  // Launch navigates the current tab: browsers block window.open() called
  // from an async callback (outside the user gesture), so a new tab would
  // silently fail. Same-tab navigation is never blocked.
  const launch = useMutation({
    mutationFn: launchInstance,
    onSuccess: (url) => {
      window.location.href = url;
    },
  });

  const button = "rounded border border-border px-3 py-1.5 text-xs disabled:opacity-40";
  const busy = start.isPending || stop.isPending || restart.isPending || remove.isPending;

  return (
    <div className="flex flex-wrap items-center gap-2">
      {status === "RUNNING" && (
        <span className="flex flex-col items-start">
          <button
            className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white disabled:opacity-40"
            disabled={launch.isPending}
            onClick={() => launch.mutate(instanceId)}
            type="button"
          >
            {launch.isPending ? "Launching…" : "Launch desktop"}
          </button>
          {launch.isError && <span className="text-[10px] text-red-600">Unable to launch.</span>}
        </span>
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
          onClick={() => setConfirming(true)}
          type="button"
        >
          Delete
        </button>
      )}

      {confirming && (
        <DeleteConfirmModal
          instanceName={instanceName}
          persistent={persistent}
          isPending={remove.isPending}
          onCancel={() => setConfirming(false)}
          onConfirm={(deleteData) => remove.mutate({ id: instanceId, deleteData })}
        />
      )}
    </div>
  );
}
