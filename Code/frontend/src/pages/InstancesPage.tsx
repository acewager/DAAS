import { useQuery } from "@tanstack/react-query";

import LaunchButton from "@/components/instance/LaunchButton";
import { fetchInstances } from "@/services/instanceService";

/**
 * Instance list with provisioning progress (VS-029) and Launch Desktop
 * buttons (VS-034).
 */
export default function InstancesPage() {
  const { data = [], isLoading } = useQuery({ queryKey: ["instances"], queryFn: fetchInstances, refetchInterval: 5000 });

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
                {instance.template_name} · {instance.cpu_limit} CPU · {instance.memory_limit}
              </p>
              {instance.subdomain && <p className="text-xs text-slate-400">{instance.subdomain}</p>}
              {instance.error_message && <p className="text-sm text-red-600">{instance.error_message}</p>}
              <div className="mt-3">
                <LaunchButton instanceId={instance.id} status={instance.status} />
              </div>
            </article>
          ))}
          {data.length === 0 && <p>No instances have been requested.</p>}
        </div>
      )}
    </section>
  );
}
