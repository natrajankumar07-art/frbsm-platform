import { clsx } from "clsx";
import { SamAvatar } from "../copilot/SamAvatar";
import { AskSAMButton } from "./AskSAMButton";
import type { BankHealth } from "./BankHealthIndicator";

interface ExecutiveSAMPanelProps {
  entityName: string;
  snapshotDate?: string;
  health: BankHealth;
  alertCount: number;
}

function getDynamicGreeting(health: BankHealth, entityName: string): string {
  const hour = new Date().getHours();
  const timeStr =
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  if (health === "healthy") {
    return `${timeStr}. ${entityName} is in a strong regulatory position across all key metrics. No immediate action is required.`;
  } else if (health === "warning") {
    return `${timeStr}. I've identified metrics requiring your attention for ${entityName}. Please review the regulatory status grid below.`;
  } else {
    return `${timeStr}. ${entityName} requires immediate executive attention. One or more critical regulatory thresholds are breached.`;
  }
}

function getExecutiveSummary(
  health: BankHealth,
  alertCount: number,
  entityName: string
): string {
  const alertText =
    alertCount === 0
      ? "No active alerts"
      : `${alertCount} active alert${alertCount !== 1 ? "s" : ""}`;

  if (health === "healthy") {
    return `All regulatory ratios pass minimum requirements. ${alertText}. ${entityName} maintains adequate liquidity buffers and capital adequacy ratios in line with Basel III and local regulatory requirements.`;
  } else if (health === "warning") {
    return `Some regulatory metrics are approaching minimum thresholds. ${alertText}. Management action is recommended to restore adequate buffers before the next reporting date.`;
  } else {
    return `Critical regulatory breaches detected. ${alertText}. Immediate remediation is required. Contact the CRO and regulatory liaison teams.`;
  }
}

const HEALTH_PANEL_STYLE: Record<
  BankHealth,
  { border: string; glow: string }
> = {
  healthy: {
    border: "border-positive/20 dark:border-green-700/30",
    glow: "shadow-[0_0_24px_rgba(31,122,74,0.12)] dark:shadow-[0_0_24px_rgba(34,197,94,0.10)]",
  },
  warning: {
    border: "border-warning/20 dark:border-amber-700/30",
    glow: "shadow-[0_0_24px_rgba(184,115,15,0.12)] dark:shadow-[0_0_24px_rgba(245,158,11,0.10)]",
  },
  critical: {
    border: "border-critical/20 dark:border-red-700/30",
    glow: "shadow-[0_0_24px_rgba(176,49,44,0.15)] dark:shadow-[0_0_24px_rgba(239,68,68,0.12)]",
  },
};

export function ExecutiveSAMPanel({
  entityName,
  snapshotDate,
  health,
  alertCount,
}: ExecutiveSAMPanelProps) {
  const greeting = getDynamicGreeting(health, entityName);
  const summary = getExecutiveSummary(health, alertCount, entityName);
  const panelStyle = HEALTH_PANEL_STYLE[health];

  return (
    <div
      className={clsx(
        "card flex flex-col gap-4 border-2 dark:bg-gray-900",
        panelStyle.border,
        panelStyle.glow
      )}
      data-testid="executive-sam-panel"
    >
      {/* SAM identity header */}
      <div className="flex items-center gap-3">
        <SamAvatar size="lg" statusDot glow />
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="text-heading font-bold text-text-primary dark:text-gray-100">
              SAM
            </p>
            <span className="text-caption text-positive dark:text-green-400 font-medium">
              ● Online
            </span>
          </div>
          <p className="text-caption text-text-secondary dark:text-gray-400">
            Senior Banking Intelligence Advisor
          </p>
          {snapshotDate && (
            <p
              className="text-text-secondary dark:text-gray-500"
              style={{ fontSize: "10px" }}
            >
              Snapshot: {snapshotDate}
            </p>
          )}
        </div>
      </div>

      {/* Dynamic greeting */}
      <div className="rounded-lg bg-surface dark:bg-gray-800 border border-border dark:border-gray-700 px-4 py-3">
        <p className="text-body text-text-primary dark:text-gray-200 leading-relaxed">
          {greeting}
        </p>
      </div>

      {/* Executive summary */}
      <div>
        <p className="text-caption font-semibold text-text-secondary dark:text-gray-400 uppercase tracking-wide mb-1">
          Executive Summary
        </p>
        <p className="text-body text-text-secondary dark:text-gray-300 leading-relaxed">
          {summary}
        </p>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2">
        <AskSAMButton
          context={`Provide a comprehensive executive summary for ${entityName} covering LCR, NSFR, capital adequacy, and key regulatory risks.`}
          label="Full Briefing"
          size="sm"
        />
        <AskSAMButton
          context={`What are the recommended management actions for ${entityName} based on the current regulatory position?`}
          label="Recommended Actions"
          size="sm"
        />
        {alertCount > 0 && (
          <AskSAMButton
            context={`Explain all active regulatory alerts for ${entityName} and provide remediation guidance.`}
            label={`${alertCount} Alert${alertCount !== 1 ? "s" : ""}`}
            size="sm"
          />
        )}
      </div>
    </div>
  );
}
