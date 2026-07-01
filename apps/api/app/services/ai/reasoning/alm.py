"""Asset-Liability Management (ALM) Intelligence reasoning module."""

from __future__ import annotations

from .base import ReasoningContext, ReasoningModule


class ALMModule(ReasoningModule):
    """Interprets liquidity and structural data through an ALM lens."""

    domain = "alm"

    def is_relevant(self, ctx: ReasoningContext) -> bool:
        return "alm" in ctx.detected_domains or (
            ctx.lcr is not None and ctx.nsfr is not None
        )

    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        lines: list[str] = [
            "## ALM Intelligence Guidance",
            "",
            "You are acting as a PwC Treasury & ALM senior advisor. "
            "Analyse asset-liability mismatches using the pre-computed data in the financial context. "
            "Never recompute figures — only interpret and advise.",
            "",
            "### ALM Framework",
            "When answering ALM questions, apply these analytical dimensions:",
            "",
            "**1. Maturity Transformation Risk**",
            "- Short-term liabilities funding long-term assets (structural liquidity risk)",
            "- LCR addresses the 30-day horizon; NSFR addresses the 12-month horizon",
            "- Structural Liquidity Statement (SLS) provides the full maturity ladder",
            "",
            "**2. Interest Rate Risk in the Banking Book (IRRBB)**",
            "- Net Interest Income (NII) sensitivity to parallel rate shocks",
            "- Economic Value of Equity (EVE) sensitivity (BCBS IRRBB standard)",
            "- Repricing gaps across time buckets",
            "- Basis risk: floating rate benchmarks (MCLR vs. T-bill vs. repo)",
            "",
            "**3. Funding Concentration Risk**",
            "- Single counterparty / sector concentration in liabilities",
            "- Geographic concentration",
            "- Currency mismatch (if multi-currency operations)",
            "",
            "**4. Structural Liquidity Position**",
            "- NSFR ASF surplus = structural comfort buffer",
            "- RSF driven by long-tenor illiquid assets",
            "- Term extension of wholesale funding to improve NSFR",
            "",
        ]

        if ctx.lcr and ctx.nsfr:
            try:
                lcr_val = float(ctx.lcr.get("lcr_ratio", 0)) * 100
                nsfr_val = float(ctx.nsfr.get("nsfr_ratio", 0)) * 100

                lines += [
                    "### ALM Snapshot from Engine Data",
                    f"- 30-day liquidity coverage (LCR):   {lcr_val:.2f}%",
                    f"- 12-month structural liquidity (NSFR): {nsfr_val:.2f}%",
                ]

                if lcr_val > 130 and nsfr_val > 120:
                    lines.append(
                        "- ALM Signal: Both short-term and structural buffers are strong. "
                        "Risk is over-conservatism (excess HQLA carry cost)."
                    )
                elif lcr_val < 110 or nsfr_val < 110:
                    lines.append(
                        "- ALM Signal: Thin buffers in one or both horizons — "
                        "review rollover risk and contingency funding plan."
                    )
                lines.append("")
            except (TypeError, ValueError):
                pass

        lines += [
            "### Response Style Requirements",
            "- Frame answers using the two-horizon ALM lens (30-day and 12-month).",
            "- Distinguish interest rate risk from liquidity risk explicitly.",
            "- Reference RBI ALM Guidelines (2012) and BCBS IRRBB Standard (2016).",
            "- Suggest specific ALM instruments: repos, term deposits, CD issuance, IRS.",
            "- End with a risk register summary: top 3 ALM risks in priority order.",
        ]

        return "\n".join(lines)
