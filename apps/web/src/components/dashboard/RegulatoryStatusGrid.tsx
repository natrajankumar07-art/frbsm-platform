import { clsx } from "clsx";
import { AskSAMButton } from "./AskSAMButton";
import type { LCRResult, NSFRResult, CapitalResult } from "../../types/api";

interface MetricItem {
  id: string;
  label: string;
  value: string;
  minimum: string;
  passes: boolean;
  askContext: string;
}

interface RegulatoryStatusGridProps {
  lcr: LCRResult | null | undefined;
  nsfr: NSFRResult | null | undefined;
  capital: CapitalResult | null | undefined;
}

const pct = (v: string | number | undefined) =>
  v !== undefined ? `${(Number(v) * 100).toFixed(2)}%` : "—";

function buildMetrics(
  lcr: LCRResult | null | undefined,
  nsfr: NSFRResult | null | undefined,
  capital: CapitalResult | null | undefined
): MetricItem[] {
  return [
    {
      id: "lcr",
      label: "LCR",
      value: lcr ? pct(lcr.lcr_ratio) : "—",
      minimum: lcr ? pct(lcr.minimum_ratio) : "100%",
      passes: lcr?.passes ?? false,
      askContext: "Explain the current LCR ratio, HQLA composition, and whether we meet the minimum regulatory requirement.",
    },
    {
      id: "nsfr",
      label: "NSFR",
      value: nsfr ? pct(nsfr.nsfr_ratio) : "—",
      minimum: nsfr ? pct(nsfr.minimum_ratio) : "100%",
      passes: nsfr?.passes ?? false,
      askContext: "Explain the current NSFR ratio, available versus required stable funding, and regulatory compliance status.",
    },
    {
      id: "cet1",
      label: "CET1",
      value: capital ? pct(capital.cet1_ratio) : "—",
      minimum: "4.50%",
      passes: capital ? Number(capital.cet1_ratio) >= 0.045 : false,
      askContext: "Explain the CET1 capital ratio, the composition of CET1 capital, and whether it meets Basel III requirements.",
    },
    {
      id: "tier1",
      label: "Tier 1",
      value: capital ? pct(capital.tier1_ratio) : "—",
      minimum: "6.00%",
      passes: capital ? Number(capital.tier1_ratio) >= 0.06 : false,
      askContext: "Explain the Tier 1 capital ratio including additional Tier 1 instruments and regulatory minimum compliance.",
    },
    {
      id: "tcr",
      label: "Total Capital",
      value: capital ? pct(capital.total_capital_ratio) : "—",
      minimum: "8.00%",
      passes: capital ? Number(capital.total_capital_ratio) >= 0.08 : false,
      askContext: "Explain the total capital adequacy ratio including Tier 2 capital and the overall Basel III capital stack.",
    },
    {
      id: "leverage",
      label: "Leverage",
      value: capital ? pct(capital.leverage_ratio) : "—",
      minimum: "3.00%",
      passes: capital ? Number(capital.leverage_ratio) >= 0.03 : false,
      askContext: "Explain the Basel III leverage ratio, how it is calculated from total exposures, and regulatory compliance.",
    },
  ];
}

export function RegulatoryStatusGrid({
  lcr,
  nsfr,
  capital,
}: RegulatoryStatusGridProps) {
  const metrics = buildMetrics(lcr, nsfr, capital);

  return (
    <div
      className="card dark:bg-gray-900 dark:border-gray-700"
      data-testid="regulatory-status-grid"
    >
      <h3 className="text-body font-semibold text-text-primary dark:text-gray-100 mb-4">
        Regulatory Status
      </h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {metrics.map((m) => (
          <div
            key={m.id}
            className={clsx(
              "rounded-lg border p-3 flex flex-col gap-2 transition-shadow hover:shadow-md",
              m.passes
                ? "border-positive/30 bg-positive/5 dark:border-green-700/40 dark:bg-green-900/10"
                : m.value === "—"
                ? "border-border dark:border-gray-700 bg-surface dark:bg-gray-800"
                : "border-critical/30 bg-critical/5 dark:border-red-700/40 dark:bg-red-900/10"
            )}
          >
            <div className="flex items-center justify-between">
              <span className="text-caption font-semibold text-text-secondary dark:text-gray-400 uppercase tracking-wide">
                {m.label}
              </span>
              {m.value !== "—" && (
                <span
                  className={clsx(
                    "text-caption font-bold",
                    m.passes
                      ? "text-positive dark:text-green-400"
                      : "text-critical dark:text-red-400"
                  )}
                >
                  {m.passes ? "✓" : "✕"}
                </span>
              )}
            </div>
            <p
              className={clsx(
                "text-xl font-bold",
                m.value === "—"
                  ? "text-text-secondary dark:text-gray-500"
                  : m.passes
                  ? "text-positive dark:text-green-400"
                  : "text-critical dark:text-red-400"
              )}
            >
              {m.value}
            </p>
            <p className="text-caption text-text-secondary dark:text-gray-500" style={{ fontSize: "10px" }}>
              Min: {m.minimum}
            </p>
            <AskSAMButton context={m.askContext} size="xs" />
          </div>
        ))}
      </div>
    </div>
  );
}
