import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { approveSoftwareRequest, fetchSoftwareRequests, rejectSoftwareRequest } from "@/services/softwareRequestService";
import type { SoftwareRequest } from "@/services/softwareRequestService";

/**
 * Admin approval page (VS-046, Sprint 7) — pending software requests with
 * Approve/Reject actions. Rejecting requires confirmation
 * (09_User_Experience.md Section 12).
 */
export default function AdminRequestsPage() {
  const queryClient = useQueryClient();
  const [rejecting, setRejecting] = useState<SoftwareRequest | null>(null);
  const { data: requests = [], isLoading } = useQuery({
    queryKey: ["admin-requests"],
    queryFn: () => fetchSoftwareRequests("PENDING"),
    refetchInterval: 10000,
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["admin-requests"] });
    void queryClient.invalidateQueries({ queryKey: ["software-requests"] });
  };
  const approve = useMutation({ mutationFn: approveSoftwareRequest, onSuccess: invalidate });
  const reject = useMutation({ mutationFn: rejectSoftwareRequest, onSuccess: () => { setRejecting(null); invalidate(); } });

  return (
    <div className="w-full max-w-2xl space-y-4">
      <h1 className="text-2xl font-semibold">Software request approvals</h1>

      {isLoading && <p className="text-sm text-slate-500">Loading pending requests…</p>}
      {!isLoading && requests.length === 0 && <p className="text-sm text-slate-500">No pending requests.</p>}

      <div className="space-y-2">
        {requests.map((request) => (
          <article className="rounded-lg border border-border bg-white p-4 dark:bg-slate-900" key={request.id}>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <strong>{request.software_name}</strong>
                <p className="text-sm text-slate-500">{request.instance_name} · requested by {request.reviewer_name || "a user"}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  className="rounded bg-green-600 px-3 py-1.5 text-xs text-white disabled:opacity-40"
                  disabled={approve.isPending}
                  onClick={() => approve.mutate(request.id)}
                  type="button"
                >
                  {approve.isPending ? "Approving…" : "Approve"}
                </button>
                <button
                  className="rounded bg-danger/10 px-3 py-1.5 text-xs text-danger disabled:opacity-40"
                  disabled={reject.isPending}
                  onClick={() => setRejecting(request)}
                  type="button"
                >
                  Reject
                </button>
              </div>
            </div>
            {request.justification && (
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">Justification: {request.justification}</p>
            )}
          </article>
        ))}
      </div>

      {rejecting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true" aria-label="Reject request">
          <div className="w-full max-w-md space-y-4 rounded-lg border border-border bg-white p-5 shadow-xl dark:bg-slate-900">
            <div className="space-y-1">
              <h2 className="text-lg font-semibold">Reject request</h2>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                Reject the request for <strong>{rejecting.software_name}</strong>? The user will see it as rejected. This cannot be undone.
              </p>
            </div>
            <div className="flex items-center justify-end gap-2">
              <button className="rounded border border-border px-4 py-2 text-sm" onClick={() => setRejecting(null)} disabled={reject.isPending} type="button">Cancel</button>
              <button className="rounded bg-red-600 px-4 py-2 text-sm text-white disabled:opacity-50" onClick={() => reject.mutate(rejecting.id)} disabled={reject.isPending} type="button">
                {reject.isPending ? "Rejecting…" : "Reject request"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
