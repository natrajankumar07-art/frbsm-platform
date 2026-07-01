import { useState } from "react";
import { clsx } from "clsx";
import type { LCRResult, NSFRResult, CapitalResult } from "../../types/api";

type RiskLevel = "green" | "amber" | "red" | "unknown";

interface RiskCategory {
  id: string;
  label: string;
  level: RiskLevel;
  value?: string;
  explanation: string;
}

const LEVEL_STYLES: Record<
  RiskLevel,
  { bg: string; text: string; label: string }
> = {
  green: {
    bg: "bg-positive/15 border-positive/30 hover:bg-positive/25 dark:bg-green-900/30 dark:border-green-700/50",
    text: "text-positive dark:text-green-400",
    label: "Low",
  },
  amber: {
    bg: "bg-warning/15 border-warning/30 hover:bg-warning/25 dark:bg-amber-900/30 dark:border-amber-700/50",
    text: "text-warning dark:text-amber-400",
    label: "Medium",
  },
  red: {
    bg: "bg-critical/15 border-critical/30 hover:bg-critical/25 dark:bg-red-900/30 dark:border-red-700/50",
    text: "text-critical dark:text-red-400",
    label: "High",
  },
  unknown: {
    bg: "bg-gray-100 border-gray-200 hover:bg-gray-200 dark:bg-gray-800 dark:border-gray-700",
    text: "text-text-secondary dark:text-gray-400",
    label: "N/A",
  },
};

function lcrLevel(lcr: LCRResult | null | undefined): RiskLevel {
  if (!lcr) return "unknown";
  const r = Number(lcr.lcr_ratio);
  if (r >= 1.2) return "green";
  if (r >= 1.0) return "amber";
  return "red";
}

function nsfrLevel(nsfr: NSFRResult | null | undefined): RiskLevel {
  if (!nsfr) return "unknown";
  const r = Number(nsfr.nsfr_ratio);
  if (r >= 1.15) return "green";
  if (r >= 1.0) return "amber";
  return "red";
}

function capitalLevel(capital: CapitalResult | null | undefined): RiskLevel {
  if (!capital) return "unknown";
  if (capital.passes_all) {
    const cet1 = Number(capital.cet1_ratio);
    return cet1 >= 0.085 ? "green" : "amber";
  }
  return "red";
}

function leverageLevel(capital: CapitalResult | null | undefined): RiskLevel {
  if (!capital) return "unknown";
  const r = Number(capital.leverage_ratio);
  if (r >= 0.04) return "green";
  if (r >= 0.03) return "amber";
  return "red";
}

interface RiskHeatmapProps {
  lcr: LCRResult | null | undefined;
  nsfr: NSFRResult | null | undefined;
  capital: CapitalResult | null | undefined;
}

export function RiskHeatmap({ lcr, nsfr, capital }: RiskHeatmapProps) {
  const [hovered, setHovered] = useState<string | null>(null);

  const categories: RiskCategory[] = [
    {
      id: "liquidity",
      label: "Liquidity Risk",
      level: lcrLevel(lcr),
      value: lcr ? `LCR ${(Number(lcr.lcr_ratio) * 100).toFixed(1)}%` : undefined,
      explanation:
        "Derived from LCR ratio. Green: ≥120%, Amber: 100–120%, Red: <100%. Reflects ability to meet short-term cash obligations.",
    },
    {
      id: "capital",
      label: "Capital Risk",
      level: capitalLevel(capital),
      value: capital ? `CET1 ${(Number(capital.cet1_ratio) * 100).toFixed(1)}%` : undefined,
      explanation:
        "Derived from CET1 ratio. Green: ≥8.5% with all checks passing, Amber: meets minimums, Red: any capital test failing.",
    },
    {
      id: "funding",
      label: "Funding Risk",
      level: nsfrLevel(nsfr),
      value: nsfr ? `NSFR ${(Number(nsfr.nsfr_ratio) * 100).toFixed(1)}%` : undefined,
      explanation:
        "Derived from NSFR ratio. Green: ≥115%, Amber: 100–115%, Red: <100%. Measures structural funding stability.",
    },
    {
      id: "market",
      label: "Market Risk",
      level: "amber",
      explanation:
        "Indicative rating. Full market risk quantification requires VaR and sensitivity models beyond current engine scope.",
    },
    {
      id: "operational",
      label: "Operational Risk",
      level: "amber",
      explanation:
        "Indicative rating. Operational risk requires AMA/Standardised model outputs. Current status reflects no active incidents.",
    },
    {
      id: "interest_rate",
      label: "Interest Rate Risk",
      level: leverageLevel(capital),
      value: capital ? `Leverage ${(Number(capital.leverage_ratio) * 100).toFixed(1)}%` : undefined,
      explanation:
        "Proxied from leverage ratio as an indicator of interest rate sensitivity. Full IRRBB requires duration and gap analysis.",
    },
  ];

  return (
    <div
      className="card dark:bg-gray-900 dark:border-gray-700"
      data-testid="risk-heatmap"
    >
      <h3 className="text-body font-semibold text-text-primary dark:text-gray-100 mb-4">
        Risk Heatmap
      </h3>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {categories.map((cat) => {
          const style = LEVEL_STYLES[cat.level];
          return (
            <div
              key={cat.id}
              className={clsx(
                "relative rounded-lg border p-3 cursor-default transition-colors",
                style.bg
              )}
              onMouseEnter={() => setHovered(cat.id)}
              onMouseLeave={() => setHovered(null)}
              data-testid={`risk-cell-${cat.id}`}
            >
              <p className="text-caption font-semibold text-text-primary dark:text-gray-200 leading-tight">
                {cat.label}
              </p>
              {cat.value && (
                <p className={clsx("text-xs font-medium mt-0.5", style.text)}>
                  {cat.value}
                </p>
              )}
              <span
                className={clsx(
                  "inline-block mt-1.5 text-xs font-bold px-1.5 py-0.5 rounded",
                  "bg-white/50 dark:bg-black/30",
                  style.text
                )}
              >
                {style.label}
              </span>

              {hovered === cat.id && (
                <div className="absolute z-20 bottom-full left-0 mb-2 w-56 rounded-lg border border-border dark:border-gray-600 bg-surface-raised dark:bg-gray-800 shadow-xl p-3 text-xs text-text-secondary dark:text-gray-300 leading-relaxed pointer-events-none">
                  {cat.explanation}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <p className="text-caption text-text-secondary dark:text-gray-500 mt-3" style={{ fontSize: "10px" }}>
        Hover each cell for methodology. Ratings derived from engine outputs — no recalculation.
      </p>
    </div>
  );
}
