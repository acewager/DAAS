interface UsageBarProps {
  label: string;
  percent: number;
  detail?: string;
}

/**
 * Usage bar (VS-056, Sprint 9) — a dependency-free CSS chart for per-instance
 * usage (09_User_Experience.md Section 9: CPU/memory widgets). Percent is
 * clamped and NaN-safe (missing analytics render as 0).
 */
export default function UsageBar({ label, percent, detail }: UsageBarProps) {
  const clamped = Math.max(0, Math.min(100, Number.isFinite(percent) ? percent : 0));
  const color = clamped > 80 ? "bg-danger" : clamped > 50 ? "bg-warning" : "bg-success";
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>{label}</span>
        <span>{detail ?? `${clamped.toFixed(0)}%`}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${clamped}%` }} />
      </div>
    </div>
  );
}
