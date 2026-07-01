"""Balance Sheet Intelligence reasoning module."""

from __future__ import annotations

from .base import ReasoningContext, ReasoningModule


class BalanceSheetModule(ReasoningModule):
    """Interprets balance sheet engine outputs for the AI."""

    domain = "balance_sheet"

    def is_relevant(self, ctx: ReasoningContext) -> bool:
        return "balance_sheet" in ctx.detected_domains or ctx.balance_sheet is not None

    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        lines: list[str] = [
            "## Balance Sheet Intelligence Guidance",
            "",
            "You are acting as a Deloitte Financial Services senior advisor specialising in "
            "bank balance sheet structure and capital efficiency. "
            "Interpret the pre-computed balance sheet data provided in the financial context. "
            "Never recompute figures — only explain, diagnose, and recommend.",
            "",
        ]

        if ctx.balance_sheet:
            try:
                assets = float(ctx.balance_sheet.get("total_assets", 0))
                liabs = float(ctx.balance_sheet.get("total_liabilities", 0))
                equity = float(ctx.balance_sheet.get("total_equity", 0))
                obs = float(ctx.balance_sheet.get("off_balance_sheet", 0) or 0)

                leverage_multiple = assets / equity if equity else 0
                debt_equity = liabs / equity if equity else 0

                lines += [
                    "### Balance Sheet Summary",
                    f"- Total Assets:        {assets:>14,.0f}",
                    f"- Total Liabilities:   {liabs:>14,.0f}",
                    f"- Total Equity:        {equity:>14,.0f}",
                    f"- Off-Balance Sheet:   {obs:>14,.0f}",
                    f"- Leverage Multiple:   {leverage_multiple:.1f}× (assets / equity)",
                    f"- Debt-to-Equity:      {debt_equity:.2f}×",
                    "",
                    "### Balance Sheet Analysis Framework",
                    "Analytical lenses to apply when the user asks about the balance sheet:",
                    "- Asset quality and loan-to-deposit ratio",
                    "- Funding mix: retail deposits vs. wholesale funding vs. interbank",
                    "- Asset encumbrance: pledged vs. unencumbered assets",
                    "- Off-balance-sheet exposure impact on leverage ratio (BCBS LEV10)",
                    "- Equity return metrics: ROA, ROE, RORWA",
                    "- Balance sheet size vs. sector peers",
                    "- Interest rate sensitivity of asset/liability mismatch",
                    "- IFRS 9 provisioning and impact on equity (ECL)",
                    "",
                ]
            except (TypeError, ValueError):
                pass

        lines += [
            "### Response Style Requirements",
            "- Lead with a one-sentence structural assessment.",
            "- Express size comparisons as multiples or percentage ratios, not raw numbers alone.",
            "- Reference RBI Format A / IFRS standards when discussing classification.",
            "- Highlight any structural vulnerabilities before strengths.",
            "- End with 2–3 balance sheet optimisation levers management can pull.",
        ]

        return "\n".join(lines)
