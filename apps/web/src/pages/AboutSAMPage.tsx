import { SamAvatar } from "../components/copilot/SamAvatar";
import { AskSAMButton } from "../components/dashboard/AskSAMButton";
import {
  Shield,
  Brain,
  Database,
  Zap,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

const CAPABILITIES = [
  {
    title: "Regulatory Analytics Interpretation",
    items: [
      "Explain LCR, NSFR, CET1, Tier 1, TCR, and Leverage ratios in plain language",
      "Identify regulatory threshold breaches and their implications",
      "Compare metrics against Basel III minimums and management buffers",
      "Explain waterfall components — HQLA tiers, cash flows, RWA drivers",
    ],
  },
  {
    title: "Executive Briefing Generation",
    items: [
      "Morning briefings with key metrics, risks, and recommended actions",
      "Daily, Weekly, Monthly Board, and Quarterly Executive briefings",
      "Customisable briefings for CEO, CRO, and Board audiences",
      "Outstanding issues and open alerts automatically included",
    ],
  },
  {
    title: "Risk Analysis and Recommendations",
    items: [
      "Priority-ranked recommendations (P1 Urgent → P5 Informational)",
      "Evidence-based analysis from engine output data",
      "Remediation guidance for liquidity, capital, and funding stress",
      "Context-aware responses based on your portfolio data",
    ],
  },
  {
    title: "Autonomous Monitoring",
    items: [
      "Continuous monitoring cycle every 15 minutes",
      "Automatic alert generation for threshold breaches",
      "Trend detection across rolling snapshot series",
      "Morning briefings generated automatically at 06:00 UTC",
    ],
  },
  {
    title: "Report Generation",
    items: [
      "CEO Summary, CRO Report, Board Pack",
      "ICAAP and ILAAP snapshots",
      "Liquidity Risk and Capital Adequacy summaries",
      "Stress testing results and scenario analysis",
    ],
  },
];

const EXPERTISE = [
  "BCBS 238 — Basel III LCR Framework",
  "BCBS 295 — Net Stable Funding Ratio",
  "CRD IV / CRR Capital Requirements",
  "ICAAP / ILAAP Internal Assessment",
  "Pillar 2 Supervisory Review",
  "Stress Testing (Regulatory & Internal)",
  "Balance Sheet Management",
  "Interest Rate Risk in the Banking Book",
  "Counterparty Credit Risk",
  "Liquidity Risk Management",
];

const BOUNDARIES = [
  {
    label: "SAM NEVER computes LCR, NSFR, CET1, or any regulatory ratio",
    icon: AlertTriangle,
    color: "text-amber-500",
    bg: "bg-amber-500/10 border-amber-500/20",
  },
  {
    label: "SAM NEVER modifies position data or financial records",
    icon: AlertTriangle,
    color: "text-amber-500",
    bg: "bg-amber-500/10 border-amber-500/20",
  },
  {
    label: "Financial engines are the single source of truth",
    icon: CheckCircle2,
    color: "text-green-500",
    bg: "bg-green-500/10 border-green-500/20",
  },
  {
    label: "All ratio values read directly from validated engine output tables",
    icon: CheckCircle2,
    color: "text-green-500",
    bg: "bg-green-500/10 border-green-500/20",
  },
  {
    label: "SAM's recommendations are advisory — human approval required",
    icon: CheckCircle2,
    color: "text-green-500",
    bg: "bg-green-500/10 border-green-500/20",
  },
];

export function AboutSAMPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-10 pb-12" data-testid="about-sam-page">
      {/* Hero */}
      <div className="rounded-2xl border-2 border-accent/20 bg-accent/5 dark:bg-gray-900 p-8 flex flex-col sm:flex-row items-center gap-8 shadow-[0_0_32px_rgba(43,91,215,0.08)]">
        <div className="flex-shrink-0">
          <SamAvatar size="lg" glow statusDot />
        </div>
        <div className="flex-1 text-center sm:text-left">
          <div className="flex items-center gap-2 justify-center sm:justify-start mb-1">
            <h1 className="text-2xl font-bold text-text-primary dark:text-gray-100">SAM</h1>
            <span className="text-sm text-green-500 font-medium">● Online</span>
          </div>
          <p className="text-body text-text-secondary dark:text-gray-400 mb-1">
            Supervisory AI Manager
          </p>
          <p className="text-caption text-text-secondary/70 dark:text-gray-500 mb-4">
            Senior Banking Intelligence Advisor · Powered by Claude (Anthropic)
          </p>
          <p className="text-body text-text-secondary dark:text-gray-300 leading-relaxed">
            SAM is an AI-powered banking intelligence advisor built into the FRBSM Platform.
            He monitors regulatory metrics continuously, generates executive briefings, surfaces
            recommendations, and answers complex banking questions — all grounded in your
            actual validated financial data.
          </p>
          <div className="mt-4">
            <AskSAMButton
              context="Introduce yourself and explain your role as the FRBSM Platform's Supervisory AI Manager."
              label="Talk to SAM"
              size="sm"
            />
          </div>
        </div>
      </div>

      {/* Capabilities */}
      <div>
        <h2 className="text-lg font-bold text-text-primary dark:text-gray-100 mb-4 flex items-center gap-2">
          <Brain className="h-5 w-5 text-accent" />
          Capabilities
        </h2>
        <div className="space-y-4">
          {CAPABILITIES.map((cap) => (
            <div
              key={cap.title}
              className="rounded-xl border border-border bg-surface p-4 dark:bg-gray-900 dark:border-gray-700"
            >
              <h3 className="text-body font-semibold text-text-primary dark:text-gray-100 mb-2 flex items-center gap-1.5">
                <ChevronRight className="h-3.5 w-3.5 text-accent flex-shrink-0" />
                {cap.title}
              </h3>
              <ul className="space-y-1">
                {cap.items.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-caption text-text-secondary dark:text-gray-400">
                    <CheckCircle2 className="h-3.5 w-3.5 text-accent flex-shrink-0 mt-0.5" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture */}
      <div>
        <h2 className="text-lg font-bold text-text-primary dark:text-gray-100 mb-4 flex items-center gap-2">
          <Database className="h-5 w-5 text-accent" />
          How SAM Works
        </h2>
        <div className="rounded-xl border border-border bg-surface p-6 dark:bg-gray-900 dark:border-gray-700">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                step: "1",
                title: "Compute Layer",
                desc: "Python financial engines (LCR, NSFR, Capital, Balance Sheet, Stress) compute all ratios from position data. No AI involvement at this layer.",
                color: "bg-green-500/15 text-green-600 dark:text-green-400",
              },
              {
                step: "2",
                title: "Tool Layer",
                desc: "15 structured tools expose engine outputs to SAM. SAM calls tools like lcr_analysis(), capital_analysis() and receives structured JSON results.",
                color: "bg-blue-500/15 text-blue-600 dark:text-blue-400",
              },
              {
                step: "3",
                title: "Reasoning Layer",
                desc: "SAM reads engine outputs and generates explanations, recommendations, briefings, and risk analysis using Claude AI. No financial computation occurs here.",
                color: "bg-purple-500/15 text-purple-600 dark:text-purple-400",
              },
            ].map((s) => (
              <div key={s.step} className="space-y-2">
                <div className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-sm font-bold ${s.color}`}>
                  {s.step}
                </div>
                <h3 className="text-body font-semibold text-text-primary dark:text-gray-100">{s.title}</h3>
                <p className="text-caption text-text-secondary dark:text-gray-400 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-border dark:border-gray-700">
            <p className="text-caption text-text-secondary dark:text-gray-400 text-center">
              This architecture ensures financial accuracy — engines compute,
              SAM explains. The two layers never mix.
            </p>
          </div>
        </div>
      </div>

      {/* Financial Boundaries */}
      <div>
        <h2 className="text-lg font-bold text-text-primary dark:text-gray-100 mb-4 flex items-center gap-2">
          <Shield className="h-5 w-5 text-accent" />
          Financial Boundaries
        </h2>
        <div className="space-y-2">
          {BOUNDARIES.map((b) => {
            const Icon = b.icon;
            return (
              <div
                key={b.label}
                className={`flex items-center gap-3 rounded-lg border px-4 py-3 ${b.bg}`}
              >
                <Icon className={`h-4 w-4 flex-shrink-0 ${b.color}`} />
                <span className="text-body text-text-primary dark:text-gray-100">{b.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Regulatory Expertise */}
      <div>
        <h2 className="text-lg font-bold text-text-primary dark:text-gray-100 mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-accent" />
          Regulatory Expertise
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {EXPERTISE.map((item) => (
            <div
              key={item}
              className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 dark:bg-gray-900 dark:border-gray-700"
            >
              <CheckCircle2 className="h-3.5 w-3.5 text-accent flex-shrink-0" />
              <span className="text-caption text-text-secondary dark:text-gray-400">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* AI Safety */}
      <div className="rounded-xl border-2 border-accent/20 bg-accent/5 dark:bg-gray-900 p-6">
        <h2 className="text-lg font-bold text-text-primary dark:text-gray-100 mb-3 flex items-center gap-2">
          <Shield className="h-5 w-5 text-accent" />
          AI Safety Statement
        </h2>
        <div className="space-y-3 text-body text-text-secondary dark:text-gray-300 leading-relaxed">
          <p>
            SAM is built with a strict separation between financial computation and AI reasoning.
            This is not a soft guideline — it is enforced architecturally. SAM has no access to
            ratio computation logic; it only receives completed engine outputs.
          </p>
          <p>
            SAM's recommendations are advisory and require human review and approval before any
            action is taken. SAM does not execute trades, modify positions, or submit regulatory
            filings. All outputs should be reviewed by qualified banking professionals.
          </p>
          <p>
            SAM is powered by Anthropic's Claude model. All conversations are bounded by the
            platform's tool layer — SAM cannot access data outside the tools provided, cannot
            connect to external services, and cannot perform actions outside its defined role.
          </p>
        </div>
      </div>
    </div>
  );
}
