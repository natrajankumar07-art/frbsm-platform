"""Capital Intelligence reasoning module (CET1, Tier 1, TCR, Leverage)."""

from __future__ import annotations

from .base import ReasoningContext, ReasoningModule


class CapitalModule(ReasoningModule):
    """Interprets capital adequacy engine outputs for the AI."""

    domain = "capital"

    def is_relevant(self, ctx: ReasoningContext) -> bool:
        return "capital" in ctx.detected_domains or ctx.capital is not None

    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        lines: list[str] = [
            "## Capital Intelligence Guidance",
            "",
            "You are acting as a BCG Capital & Risk Management senior advisor. "
            "Interpret the pre-computed capital adequacy data provided in the financial context. "
            "Never recompute ratios — only explain, diagnose, and recommend.",
            "",
        ]

        if ctx.capital:
            try:
                cet1 = float(ctx.capital.get("cet1_ratio", 0)) * 100
                t1 = float(ctx.capital.get("tier1_ratio", 0)) * 100
                tcr = float(ctx.capital.get("total_capital_ratio", 0)) * 100
                lev = float(ctx.capital.get("leverage_ratio", 0)) * 100
                rwa = float(ctx.capital.get("total_rwa", 0))
                cet1_cap = float(ctx.capital.get("cet1_capital", 0))
                passes = ctx.capital.get("passes_all", True)

                # Basel III minimums
                cet1_min, t1_min, tcr_min, lev_min = 4.5, 6.0, 8.0, 3.5
                # With CCB
                cet1_ccb = 7.0

                lines += [
                    "### Capital Adequacy Position",
                    f"- CET1 Ratio:          {cet1:.2f}% (minimum 4.50%; with CCB 7.00%; headroom {cet1 - cet1_ccb:+.2f}pp)",
                    f"- Tier 1 Ratio:        {t1:.2f}% (minimum 6.00%; headroom {t1 - t1_min:+.2f}pp)",
                    f"- Total Capital Ratio: {tcr:.2f}% (minimum 8.00%; headroom {tcr - tcr_min:+.2f}pp)",
                    f"- Leverage Ratio:      {lev:.2f}% (minimum 3.50%; headroom {lev - lev_min:+.2f}pp)",
                    f"- Total RWA:           {rwa:,.0f}",
                    f"- CET1 Capital (₹):   {cet1_cap:,.0f}",
                    f"- Overall Status:      {'ALL MINIMUMS PASS' if passes else 'ONE OR MORE MINIMUMS FAIL'}",
                    "",
                    "### Capital Analysis Framework",
                    "Analytical lenses to apply when the user asks about capital:",
                    "- Capital stack quality: CET1 vs. AT1 vs. Tier 2 composition",
                    "- Capital Conservation Buffer (CCB) 2.5pp — dividend/buyback restrictions",
                    "- Countercyclical Buffer (CCyB) — RBI-directed, currently 0%",
                    "- D-SIB surcharge considerations (if applicable)",
                    "- Pillar 2A/2B add-ons and ICAAP findings",
                    "- RWA density by risk type (credit / market / operational)",
                    "- Return on RWA vs. peers: capital efficiency",
                    "- AT1 instrument eligibility and call risk",
                    "- MDA (Maximum Distributable Amount) thresholds",
                    "",
                ]
            except (TypeError, ValueError):
                pass

        lines += [
            "### Response Style Requirements",
            "- Lead with a one-sentence executive verdict on capital adequacy.",
            "- Express all ratios in percent (e.g., 11.23%), not decimals.",
            "- Cite BCBS paragraph references (CAP10, etc.) and RBI circular dates.",
            "- Distinguish between minimum requirements and buffer requirements.",
            "- End with a traffic-light summary: CET1 / T1 / TCR / Leverage — Green / Amber / Red.",
        ]

        return "\n".join(lines)
