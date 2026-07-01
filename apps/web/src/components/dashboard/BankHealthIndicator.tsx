import { clsx } from "clsx";

export type BankHealth = "healthy" | "warning" | "critical";

interface BankHealthIndicatorProps {
  health: BankHealth;
  passCount: number;
  totalChecks: number;
  className?: string;
}

const CONFIG: Record<
  BankHealth,
  { label: string; icon: string; textColor: string; bg: string; border: string; ringColor: string }
> = {
  healthy: {
    label: "Healthy",
    icon: "✓",
    textColor: "text-positive dark:text-green-400",
    bg: "bg-positive/10 dark:bg-green-900/30",
    border: "border-positive/30 dark:border-green-700/50",
    ringColor: "ring-positive/20",
  },
  warning: {
    label: "Warning",
    icon: "⚠",
    textColor: "text-warning dark:text-amber-400",
    bg: "bg-warning/10 dark:bg-amber-900/30",
    border: "border-warning/30 dark:border-amber-700/50",
    ringColor: "ring-warning/20",
  },
  critical: {
    label: "Critical",
    icon: "✕",
    textColor: "text-critical dark:text-red-400",
    bg: "bg-critical/10 dark:bg-red-900/30",
    border: "border-critical/30 dark:border-red-700/50",
    ringColor: "ring-critical/20",
  },
};

export function BankHealthIndicator({
  health,
  passCount,
  totalChecks,
  className,
}: BankHealthIndicatorProps) {
  const cfg = CONFIG[health];
  return (
    <div
      className={clsx(
        "card flex flex-col items-center justify-center gap-2 py-6 border-2",
        cfg.bg,
        cfg.border,
        className
      )}
      data-testid="bank-health-indicator"
    >
      <div
        className={clsx(
          "h-14 w-14 rounded-full flex items-center justify-center text-2xl font-bold border-2 ring-4",
          cfg.bg,
          cfg.border,
          cfg.ringColor,
          cfg.textColor
        )}
      >
        {cfg.icon}
      </div>
      <div className="text-center">
        <p className="text-caption text-text-secondary dark:text-gray-400 uppercase tracking-wide">
          Bank Health
        </p>
        <p className={clsx("text-xl font-bold mt-0.5", cfg.textColor)}>
          {cfg.label}
        </p>
        <p className="text-caption text-text-secondary dark:text-gray-400 mt-1">
          {passCount}/{totalChecks} checks passing
        </p>
      </div>
    </div>
  );
}
