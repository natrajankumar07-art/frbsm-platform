"""Executive Intelligence reasoning module (board-level synthesis)."""

from __future__ import annotations

from .base import ReasoningContext, ReasoningModule


class ExecutiveModule(ReasoningModule):
    """Synthesises all metrics into board-level executive insights."""

    domain = "executive"

    def is_relevant(self, ctx: ReasoningContext) -> bool:
        return "executive" in ctx.detected_domains or "summary" in ctx.detected_domains or "overview" in ctx.detected_domains

    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        lines: list[str] = [
            "## Executive Intelligence Guidance",
            "",
            "You are acting as the Chief Risk Officer preparing a board briefing. "
            "Synthesise all available financial metrics into a coherent, board-ready narrative. "
            "Never recompute figures — only interpret and synthesise.",
            "",
            "### Executive Communication Principles",
            "1. **Lead with the verdict**: open with a 1–2 sentence overall risk assessment.",
            "2. **Exception reporting**: focus on what is outside tolerance, not what is in.",
            "3. **Quantify risk appetite utilisation**: express headroom as % of buffer consumed.",
            "4. **Peer context**: where possible, reference typical peer ranges for Indian banks.",
            "5. **Forward-looking**: end with 3 forward-looking risk watchpoints for the next quarter.",
            "",
            "### Board Dashboard Template",
            "When producing an executive summary, structure it as:",
            "```",
            "EXECUTIVE RISK SUMMARY — [Entity] — [Snapshot Date]",
            "══════════════════════════════════════════════════",
            "OVERALL ASSESSMENT: [Satisfactory / Requires Attention / Elevated Risk]",
            "",
            "LIQUIDITY",
            "  LCR:  [value]%  [▲/▼ vs minimum]  [GREEN/AMBER/RED]",
            "  NSFR: [value]%  [▲/▼ vs minimum]  [GREEN/AMBER/RED]",
            "",
            "CAPITAL",
            "  CET1:  [value]%  (headroom [+pp] above 7.0% CCB floor)  [GREEN/AMBER/RED]",
            "  TCR:   [value]%  (headroom [+pp] above 10.875% RBI min)  [GREEN/AMBER/RED]",
            "  Leverage: [value]%  [GREEN/AMBER/RED]",
            "",
            "BALANCE SHEET",
            "  Total Assets:    [value]",
            "  Leverage Ratio:  [assets/equity]×",
            "  Off-B/S:         [value]",
            "",
            "TOP 3 WATCHPOINTS",
            "  1. [risk]",
            "  2. [risk]",
            "  3. [risk]",
            "```",
            "",
        ]

        # Build a quick traffic-light from actual data
        lights: list[str] = []
        if ctx.lcr:
            try:
                lcr_val = float(ctx.lcr.get("lcr_ratio", 0)) * 100
                if lcr_val >= 130:
                    lights.append(f"LCR {lcr_val:.1f}% — GREEN")
                elif lcr_val >= 110:
                    lights.append(f"LCR {lcr_val:.1f}% — AMBER")
                else:
                    lights.append(f"LCR {lcr_val:.1f}% — RED")
            except (TypeError, ValueError):
                pass
        if ctx.nsfr:
            try:
                nsfr_val = float(ctx.nsfr.get("nsfr_ratio", 0)) * 100
                if nsfr_val >= 120:
                    lights.append(f"NSFR {nsfr_val:.1f}% — GREEN")
                elif nsfr_val >= 105:
                    lights.append(f"NSFR {nsfr_val:.1f}% — AMBER")
                else:
                    lights.append(f"NSFR {nsfr_val:.1f}% — RED")
            except (TypeError, ValueError):
                pass
        if ctx.capital:
            try:
                cet1 = float(ctx.capital.get("cet1_ratio", 0)) * 100
                if cet1 >= 10.0:
                    lights.append(f"CET1 {cet1:.1f}% — GREEN")
                elif cet1 >= 8.0:
                    lights.append(f"CET1 {cet1:.1f}% — AMBER")
                else:
                    lights.append(f"CET1 {cet1:.1f}% — RED")
            except (TypeError, ValueError):
                pass

        if lights:
            lines += ["### Indicative Traffic Light (from engine data)"]
            lines.extend(f"- {l}" for l in lights)
            lines.append("")

        lines += [
            "### Response Style Requirements",
            "- Use the board dashboard template above as your response structure.",
            "- Express all ratios as percentages; express capital amounts in crores if INR.",
            "- Use traffic-light language (GREEN / AMBER / RED) consistently.",
            "- Peer context for Indian mid-size banks: CET1 ~12–14%, LCR ~140–160%, NSFR ~120–130%.",
            "- Keep the executive summary under 400 words; use appendix for detail.",
        ]

        return "\n".join(lines)
