import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import StatusBadge from "@/components/common/StatusBadge";
import { fetchAdminAnalytics, fetchAdminHealth } from "@/services/adminService";

/**
 * Admin dashboard (VS-049, Sprint 8) — the platform overview: system health,
 * user/instance/request statistics, recent activity, and quick links.
 */
export default function AdminDashboardPage() {
  const { data: analytics } = useQuery({ queryKey: ["admin-analytics"], queryFn: fetchAdminAnalytics, refetchInterval: 15000 });
  const { data: health } = useQuery({ queryKey: ["admin-health"], queryFn: fetchAdminHealth, refetchInterval: 15000 });

  return (
    <div className="w-full space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Administration</h1>
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <Link to="/admin/users" className="rounded border border-border px-3 py-1.5">Users</Link>
          <Link to="/admin/instances" className="rounded border border-border px-3 py-1.5">Instances</Link>
          <Link to="/admin/events" className="rounded border border-border px-3 py-1.5">Events</Link>
          <Link to="/admin/requests" className="rounded border border-border px-3 py-1.5">Requests</Link>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-medium text-slate-500">System health</h2>
        {health ? (
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <StatusBadge status={health.status} />
            {Object.entries(health.checks).map(([name, value]) => (
              <span key={name} className="flex items-center gap-1 text-sm text-slate-600 dark:text-slate-300">
                {name}: <StatusBadge status={String(value)} />
              </span>
            ))}
          </div>
        ) : (
          <p className="mt-1 text-sm text-slate-500">Checking…</p>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Users</p>
          <p className="text-2xl font-semibold">{analytics ? `${analytics.users.total} (${analytics.users.active} active)` : "—"}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Instances</p>
          <p className="text-2xl font-semibold">
            {analytics ? `${analytics.instances.running} running / ${analytics.instances.total}` : "—"}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Failed instances</p>
          <p className="text-2xl font-semibold">{analytics?.instances.failed ?? "—"}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-slate-500">Pending requests</p>
          <p className="text-2xl font-semibold">{analytics?.software_requests.pending ?? "—"}</p>
        </div>
      </div>

      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Recent platform activity</h2>
        {analytics && analytics.recent_events.length === 0 && <p className="text-sm text-slate-500">No activity yet.</p>}
        <ul className="space-y-1">
          {analytics?.recent_events.map((event, index) => (
            <li className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300" key={index}>
              <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs dark:bg-slate-800">{event.event_type}</span>
              {event.message}
              {event.actor && <span className="text-xs text-slate-400">by {event.actor}</span>}
              <span className="text-xs text-slate-400">{new Date(event.created_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
