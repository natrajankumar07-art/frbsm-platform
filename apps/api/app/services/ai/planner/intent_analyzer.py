"""
Intent analysis for the SAM Planner (Epic 4D).

Analyzes user messages to extract:
- Primary intent (list, compare, analyze, generate_report, monitor, explain)
- Banking domains required (lcr, nsfr, capital, balance_sheet, alm, stress, regulatory)
- Entity / snapshot references
- Conversational references ("same entity", "last month", "repeat", etc.)

No financial computation. No Anthropic API calls. Pure keyword/pattern matching.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Intent categories
# ---------------------------------------------------------------------------

class PrimaryIntent:
    LIST = "list"                    # "show me all entities", "list snapshots"
    COMPARE = "compare"              # "compare Jan vs Feb", "compare two entities"
    ANALYZE = "analyze"              # "analyze LCR", "explain NSFR for Bank A"
    GENERATE_REPORT = "generate_report"  # "generate board pack", "create CEO brief"
    MONITOR = "monitor"              # "check alerts", "are there any threshold breaches?"
    EXPLAIN = "explain"              # "explain what LCR means"
    STRESS = "stress"                # "run stress scenario", "what happens under shock?"
    SUMMARIZE = "summarize"          # "summarize regulatory position"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Reference patterns for conversation intelligence
# ---------------------------------------------------------------------------

_TIME_REFS = {
    "last month": "previous_month",
    "previous month": "previous_month",
    "last quarter": "previous_quarter",
    "yesterday": "previous_day",
    "last year": "previous_year",
    "prior period": "previous_period",
}

_ENTITY_REFS = {
    "same entity": "active_entity",
    "same bank": "active_entity",
    "this entity": "active_entity",
    "current entity": "active_entity",
    "same one": "active_entity",
}

_SNAPSHOT_REFS = {
    "same snapshot": "active_snapshot",
    "this snapshot": "active_snapshot",
    "current snapshot": "active_snapshot",
    "same date": "active_snapshot",
}

_REPEAT_REFS = {
    "repeat": "repeat_analysis",
    "again": "repeat_analysis",
    "do it again": "repeat_analysis",
    "same analysis": "repeat_analysis",
    "previous analysis": "repeat_analysis",
    "run again": "repeat_analysis",
    "another report": "repeat_report",
    "generate another": "repeat_report",
    "same report": "repeat_report",
}


# ---------------------------------------------------------------------------
# Domain keyword scoring
# ---------------------------------------------------------------------------

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "lcr": ["lcr", "liquidity coverage", "hqla", "outflow", "inflow", "liquidity ratio", "30-day"],
    "nsfr": ["nsfr", "net stable", "available stable", "required stable", "asf", "rsf"],
    "capital": ["capital", "cet1", "tier 1", "tier1", "rwa", "risk weighted", "capital ratio", "leverage ratio", "tcr"],
    "balance_sheet": ["balance sheet", "assets", "liabilities", "equity", "total assets", "net assets"],
    "alm": ["alm", "asset liability", "gap", "maturity", "duration", "repricing", "cashflow", "cash flow"],
    "stress": ["stress", "scenario", "shock", "adverse", "downside", "what if", "sensitivity"],
    "regulatory": ["regulatory", "basel", "rbi", "pillar", "disclosure", "compliance", "corep", "finrep", "icaap", "ilaap"],
    "executive": ["executive", "ceo", "cfo", "cro", "board", "summary", "overview", "high level"],
}

_INTENT_KEYWORDS: dict[str, list[str]] = {
    PrimaryIntent.LIST: ["list", "show", "all entities", "all snapshots", "available", "what entities", "what snapshots"],
    PrimaryIntent.COMPARE: ["compare", "versus", " vs ", "difference between", "how does", "changed from", "compare with"],
    PrimaryIntent.ANALYZE: ["analyze", "analyse", "explain", "what is", "what are", "break down", "detail", "deep dive"],
    PrimaryIntent.GENERATE_REPORT: ["generate", "create report", "produce report", "write report", "board pack", "ceo brief", "cro report", "report"],
    PrimaryIntent.MONITOR: ["alert", "breach", "threshold", "warning", "monitor", "check", "violations", "below minimum"],
    PrimaryIntent.STRESS: ["stress", "scenario", "shock", "run stress", "what happens if", "simulate"],
    PrimaryIntent.SUMMARIZE: ["summarize", "summarise", "summary", "overview", "brief", "high level", "quick view"],
    PrimaryIntent.EXPLAIN: ["what does", "what is", "how does", "explain what", "meaning of", "definition"],
}


@dataclass
class IntentAnalysis:
    """Structured result from analyzing a user message."""

    primary_intent: str = PrimaryIntent.UNKNOWN
    domains: list[str] = field(default_factory=list)
    required_tools: list[str] = field(default_factory=list)
    entity_hints: list[str] = field(default_factory=list)   # entity names/IDs mentioned
    snapshot_hints: list[str] = field(default_factory=list) # dates/IDs mentioned
    time_reference: str | None = None      # "previous_month", "previous_quarter", etc.
    entity_reference: str | None = None    # "active_entity" etc.
    snapshot_reference: str | None = None  # "active_snapshot" etc.
    repeat_reference: str | None = None    # "repeat_analysis", "repeat_report"
    report_type_hint: str | None = None    # "board_pack", "ceo_brief", etc.
    confidence: float = 0.5

    def to_dict(self) -> dict:
        return {
            "primary_intent": self.primary_intent,
            "domains": self.domains,
            "required_tools": self.required_tools,
            "entity_hints": self.entity_hints,
            "snapshot_hints": self.snapshot_hints,
            "time_reference": self.time_reference,
            "entity_reference": self.entity_reference,
            "snapshot_reference": self.snapshot_reference,
            "repeat_reference": self.repeat_reference,
            "report_type_hint": self.report_type_hint,
            "confidence": self.confidence,
        }


_REPORT_TYPE_KEYWORDS: dict[str, list[str]] = {
    "executive_dashboard": ["executive dashboard", "exec dashboard"],
    "daily_treasury": ["daily treasury", "treasury report"],
    "liquidity_risk": ["liquidity risk report"],
    "capital_adequacy": ["capital adequacy report", "capital report"],
    "alm_summary": ["alm report", "alm summary", "asset liability report"],
    "stress_testing": ["stress report", "stress testing report"],
    "regulatory_compliance": ["regulatory compliance", "compliance report"],
    "board_pack": ["board pack", "board report"],
    "cro_report": ["cro report", "risk report"],
    "ceo_brief": ["ceo brief", "ceo report", "ceo summary"],
}

_DOMAIN_TO_PRIMARY_TOOLS: dict[str, list[str]] = {
    "lcr": ["get_snapshots", "summarize_regulatory_results"],
    "nsfr": ["get_snapshots", "summarize_regulatory_results"],
    "capital": ["get_snapshots", "summarize_regulatory_results"],
    "balance_sheet": ["get_snapshots", "summarize_regulatory_results"],
    "alm": ["get_snapshots", "summarize_regulatory_results"],
    "stress": ["run_stress_scenario", "summarize_regulatory_results"],
    "regulatory": ["summarize_regulatory_results"],
    "executive": ["generate_executive_summary"],
}


def analyze_intent(user_message: str, memory_preamble: str = "") -> IntentAnalysis:
    """Analyze user message and return structured IntentAnalysis."""
    text = f"{user_message} {memory_preamble}".lower()
    result = IntentAnalysis()

    # --- Primary intent ---
    intent_scores: dict[str, int] = {}
    for intent, keywords in _INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score:
            intent_scores[intent] = score

    if intent_scores:
        result.primary_intent = max(intent_scores, key=lambda k: intent_scores[k])
        result.confidence = min(0.95, 0.5 + intent_scores[result.primary_intent] * 0.15)

    # --- Domain detection ---
    domain_scores: dict[str, int] = {}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score:
            domain_scores[domain] = score
    result.domains = sorted(domain_scores, key=lambda k: -domain_scores[k])

    # --- Required tools heuristic ---
    tool_set: list[str] = ["list_entities"]  # almost always needed
    if result.primary_intent in (PrimaryIntent.LIST,):
        tool_set = ["list_entities", "get_snapshots"]
    elif result.primary_intent == PrimaryIntent.COMPARE:
        tool_set = ["list_entities", "get_snapshots", "compare_snapshots"]
        if "entit" in text:
            tool_set.append("compare_entities")
    elif result.primary_intent == PrimaryIntent.STRESS:
        tool_set = ["list_entities", "get_snapshots", "run_stress_scenario"]
    elif result.primary_intent == PrimaryIntent.GENERATE_REPORT:
        tool_set = ["list_entities", "get_snapshots", "generate_executive_summary"]
    elif result.primary_intent in (PrimaryIntent.ANALYZE, PrimaryIntent.SUMMARIZE):
        tool_set = ["list_entities", "get_snapshots", "summarize_regulatory_results"]
    elif result.primary_intent == PrimaryIntent.MONITOR:
        tool_set = ["list_entities", "get_snapshots", "summarize_regulatory_results"]

    # Add domain-specific tools
    for domain in result.domains[:2]:  # top 2 domains
        extra = _DOMAIN_TO_PRIMARY_TOOLS.get(domain, [])
        for t in extra:
            if t not in tool_set:
                tool_set.append(t)

    result.required_tools = tool_set

    # --- Report type hint ---
    for rt, keywords in _REPORT_TYPE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            result.report_type_hint = rt
            if "generate_executive_summary" not in result.required_tools:
                result.required_tools.append("generate_executive_summary")
            break

    # --- Conversational references ---
    for phrase, ref in _TIME_REFS.items():
        if phrase in text:
            result.time_reference = ref
            break

    for phrase, ref in _ENTITY_REFS.items():
        if phrase in text:
            result.entity_reference = ref
            break

    for phrase, ref in _SNAPSHOT_REFS.items():
        if phrase in text:
            result.snapshot_reference = ref
            break

    for phrase, ref in _REPEAT_REFS.items():
        if phrase in text:
            result.repeat_reference = ref
            break

    # --- Extract date mentions (YYYY-MM-DD or MM/DD/YYYY) ---
    date_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")
    result.snapshot_hints = date_pattern.findall(user_message)

    return result
