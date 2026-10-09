import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { fetchAdminEvents } from "@/services/adminService";

const EVENT_TYPES = [
  "", "USER_REGISTERED", "USER_LOGGED_IN", "USER_LOGGED_OUT", "USER_LOGIN_FAILED",
  "PASSWORD_RESET_REQUESTED", "PASSWORD_RESET_COMPLETED",
  "TEMPLATE_CREATED", "TEMPLATE_UPDATED", "TEMPLATE_ARCHIVED",
  "INSTANCE_REQUESTED", "INSTANCE_PROVISIONED", "INSTANCE_PROVISION_FAILED",
  "INSTANCE_LAUNCHED", "INSTANCE_STARTED", "INSTANCE_STOPPED", "INSTANCE_RESTARTED",
  "INSTANCE_DELETE_REQUESTED", "INSTANCE_DELETED",
  "SOFTWARE_REQUESTED", "SOFTWARE_REQUEST_APPROVED", "SOFTWARE_REQUEST_REJECTED",
  "SOFTWARE_INSTALLED", "SOFTWARE_INSTALL_FAILED",
];

/**
 * Event log viewer (VS-052, Sprint 8) — the platform event history with
 * type/search filters and pagination.
 */
export default function AdminEventsPage() {
  const [eventType, setEventType] = useState("");
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["admin-events", eventType, search],
    queryFn: () => fetchAdminEvents({ eventType: eventType || undefined, search: search || undefined }),
    refetchInterval: 10000,
  });

  return (
    <div className="w-full max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">Event log</h1>
      <div className="flex flex-wrap items-center gap-2">
        <input
          className="flex-1 rounded border p-2 text-sm"
          placeholder="Search events…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <select className="rounded border p-2 text-sm" value={eventType} onChange={(event) => setEventType(event.target.value)}>
          {EVENT_TYPES.map((value) => (
            <option key={value} value={value}>{value || "All types"}</option>
          ))}
        </select>
      </div>
      {isLoading && <p className="text-sm text-slate-500">Loading events…</p>}
      <div className="space-y-1">
        {data?.events.map((event) => (
          <div className="flex flex-wrap items-center gap-2 rounded border border-border bg-white p-2 text-sm dark:bg-slate-900" key={event.id}>
            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs dark:bg-slate-800">{event.event_type}</span>
            <span className="text-slate-600 dark:text-slate-300">{event.message}</span>
            {event.actor_name && <span className="text-xs text-slate-400">by {event.actor_name}</span>}
            <span className="ml-auto text-xs text-slate-400">{new Date(event.created_at).toLocaleString()}</span>
          </div>
        ))}
        {data && data.events.length === 0 && <p className="text-sm text-slate-500">No events match.</p>}
      </div>
      {data && data.pagination.pages > 1 && (
        <p className="text-sm text-slate-500">Page {data.pagination.page} of {data.pagination.pages} ({data.pagination.total} events)</p>
      )}
    </div>
  );
}
