import { clsx } from "clsx";

type Variant = "default" | "positive" | "warning" | "critical" | "accent";

const VARIANTS: Record<Variant, string> = {
  default: "bg-border text-text-secondary",
  positive: "bg-green-100 text-positive",
  warning: "bg-orange-100 text-warning",
  critical: "bg-red-100 text-critical",
  accent: "bg-blue-100 text-accent",
};

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: Variant;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2 py-0.5 text-caption font-medium",
        VARIANTS[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
