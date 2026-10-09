import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import InstanceActions from "@/components/instance/InstanceActions";
import StatusBadge from "@/components/common/StatusBadge";
import { fetchAdminInstances } from "@/services/adminService";

const STATUSES = ["", "RUNNING", "STOPPED", "FAILED", "PROVISIONING", "DELETED"];

/**
 * Instance management (VS-051, Sprint 8) — all users' instances with
 * filters; admins can start/stop/restart/delete any instance.
 */
export default function AdminInstancesPage() {
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["admin-instances", status, search],
    queryFn: () => fetchAdminInstances({ status: status || undefined, search: search || undefined }),
    refetchInterval: 10000,
  });

  return (
    <div className="w-full max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">Instances</h1>
      <div className="flex flex-wrap items-center gap-2">
        <input
          className="flex-1 rounded border p-2 text-sm"
          placeholder="Search by name or username…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <select className="rounded border p-2 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
          {STATUSES.map((value) => (
            <option key={value} value={value}>{value || "All statuses"}</option>
          ))}
        </select>
      </div>
      {isLoading && <p className="text-sm text-slate-500">Loading instances…</p>}
      <div className="space-y-2">
        {data?.instances.map((instance) => (
          <article className="rounded-lg border border-border bg-white p-4 dark:bg-slate-900" key={instance.id}>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <strong>{instance.name}</strong>
                <p className="text-sm text-slate-500">by {instance.username} · {instance.template_name} · {instance.cpu_limit} CPU · {instance.memory_limit}</p>
              </div>
              <StatusBadge status={instance.status} />
            </div>
            {instance.error_message && <p className="mt-1 text-sm text-red-600">{instance.error_message}</p>}
            <div className="mt-3">
              <InstanceActions instanceId={instance.id} status={instance.status} instanceName={instance.name} />
            </div>
          </article>
        ))}
        {data && data.instances.length === 0 && <p className="text-sm text-slate-500">No instances match.</p>}
      </div>
      {data && data.pagination.pages > 1 && (
        <p className="text-sm text-slate-500">Page {data.pagination.page} of {data.pagination.pages} ({data.pagination.total} instances)</p>
      )}
    </div>
  );
}
