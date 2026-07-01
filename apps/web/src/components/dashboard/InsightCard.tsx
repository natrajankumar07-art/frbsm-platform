import { clsx } from "clsx";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export type TrendDirection = "up" | "down" | "flat";
export type InsightDomain = "liquidity" | "capital" | "funding" | "stress";

interface InsightCardProps {
  domain: InsightDomain;
  title: string;
  value: string;
  unit?: string;
  trend: TrendDirection;
  trendLabel?: string;
  drivers: string[];
  recommendation: string;
  onAskSAM?: () => void;
}

const DOMAIN_STYLES: Record<InsightDomain, { accent: string; bg: string }> = {
  liquidity: { accent: "text-blue-600 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-900/20" },
  capital: { accent: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-900/20" },
  funding: { accent: "text-violet-600 dark:text-violet-400", bg: "bg-violet-50 dark:bg-violet-900/20" },
  stress: { accent: "text-orange-600 dark:text-orange-400", bg: "bg-orange-50 dark:bg-orange-900/20" },
};

const TREND_CONFIG: Record<
  TrendDirection,
  { icon: typeof TrendingUp; color: string }
> = {
  up: { icon: TrendingUp, color: "text-positive dark:text-green-400" },
  down: { icon: TrendingDown, color: "text-critical dark:text-red-400" },
  flat: { icon: Minus, color: "text-text-secondary dark:text-gray-400" },
};

export function InsightCard({
  domain,
  title,
  value,
  unit,
  trend,
  trendLabel,
  drivers,
  recommendation,
  onAskSAM,
}: InsightCardProps) {
  const ds = DOMAIN_STYLES[domain];
  const tc = TREND_CONFIG[trend];
  const TrendIcon = tc.icon;

  return (
    <div
      className="card flex flex-col gap-3 dark:bg-gray-900 dark:border-gray-700"
      data-testid={`insight-card-${domain}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-caption text-text-secondary dark:text-gray-400 uppercase tracking-wide">
            {title}
          </p>
          <div className="flex items-baseline gap-1.5 mt-1">
            <span className={clsx("text-2xl font-bold", ds.accent)}>{value}</span>
            {unit && (
              <span className="text-caption text-text-secondary dark:text-gray-400">{unit}</span>
            )}
          </div>
        </div>
        <div
          className={clsx(
            "flex items-center gap-1 text-caption font-medium",
            tc.color
          )}
        >
          <TrendIcon className="h-4 w-4" />
          {trendLabel && <span>{trendLabel}</span>}
        </div>
      </div>

      {drivers.length > 0 && (
        <div className={clsx("rounded-md px-3 py-2 text-xs", ds.bg)}>
          <p className={clsx("font-semibold mb-1", ds.accent)}>Key Drivers</p>
          <ul className="space-y-0.5 text-text-secondary dark:text-gray-400">
            {drivers.map((d, i) => (
              <li key={i}>· {d}</li>
            ))}
          </ul>
        </div>
      )}

      <p className="text-caption text-text-secondary dark:text-gray-400 italic leading-relaxed">
        {recommendation}
      </p>

      {onAskSAM && (
        <button
          onClick={onAskSAM}
          className="self-start text-xs px-2.5 py-1 rounded-md bg-accent/10 text-accent dark:bg-blue-900/40 dark:text-blue-400 hover:bg-accent/20 dark:hover:bg-blue-800/50 transition-colors font-medium"
        >
          Ask SAM →
        </button>
      )}
    </div>
  );
}
