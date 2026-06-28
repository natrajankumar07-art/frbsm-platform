import { clsx } from "clsx";

interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  status?: "positive" | "warning" | "critical" | "neutral";
  className?: string;
}

const STATUS_COLORS = {
  positive: "text-positive",
  warning: "text-warning",
  critical: "text-critical",
  neutral: "text-text-primary",
};

export function MetricCard({
  label,
  value,
  sub,
  status = "neutral",
  className,
}: MetricCardProps) {
  return (
    <div className={clsx("card flex flex-col gap-1", className)}>
      <p className="text-caption text-text-secondary uppercase tracking-wide">{label}</p>
      <p className={clsx("text-display font-semibold", STATUS_COLORS[status])}>{value}</p>
      {sub && <p className="text-caption text-text-secondary">{sub}</p>}
    </div>
  );
}
