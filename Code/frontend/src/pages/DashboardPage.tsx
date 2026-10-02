import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import InstanceActions from "@/components/instance/InstanceActions";
import StatusBadge from "@/components/common/StatusBadge";
import { useAuth } from "@/contexts/AuthContext";
import { fetchDashboard } from "@/services/dashboardService";
import { fetchInstances } from "@/services/instanceService";

/**
 * User Dashboard (VS-030 through VS-034, Sprint 4).
 *
 * Sections per 09_User_Experience.md Section 4: welcome message, active
 * instances, stopped instances, recent activity, resource usage summary,
 * and quick actions. Replaces the M1 placeholder.
 */
export default function DashboardPage() {
  const { user } = useAuth();
  const { data: stats } = useQuery({ queryKey: ["dashboard"], queryFn: fetchDashboard });
  const { data: instances = [] } = useQuery({ queryKey: ["instances"], queryFn: fetchInstances });

  const running = instances.filter((instance) => instance.status === "RUNNING");
  const stopped = instances.filter((instance) => instance.status === "STOPPED");

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Welcome back{user ? `, ${user.username}` : ""}</h1>
        <div className="flex items-center gap-2 text-sm">
          <Link to="/instances/new" className="rounded bg-blue-600 px-3 py-1.5 text-white">New instance</Link>
          <Link to="/templates" className="rounded border border-border px-3 py-1.5">Templates</Link>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Running</p>
          <p className="text-2xl font-semibold">{stats?.instances.running ?? "—"}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Stopped</p>
          <p className="text-2xl font-semibold">{stats?.instances.stopped ?? "—"}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Failed</p>
          <p className="text-2xl font-semibold">{stats?.instances.failed ?? "—"}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Total</p>
          <p className="text-2xl font-semibold">{stats?.instances.total ?? "—"}</p>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-medium text-slate-500">Resource usage (running instances)</h2>
        {stats ? (
          <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">
            {stats.usage.cpu_cores} CPU cores · {stats.usage.memory_gb} GB memory in use
          </p>
        ) : (
          <p className="mt-1 text-sm text-slate-500">Loading…</p>
        )}
      </div>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Active instances</h2>
        {running.length === 0 && <p className="text-sm text-slate-500">No running instances.</p>}
        <div className="grid gap-3 md:grid-cols-2">
          {running.map((instance) => (
            <article className="rounded-lg border border-border bg-white p-4 shadow-sm dark:bg-slate-900" key={instance.id}>
              <div className="flex items-center justify-between">
                <strong>{instance.name}</strong>
                <StatusBadge status={instance.status} />
              </div>
              <p className="mt-1 text-sm text-slate-500">
                {instance.template_name} · {instance.cpu_limit} CPU · {instance.memory_limit}
              </p>
              {instance.subdomain && <p className="mt-1 text-xs text-slate-400">{instance.subdomain}</p>}
              <div className="mt-3">
                <InstanceActions instanceId={instance.id} status={instance.status} instanceName={instance.name} persistent={instance.persistent} />
              </div>
            </article>
          ))}
        </div>
      </div>

      {stopped.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Stopped instances</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {stopped.map((instance) => (
              <article className="rounded-lg border border-border bg-white p-4 shadow-sm dark:bg-slate-900" key={instance.id}>
                <div className="flex items-center justify-between">
                  <strong>{instance.name}</strong>
                  <StatusBadge status={instance.status} />
                </div>
                <p className="mt-1 text-sm text-slate-500">{instance.template_name}</p>
              </article>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Recent activity</h2>
        {stats && stats.recent_activity.length === 0 && (
          <p className="text-sm text-slate-500">No activity yet.</p>
        )}
        <ul className="space-y-1">
          {stats?.recent_activity.map((event, index) => (
            <li className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300" key={index}>
              <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs dark:bg-slate-800">{event.event_type}</span>
              {event.message}
              <span className="text-xs text-slate-400">{new Date(event.created_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
