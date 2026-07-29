interface StatusBadgeProps {
  status: "healthy" | "warning" | "critical" | string;
}

const STYLES: Record<string, string> = {
  healthy: "bg-success/10 text-success",
  warning: "bg-warning/10 text-warning",
  critical: "bg-danger/10 text-danger",
};

// Reusable status indicator per 08_Frontend_Architecture.md Section 10
// (Instance Components -> StatusIndicator) and 19_UI_Design_System.md.
export default function StatusBadge({ status }: StatusBadgeProps) {
  const style = STYLES[status] ?? "bg-slate-200 text-slate-700";
  return (
    <span
      className={`inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium capitalize ${style}`}
    >
      {status}
    </span>
  );
}
