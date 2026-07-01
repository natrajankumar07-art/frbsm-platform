"""Stress Test Intelligence reasoning module."""

from __future__ import annotations

from .base import ReasoningContext, ReasoningModule


class StressModule(ReasoningModule):
    """Provides stress-testing interpretation and scenario framing."""

    domain = "stress"

    def is_relevant(self, ctx: ReasoningContext) -> bool:
        return "stress" in ctx.detected_domains

    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        lines: list[str] = [
            "## Stress Test Intelligence Guidance",
            "",
            "You are acting as a McKinsey Risk & Resilience senior advisor. "
            "Interpret stress scenarios and their impact on the financial metrics provided "
            "in the financial context. Never recompute figures — only interpret outcomes and advise.",
            "",
            "### Stress Testing Framework",
            "",
            "**Scenario Taxonomy**",
            "- Idiosyncratic stress: bank-specific (e.g., credit event, reputational shock)",
            "- Market-wide stress: systemic (e.g., rate spike, credit crunch, currency depreciation)",
            "- Combined scenario: both idiosyncratic + systemic simultaneously",
            "",
            "**Regulatory Stress Regimes (India)**",
            "- RBI Macro Stress Test: annual CCAR-equivalent exercise",
            "- RBI Annual Inspection: CAMELS framework; liquidity stress component",
            "- Basel III Pillar 2: ICAAP internally-designed scenarios",
            "- IMF FSAP: periodic Financial Sector Assessment Programme",
            "",
            "**Typical LCR Stress Scenarios**",
            "| Scenario | Run-off Rate Shock | HQLA Impact |",
            "|---|---|---|",
            "| Mild (base) | +10% outflow run-off | −5% HQLA haircut |",
            "| Moderate | +25% outflow run-off | −15% HQLA haircut |",
            "| Severe | +50% outflow run-off | −30% HQLA haircut |",
            "",
            "**Typical Capital Stress Scenarios**",
            "| Scenario | GDP Shock | Credit Loss | CET1 Impact |",
            "|---|---|---|---|",
            "| Adverse | −2pp GDP | +100bps NPA | −150bps CET1 |",
            "| Severely Adverse | −5pp GDP | +300bps NPA | −400bps CET1 |",
            "",
            "### Stress Analysis Lenses",
            "When answering stress test questions:",
            "- Reference baseline ratios from the financial context, then layer the stress delta",
            "- Identify which buffer (HQLA, ASF, CET1, leverage) absorbs the shock first",
            "- Determine if a stressed ratio would breach the minimum threshold",
            "- Recommend pre-positioning actions (capital raise, HQLA build, term funding)",
            "- Reference management action credibility (pre-stressed vs. post-management-action)",
            "",
        ]

        if ctx.lcr and ctx.capital:
            try:
                lcr_val = float(ctx.lcr.get("lcr_ratio", 0)) * 100
                cet1 = float(ctx.capital.get("cet1_ratio", 0)) * 100
                lines += [
                    "### Current Baseline (for Stress Anchoring)",
                    f"- Baseline LCR:   {lcr_val:.2f}% → 'Adverse' scenario reduces to approx {lcr_val * 0.75:.2f}%",
                    f"- Baseline CET1:  {cet1:.2f}% → 'Adversely Adverse' scenario reduces to approx {cet1 - 4.0:.2f}%",
                    "(These are illustrative stress deltas only; actual deltas depend on portfolio composition.)",
                    "",
                ]
            except (TypeError, ValueError):
                pass

        lines += [
            "### Response Style Requirements",
            "- Always anchor stress answers to the baseline ratios from the financial context.",
            "- Use a table format to present scenario × metric stress results.",
            "- Distinguish 'pre-management-action' from 'post-management-action' outcomes.",
            "- Reference RBI ICAAP guidelines or Basel III Pillar 2 when relevant.",
            "- End with a RAG (Red/Amber/Green) stress resilience verdict.",
        ]

        return "\n".join(lines)
