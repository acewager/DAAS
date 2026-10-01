import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import { createInstance } from "@/services/instanceService";
import { fetchTemplates } from "@/services/templateService";

interface FormValues {
  name: string;
  templateId: string;
  cpuLimit: string;
  memoryLimit: string;
  persistent: boolean;
  autoStopMinutes: number;
}

/**
 * Order Instance form (VS-029, Sprint 3).
 *
 * Mirrors the Order Instance Wizard steps from 09_User_Experience.md
 * Section 5 (Template → Instance Settings → Resource Selection) as a single
 * page. Frontend validation gives immediate feedback; the backend remains
 * the validation authority.
 */
export default function NewInstancePage() {
  const navigate = useNavigate();
  const { data: templates = [], isLoading: templatesLoading } = useQuery({
    queryKey: ["templates"],
    queryFn: fetchTemplates,
  });
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    defaultValues: { name: "", templateId: "", cpuLimit: "2.00", memoryLimit: "2G", persistent: false, autoStopMinutes: 60 },
  });
  const mutation = useMutation({
    mutationFn: createInstance,
    onSuccess: () => navigate("/instances"),
  });

  const selectedTemplate = templates.find((template) => template.id === watch("templateId"));
  const persistenceAvailable = selectedTemplate?.json_configuration.persistent_supported ?? true;

  return (
    <div className="max-w-md space-y-4">
      <h1 className="text-2xl font-semibold">New instance</h1>
      <form className="space-y-4" onSubmit={handleSubmit((values) => mutation.mutate(values))}>
        <fieldset className="space-y-2 rounded-lg border border-border bg-surface p-4">
          <legend className="px-1 text-sm font-medium">Template</legend>
          {templatesLoading && <p className="text-sm text-slate-500">Loading templates…</p>}
          <select
            className="w-full rounded border p-2"
            defaultValue=""
            {...register("templateId", { required: "Choose a template" })}
          >
            <option value="" disabled>
              Choose a template…
            </option>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
          {selectedTemplate && (
            <p className="text-xs text-slate-500">
              Image: {selectedTemplate.json_configuration.image}
            </p>
          )}
          {errors.templateId && <p className="text-sm text-red-600">{errors.templateId.message}</p>}
        </fieldset>

        <fieldset className="space-y-2 rounded-lg border border-border bg-surface p-4">
          <legend className="px-1 text-sm font-medium">Instance settings</legend>
          <label className="block text-sm">
            Instance name
            <input
              className="mt-1 w-full rounded border p-2"
              placeholder="My desktop"
              {...register("name", { required: "Instance name is required" })}
            />
          </label>
          {errors.name && <p className="text-sm text-red-600">{errors.name.message}</p>}
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" {...register("persistent")} disabled={!persistenceAvailable} />
            Persistent storage
            {!persistenceAvailable && <span className="text-xs text-slate-500">(not supported by this template)</span>}
          </label>
          <label className="block text-sm">
            Auto-stop timeout (minutes)
            <input
              type="number"
              min={5}
              className="mt-1 w-full rounded border p-2"
              {...register("autoStopMinutes", { valueAsNumber: true, min: { value: 5, message: "Minimum is 5 minutes" } })}
            />
          </label>
          {errors.autoStopMinutes && <p className="text-sm text-red-600">{errors.autoStopMinutes.message}</p>}
        </fieldset>

        <fieldset className="space-y-2 rounded-lg border border-border bg-surface p-4">
          <legend className="px-1 text-sm font-medium">Resources</legend>
          <label className="block text-sm">
            CPU cores
            <select className="mt-1 w-full rounded border p-2" {...register("cpuLimit")}>
              <option value="1.00">1</option>
              <option value="2.00">2</option>
              <option value="4.00">4</option>
            </select>
          </label>
          <label className="block text-sm">
            Memory
            <select className="mt-1 w-full rounded border p-2" {...register("memoryLimit")}>
              <option value="2G">2 GB</option>
              <option value="4G">4 GB</option>
              <option value="8G">8 GB</option>
            </select>
          </label>
        </fieldset>

        {mutation.isError && (
          <p className="text-sm text-red-600">Unable to create the instance. Please try again.</p>
        )}
        <button
          className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
          disabled={mutation.isPending}
          type="submit"
        >
          {mutation.isPending ? "Requesting…" : "Create instance"}
        </button>
      </form>
    </div>
  );
}
