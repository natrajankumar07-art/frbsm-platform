"""
Banking Intelligence reasoning engine.

Classifies user intent and assembles an enriched system prompt by activating
the appropriate reasoning modules. No financial computation happens here.
"""

from __future__ import annotations

from .reasoning.alm import ALMModule
from .reasoning.balance_sheet import BalanceSheetModule
from .reasoning.base import ReasoningContext, ReasoningModule
from .reasoning.capital import CapitalModule
from .reasoning.executive import ExecutiveModule
from .reasoning.liquidity import LiquidityModule
from .reasoning.regulatory import RegulatoryModule
from .reasoning.stress import StressModule

# All registered modules, in priority order
_MODULES: list[ReasoningModule] = [
    LiquidityModule(),
    CapitalModule(),
    BalanceSheetModule(),
    ALMModule(),
    StressModule(),
    RegulatoryModule(),
    ExecutiveModule(),
]

# Domain keyword map — values are the domain tags; scores are additive
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "liquidity": [
        "lcr", "hqla", "liquidity coverage", "outflow", "inflow", "runoff",
        "liquidity", "liquid", "cash", "funding gap", "intraday", "buffer",
        "high quality liquid",
    ],
    "nsfr": [
        "nsfr", "stable funding", "asf", "rsf", "available stable",
        "required stable", "structural liquidity",
    ],
    "capital": [
        "cet1", "tier 1", "tier1", "capital ratio", "crar", "rwa",
        "risk weighted", "leverage ratio", "capital adequacy", "capital",
        "at1", "additional tier", "tier 2", "total capital", "capital buffer",
        "ccb", "conservation buffer", "d-sib",
    ],
    "balance_sheet": [
        "balance sheet", "total assets", "total liabilities", "equity",
        "off-balance", "assets", "liabilities", "loan to deposit", "ldr",
        "asset quality", "encumbrance",
    ],
    "alm": [
        "alm", "asset liability", "maturity mismatch", "repricing", "irrbb",
        "interest rate risk", "nii", "eve", "duration", "mclr", "rate",
        "basis risk", "term funding", "funding mix",
    ],
    "stress": [
        "stress", "scenario", "shock", "adverse", "severely adverse",
        "icaap", "stress test", "credit loss", "npa", "downturn",
        "recession", "crisis", "tail risk", "resilience",
    ],
    "regulatory": [
        "regulatory", "compliance", "rbi", "basel", "bcbs", "pillar",
        "disclosure", "reporting", "circular", "guideline", "notification",
        "pca", "prompt corrective", "inspection", "supervisory",
    ],
    "executive": [
        "summary", "overview", "board", "executive", "cro", "cfo",
        "management", "overall", "highlight", "snapshot", "dashboard",
        "report", "briefing", "presentation",
    ],
}

# Also treat "nsfr" as contributing to liquidity domain
_DOMAIN_ALIAS: dict[str, str] = {"nsfr": "liquidity"}


def classify_intent(user_message: str) -> list[str]:
    """
    Return a list of domain tags detected in the user message.

    Uses additive keyword scoring; returns any domain with score ≥ 1.
    Domains are returned in descending score order.
    """
    msg_lower = user_message.lower()
    scores: dict[str, int] = {}

    for domain, keywords in _DOMAIN_KEYWORDS.items():
        target = _DOMAIN_ALIAS.get(domain, domain)
        for kw in keywords:
            if kw in msg_lower:
                scores[target] = scores.get(target, 0) + 1

    if not scores:
        # Default to executive overview when no specific domain is detected
        return ["executive"]

    return sorted(scores.keys(), key=lambda d: -scores[d])


async def build_reasoning_context(
    user_message: str,
    entity_name: str,
    snapshot_date: str,
    financial_data: dict,
) -> ReasoningContext:
    """
    Populate a ReasoningContext from the raw financial data dict.

    `financial_data` is the dict returned by context.get_financial_data().
    """
    domains = classify_intent(user_message)

    return ReasoningContext(
        user_message=user_message,
        entity_name=entity_name,
        snapshot_date=snapshot_date,
        lcr=financial_data.get("lcr"),
        nsfr=financial_data.get("nsfr"),
        capital=financial_data.get("capital"),
        balance_sheet=financial_data.get("balance_sheet"),
        detected_domains=domains,
    )


def build_enriched_system_prompt(base_prompt: str, ctx: ReasoningContext) -> str:
    """
    Extend the base system prompt with module-specific guidance.

    Only modules that report is_relevant() = True contribute.
    """
    extensions: list[str] = []

    for module in _MODULES:
        if module.is_relevant(ctx):
            ext = module.build_prompt_extension(ctx)
            if ext:
                extensions.append(ext)

    if not extensions:
        return base_prompt

    separator = "\n\n" + "─" * 72 + "\n\n"
    banking_intelligence_block = separator.join(extensions)

    return (
        f"{base_prompt}\n\n"
        f"{'═' * 72}\n"
        f"BANKING INTELLIGENCE LAYER — ACTIVATED MODULES: "
        f"{', '.join(m.domain for m in _MODULES if m.is_relevant(ctx)).upper()}\n"
        f"{'═' * 72}\n\n"
        f"{banking_intelligence_block}"
    )
