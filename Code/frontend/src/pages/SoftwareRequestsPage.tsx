import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { fetchInstances } from "@/services/instanceService";
import { fetchSoftwareRequests, submitSoftwareRequest } from "@/services/softwareRequestService";

interface RequestFormValues {
  instanceId: string;
  softwareName: string;
  justification: string;
}

const STATUS_STYLES: Record<string, string> = {
  PENDING: "bg-amber-100 text-amber-800",
  APPROVED: "bg-blue-100 text-blue-800",
  REJECTED: "bg-red-100 text-red-700",
  INSTALLING: "bg-indigo-100 text-indigo-800",
  INSTALLED: "bg-green-100 text-green-700",
  FAILED: "bg-red-100 text-red-700",
};

/**
 * Software Requests page (VS-045, Sprint 7) — the user's request history and
 * the New Request form, per 09_User_Experience.md Section 8.
 */
export default function SoftwareRequestsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const { data: requests = [], isLoading } = useQuery({
    queryKey: ["software-requests"],
    queryFn: () => fetchSoftwareRequests(),
    refetchInterval: 10000,
  });
  const { data: instances = [] } = useQuery({ queryKey: ["instances"], queryFn: fetchInstances });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<RequestFormValues>({
    defaultValues: { instanceId: "", softwareName: "", justification: "" },
  });
  const mutation = useMutation({
    mutationFn: submitSoftwareRequest,
    onSuccess: () => {
      reset();
      setShowForm(false);
      void queryClient.invalidateQueries({ queryKey: ["software-requests"] });
    },
  });

  const usableInstances = instances.filter((instance) => instance.status === "RUNNING");

  return (
    <div className="w-full max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Software requests</h1>
        <button
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white"
          onClick={() => setShowForm((value) => !value)}
          type="button"
        >
          {showForm ? "Close" : "New request"}
        </button>
      </div>

      {showForm && (
        <form className="space-y-3 rounded-lg border border-border bg-surface p-4" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
          <label className="block text-sm">
            Instance
            <select className="mt-1 w-full rounded border p-2" defaultValue="" {...register("instanceId", { required: "Choose an instance" })}>
              <option value="" disabled>Choose a running instance…</option>
              {usableInstances.map((instance) => (
                <option key={instance.id} value={instance.id}>{instance.name}</option>
              ))}
            </select>
          </label>
          {errors.instanceId && <p className="text-sm text-red-600">{errors.instanceId.message}</p>}
          {usableInstances.length === 0 && (
            <p className="text-xs text-slate-500">No running instances — start one first; software is installed into running desktops.</p>
          )}
          <label className="block text-sm">
            Software name
            <input
              className="mt-1 w-full rounded border p-2"
              placeholder="e.g. htop"
              {...register("softwareName", {
                required: "Software name is required",
                pattern: { value: /^[A-Za-z0-9][A-Za-z0-9+._-]*$/, message: "Package names use letters, numbers and . _ + - only" },
              })}
            />
          </label>
          {errors.softwareName && <p className="text-sm text-red-600">{errors.softwareName.message}</p>}
          <label className="block text-sm">
            Justification (optional)
            <textarea className="mt-1 w-full rounded border p-2" rows={3} {...register("justification")} />
          </label>
          {mutation.isError && <p className="text-sm text-red-600">Unable to submit the request. Please try again.</p>}
          <button className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50" disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Submitting…" : "Submit request"}
          </button>
        </form>
      )}

      <div className="space-y-2">
        {isLoading && <p className="text-sm text-slate-500">Loading requests…</p>}
        {!isLoading && requests.length === 0 && <p className="text-sm text-slate-500">No software requests yet.</p>}
        {requests.map((request) => (
          <article className="rounded-lg border border-border bg-white p-4 dark:bg-slate-900" key={request.id}>
            <div className="flex items-center justify-between">
              <strong>{request.software_name}</strong>
              <span className={`rounded px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[request.status] ?? "bg-slate-200 text-slate-700"}`}>{request.status}</span>
            </div>
            <p className="mt-1 text-sm text-slate-500">{request.instance_name} · {new Date(request.created_at).toLocaleString()}</p>
            {request.justification && <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{request.justification}</p>}
            {request.status === "FAILED" && request.failure_reason && (
              <p className="mt-1 rounded bg-red-50 p-2 text-xs text-red-700 dark:bg-red-950 dark:text-red-300">
                Installation failed: {request.failure_reason}
              </p>
            )}
            {request.reviewer_name && (
              <p className="mt-1 text-xs text-slate-400">Reviewed by {request.reviewer_name}</p>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
