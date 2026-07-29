import { useHealthCheck } from "@/hooks/useHealthCheck";
import StatusBadge from "@/components/common/StatusBadge";

/**
 * Placeholder dashboard.
 *
 * Renders the platform health check so M1's acceptance criteria
 * ("backend and frontend communicate") is visibly demonstrable. The real
 * dashboard (running/stopped instances, recent activity, quick actions)
 * arrives in Sprint 4 per 09_User_Experience.md Section 4.
 */
export default function DashboardPage() {
  const { data, isLoading, isError } = useHealthCheck();

  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-2xl font-semibold">Welcome</h1>

      <div className="rounded-md border border-border bg-surface p-4 shadow-sm">
        <h2 className="text-sm font-medium text-slate-500 mb-2">
          Platform Status
        </h2>

        {isLoading && <p className="text-sm text-slate-500">Checking…</p>}

        {isError && <StatusBadge status="critical" />}

        {data && (
          <div className="space-y-2">
            <StatusBadge status={data.data.status} />
            <ul className="text-sm text-slate-600 mt-2 space-y-1">
              {Object.entries(data.data.checks).map(([name, value]) => (
                <li key={name} className="flex justify-between">
                  <span className="capitalize">{name}</span>
                  <StatusBadge status={value} />
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
