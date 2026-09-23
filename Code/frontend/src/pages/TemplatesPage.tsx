import { useQuery } from "@tanstack/react-query";
import { fetchTemplates } from "@/services/templateService";

export default function TemplatesPage() {
  const { data = [], isLoading, isError } = useQuery({ queryKey: ["templates"], queryFn: fetchTemplates });
  return <section className="w-full space-y-4"><h1 className="text-2xl font-semibold">Choose a desktop template</h1><p className="text-slate-500">Your selected template will be used when provisioning a desktop.</p>{isLoading && <p>Loading templates…</p>}{isError && <p className="text-red-600">Unable to load templates.</p>}<div className="grid gap-4 md:grid-cols-2">{data.map((template) => <article key={template.id} className="rounded-lg border bg-white p-5 shadow-sm"><h2 className="font-semibold">{template.name}</h2><p className="mt-2 text-sm text-slate-600">{template.description || "No description available."}</p><p className="mt-3 text-xs text-slate-500">Image: {template.json_configuration.image}</p></article>)}</div>{!isLoading && !isError && data.length === 0 && <p>No desktop templates are currently available.</p>}</section>;
}
