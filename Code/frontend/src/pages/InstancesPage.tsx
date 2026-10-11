import { useQuery } from "@tanstack/react-query";

import InstanceActions from "@/components/instance/InstanceActions";
import UsageBar from "@/components/instance/UsageBar";
import { fetchInstances } from "@/services/instanceService";

/**
 * Instance list with provisioning progress (VS-029), Launch Desktop
 * buttons (VS-034), and usage charts (VS-056).
 */
export default function InstancesPage() {
  const { data = [], isLoading } = useQuery({ queryKey: ["instances"], queryFn: fetchInstances, refetchInterval: 5000 });

  // Null-safe: missing analytics fields arrive as null.
  const cpuPercent = (instance: { cpu_average: number; cpu_limit: string }) => {
    const cores = parseFloat(instance.cpu_limit) || 1;
    const average = instance.cpu_average ?? 0;
    return (average / cores) * 100;
  };
  const ramPercent = (instance: { ram_average: number; memory_limit: string }) => {
    const match = instance.memory_limit.match(/^(\d+)G$/);
    const gb = match ? Number(match[1]) : 2;
    const average = instance.ram_average ?? 0;
    return (average / (gb * 1024)) * 100;
  };
  const uptime = (seconds: number) => {
    if (!seconds) return "—";
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
  };

  return (
    <section className="w-full space-y-4">
      <h1 className="text-2xl font-semibold">Provisioning progress</h1>
      {isLoading ? (
        <p>Loading instances…</p>
      ) : (
        <div className="grid gap-3">
          {data.map((instance) => (
            <article className="rounded border border-border bg-white p-4 dark:bg-slate-900" key={instance.id}>
              <div className="flex justify-between">
                <strong>{instance.name}</strong>
                <span>{instance.status}</span>
              </div>
              <p className="text-sm text-slate-500">
                {instance.template_name} · {instance.cpu_limit} CPU · {instance.memory_limit} · up {uptime(instance.uptime_seconds)}
              </p>
              {instance.subdomain && <p className="text-xs text-slate-400">{instance.subdomain}</p>}
              {instance.status === "RUNNING" && (
                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  <UsageBar label="CPU" percent={cpuPercent(instance)} detail={`${(instance.cpu_average ?? 0).toFixed(1)}% of ${instance.cpu_limit} cores`} />
                  <UsageBar label="Memory" percent={ramPercent(instance)} detail={`${(instance.ram_average ?? 0).toFixed(0)} MB of ${instance.memory_limit}`} />
                </div>
              )}
              {instance.error_message && <p className="text-sm text-red-600">{instance.error_message}</p>}
              <div className="mt-3">
                <InstanceActions instanceId={instance.id} status={instance.status} instanceName={instance.name} persistent={instance.persistent} />
              </div>
            </article>
          ))}
          {data.length === 0 && <p>No instances have been requested.</p>}
        </div>
      )}
    </section>
  );
}
