"""Regulatory Intelligence reasoning module (Basel III / RBI guidance)."""

from __future__ import annotations

from .base import ReasoningContext, ReasoningModule


class RegulatoryModule(ReasoningModule):
    """Provides regulatory interpretation and compliance status framing."""

    domain = "regulatory"

    def is_relevant(self, ctx: ReasoningContext) -> bool:
        return "regulatory" in ctx.detected_domains or "compliance" in ctx.detected_domains

    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        lines: list[str] = [
            "## Regulatory Intelligence Guidance",
            "",
            "You are acting as a Big Four (KPMG EMA Financial Services) senior regulatory advisor. "
            "Interpret the bank's regulatory compliance position using the data provided "
            "in the financial context. Never recompute figures — only assess and advise.",
            "",
            "### Regulatory Framework Reference",
            "",
            "**Basel III Pillars**",
            "- Pillar 1: Minimum capital requirements (CET1/T1/TCR/Leverage) and liquidity (LCR/NSFR)",
            "- Pillar 2: ICAAP — internal capital adequacy assessment process",
            "- Pillar 3: Market discipline through public disclosure",
            "",
            "**RBI-Specific Requirements (India)**",
            "| Metric | Basel III Min | RBI Implementation |",
            "|---|---|---|",
            "| CET1 | 4.5% | 5.5% (effective 2019) |",
            "| CCB | 2.5% | 2.5% |",
            "| CET1 + CCB | 7.0% | 8.0% |",
            "| Total CRAR | 8.0% | 10.875% (incl. CCB + CCyB) |",
            "| LCR | 100% | 100% (Jan 2019) |",
            "| NSFR | 100% | 100% (Oct 2021) |",
            "| Leverage | 3.5% | 3.5% |",
            "",
            "**Key RBI Circulars**",
            "- Master Circular – Basel III Capital Regulations (Jul 2015 and amendments)",
            "- Master Circular – LCR (Jul 2015, amended Apr 2021)",
            "- NSFR Guidelines (May 2018, effective Oct 2021)",
            "- Revised IRRBB Guidelines (Feb 2023)",
            "- Large Exposures Framework (Jun 2019)",
            "",
            "**Regulatory Reporting Calendar (India)**",
            "- LCR: Monthly to RBI (within 15 days of month-end)",
            "- NSFR: Quarterly to RBI",
            "- CRAR: Quarterly",
            "- Basel III Pillar 3 Disclosures: Quarterly (Basel III tables)",
            "",
        ]

        if ctx.lcr or ctx.capital:
            lines += [
                "### Compliance Snapshot from Engine Data",
            ]
            if ctx.lcr:
                try:
                    lcr_val = float(ctx.lcr.get("lcr_ratio", 0)) * 100
                    passes = ctx.lcr.get("passes", True)
                    lines.append(
                        f"- LCR: {lcr_val:.2f}% — {'✓ Compliant (≥100%)' if passes else '✗ Non-compliant (<100%)'}"
                    )
                except (TypeError, ValueError):
                    pass
            if ctx.nsfr:
                try:
                    nsfr_val = float(ctx.nsfr.get("nsfr_ratio", 0)) * 100
                    passes = ctx.nsfr.get("passes", True)
                    lines.append(
                        f"- NSFR: {nsfr_val:.2f}% — {'✓ Compliant (≥100%)' if passes else '✗ Non-compliant (<100%)'}"
                    )
                except (TypeError, ValueError):
                    pass
            if ctx.capital:
                try:
                    cet1 = float(ctx.capital.get("cet1_ratio", 0)) * 100
                    tcr = float(ctx.capital.get("total_capital_ratio", 0)) * 100
                    passes = ctx.capital.get("passes_all", True)
                    lines.append(f"- CET1: {cet1:.2f}% | TCR: {tcr:.2f}% — {'✓ All minimums pass' if passes else '✗ One or more minimums fail'}")
                except (TypeError, ValueError):
                    pass
            lines.append("")

        lines += [
            "### Response Style Requirements",
            "- Always distinguish Basel III minimum from RBI-enhanced minimum.",
            "- Cite specific RBI circular numbers and dates when assessing compliance.",
            "- Identify supervisory escalation triggers (PCA framework thresholds).",
            "- Frame non-compliance in terms of regulatory remediation timelines.",
            "- End with a compliance dashboard: metric × regulatory minimum × status × headroom.",
        ]

        return "\n".join(lines)
