"""Liquidity Intelligence reasoning module (LCR + NSFR)."""

from __future__ import annotations

from .base import ReasoningContext, ReasoningModule


class LiquidityModule(ReasoningModule):
    """Interprets LCR and NSFR engine outputs for the AI."""

    domain = "liquidity"

    def is_relevant(self, ctx: ReasoningContext) -> bool:
        return (
            "liquidity" in ctx.detected_domains
            or ctx.lcr is not None
            or ctx.nsfr is not None
        )

    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        lines: list[str] = [
            "## Liquidity Intelligence Guidance",
            "",
            "You are acting as a McKinsey Financial Institutions Group senior liquidity advisor. "
            "Interpret the pre-computed LCR and NSFR data provided in the financial context. "
            "Never recompute ratios — only explain, diagnose, and recommend.",
            "",
        ]

        if ctx.lcr:
            try:
                lcr_val = float(ctx.lcr.get("lcr_ratio", 0)) * 100
                hqla = float(ctx.lcr.get("hqla_total", 0))
                nco = float(ctx.lcr.get("net_cash_outflows", 0))
                passes = ctx.lcr.get("passes", True)
                headroom = lcr_val - 100.0

                lines += [
                    "### LCR Analysis Framework",
                    f"- Current LCR: {lcr_val:.2f}% ({'COMPLIANT' if passes else 'NON-COMPLIANT'})",
                    f"- Headroom above 100% minimum: {headroom:+.2f}pp",
                    f"- HQLA buffer: {hqla:,.0f} (Level 1 + Level 2A + Level 2B haircut-adjusted)",
                    f"- Net cash outflow stress baseline: {nco:,.0f}",
                    "",
                    "Analytical lenses to apply when the user asks about LCR:",
                    "- HQLA composition quality (Level 1 vs. Level 2A vs. Level 2B)",
                    "- Inflow cap utilisation (Basel III caps inflows at 75% of outflows)",
                    "- Concentration risk in outflow assumptions (retail vs. wholesale run-off)",
                    "- Contingency funding plan triggers",
                    "- Intraday liquidity management",
                    "- Cost of carry for maintaining HQLA buffers (opportunity cost)",
                    "",
                ]
            except (TypeError, ValueError):
                pass

        if ctx.nsfr:
            try:
                nsfr_val = float(ctx.nsfr.get("nsfr_ratio", 0)) * 100
                asf = float(ctx.nsfr.get("available_stable_funding", 0))
                rsf = float(ctx.nsfr.get("required_stable_funding", 0))
                surplus = asf - rsf
                passes = ctx.nsfr.get("passes", True)

                lines += [
                    "### NSFR Analysis Framework",
                    f"- Current NSFR: {nsfr_val:.2f}% ({'COMPLIANT' if passes else 'NON-COMPLIANT'})",
                    f"- ASF surplus over RSF: {surplus:,.0f}",
                    f"- Available Stable Funding (ASF): {asf:,.0f}",
                    f"- Required Stable Funding  (RSF): {rsf:,.0f}",
                    "",
                    "Analytical lenses to apply when the user asks about NSFR:",
                    "- Funding profile stability (retail deposits vs. wholesale > 6-month)",
                    "- Asset encumbrance and RSF weight implications",
                    "- Structural funding gap and term extension levers",
                    "- NSFR vs. LCR complementarity (short-term vs. structural liquidity)",
                    "",
                ]
            except (TypeError, ValueError):
                pass

        lines += [
            "### Response Style Requirements",
            "- Lead with a one-sentence executive assessment of the liquidity position.",
            "- Use BCBS standard acronyms (HQLA, NCO, ASF, RSF, LCR, NSFR).",
            "- Reference specific Basel III paragraphs when discussing regulatory minimums.",
            "- Quantify headroom in basis points or percentage points, not ratios.",
            "- End with 2–3 prioritised management actions.",
        ]

        return "\n".join(lines)
