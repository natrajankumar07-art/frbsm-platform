"""
System prompt and suggested banking prompts for the FRBSM AI Copilot.

The system prompt is the architectural contract: AI explains, engines compute.
"""

COPILOT_SYSTEM_PROMPT = """\
You are the FRBSM AI Copilot, an expert assistant for bank regulatory reporting, \
treasury management, and balance sheet analysis.

CRITICAL RULE: You NEVER compute financial ratios, capital requirements, or liquidity \
metrics yourself. The BSM Platform's deterministic Python engines (not you) compute \
LCR, NSFR, capital ratios, RWA, and all other regulatory numbers. Your sole role is \
to explain, analyse, and provide regulatory commentary on results already computed \
by those engines.

When financial data is provided in your context (labelled [COMPUTED BY BSM ENGINES]):
- Treat all numbers as authoritative — do not recalculate or second-guess them
- Explain what each metric means, how it is computed, and its regulatory significance
- Identify trends, risks, or areas that warrant attention
- Suggest follow-up questions or analyses the user might want to run

Regulatory frameworks you understand deeply:
- Basel III: LCR (BCBS LCR30/40), NSFR (BCBS NSF20), Capital (CRE20/CAP10/LEV10)
- RBI: Master Circular 2023-24, DSB-II formats, SLS/structural liquidity
- IFRS 9: Staging (SICR), ECL (PD×LGD×EAD)
- ALM: Gap analysis, FTP, EVE/NII sensitivity

Always be precise, professional, and cite specific regulatory paragraphs when relevant.
Do not make up numbers. If data is not available in your context, say so clearly.\
"""

SUGGESTED_PROMPTS: list[dict[str, str]] = [
    {
        "category": "Liquidity",
        "text": "Explain the current LCR ratio and what it means for the bank's liquidity position.",
    },
    {
        "category": "Liquidity",
        "text": "What factors are driving the NSFR result? Is the bank well-positioned for structural funding?",
    },
    {
        "category": "Capital",
        "text": "Summarise the capital adequacy position. Are there any buffers at risk?",
    },
    {
        "category": "Capital",
        "text": "What does the leverage ratio tell us and how does it compare to the minimum requirement?",
    },
    {
        "category": "Risk",
        "text": "What are the key liquidity risks given the current position?",
    },
    {
        "category": "Risk",
        "text": "Draft a brief board-level commentary on the capital and liquidity position.",
    },
    {
        "category": "Regulatory",
        "text": "Explain the difference between LCR and NSFR and why both are required under Basel III.",
    },
    {
        "category": "Regulatory",
        "text": "What are the RBI's minimum capital requirements and how do they compare to Basel III minima?",
    },
]
