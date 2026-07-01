"""
AI Copilot prompt library for the FRBSM Banking Intelligence platform.

COPILOT_SYSTEM_PROMPT: defines the AI's role, constraints, and response style.
SUGGESTED_PROMPTS: ~50 professional prompts organised by domain.

All prompts assume the AI acts as an explainer and orchestrator only.
The AI NEVER computes financial ratios, recalculates numbers, or overrides
the output of the deterministic Python engines.
"""

from __future__ import annotations

COPILOT_SYSTEM_PROMPT = """\
You are the FRBSM AI Copilot, the Banking Intelligence assistant for the Financial \
Risk & Balance Sheet Management (FRBSM) platform.

## Role and Mandate
You act as a senior advisor at a top-tier consulting firm (McKinsey FIG / BCG GAMMA / \
Deloitte Banking) specialising in regulatory capital, liquidity risk, and balance sheet \
management for commercial banks. You synthesise pre-computed engine outputs into \
board-ready, regulator-grade analysis and recommendations.

## Authoritative Source of Truth
All financial numbers (LCR, NSFR, Capital ratios, Balance Sheet figures) are computed \
exclusively by the BSM deterministic Python engines and are provided to you in the \
[COMPUTED BY BSM ENGINES] section of the context. You MUST:
- Accept those numbers as fact. NEVER recompute, recalculate, or second-guess them.
- NEVER state a ratio, amount, or metric that contradicts the engine output.
- Cite engine outputs as "[BSM Engine result]" when referencing specific numbers.
- Explain WHAT the numbers mean, WHY they matter, and WHAT management should do.

## What You NEVER Do
- Compute LCR, NSFR, CET1, Total Capital Ratio, Leverage Ratio, RWA, or any variant.
- Reproduce Basel III formulae as if performing the calculation yourself.
- Contradict or override engine output with your own arithmetic.
- Speculate about numbers when they are not in the context.
- Give legal or accounting advice.

## Response Quality Standards
1. **Executive precision**: Every answer must open with a 1-2 sentence executive verdict.
2. **Evidence citations**: Reference specific BCBS paragraphs, RBI circulars, or IFRS \
   standards when making regulatory assertions.
3. **Quantified insights**: Always express headroom in basis points or percentage points \
   (e.g., "127bp above the 100% LCR minimum"), not just "above the minimum."
4. **Structured output**: Use markdown headers, tables, and bullet lists. Long answers use \
   an Executive Summary section followed by deeper analysis.
5. **Actionable recommendations**: End with 2-5 prioritised, specific management actions.
6. **Proportionality**: Match response length to question complexity. Simple questions get \
   direct 2-3 sentence answers. Board-level analysis gets full structured reports.

## Regulatory Reference Base
- Basel III: BCBS (2013) LCR30/40; BCBS (2014) NSF20/30/40; BCBS (2011) CAP10/20; \
  BCBS (2014) LEV10
- RBI India: Master Circular on Basel III Capital (Jul 2015); LCR Master Circular (Jul 2015, \
  amended Apr 2021); NSFR Guidelines (May 2018); IRRBB Guidelines (Feb 2023)
- IFRS: IFRS 9 (Financial Instruments); IFRS 7 (Financial Instruments Disclosures)

## Tone and Style
- Senior advisor tone: confident, precise, action-oriented.
- No hedging language ("it seems", "perhaps", "might be") unless genuinely uncertain.
- Use Indian banking context: amounts in INR crores for large numbers; reference RBI, SEBI, \
  and Indian banking regulation where relevant.
- When uncertain about context not in the data, say so clearly rather than speculating.\
"""


# ---------------------------------------------------------------------------
# Suggested Prompts (~50 professional prompts across 8 domains)
# ---------------------------------------------------------------------------

SUGGESTED_PROMPTS: list[dict[str, str]] = [
    # ── Liquidity Coverage Ratio ───────────────────────────────────────────
    {
        "category": "Liquidity — LCR",
        "text": "What is our current LCR position and how much headroom do we have above the regulatory minimum?",
    },
    {
        "category": "Liquidity — LCR",
        "text": "Explain the composition of our HQLA buffer — what is the Level 1 vs Level 2 split and what are the haircut implications?",
    },
    {
        "category": "Liquidity — LCR",
        "text": "Is the inflow cap binding for us? What does that mean for our LCR management strategy?",
    },
    {
        "category": "Liquidity — LCR",
        "text": "How would a 25% spike in wholesale deposit run-off rates affect our LCR position?",
    },
    {
        "category": "Liquidity — LCR",
        "text": "What are the top three HQLA optimisation actions that would most improve our LCR headroom?",
    },
    {
        "category": "Liquidity — LCR",
        "text": "Compare our LCR to typical levels for Indian mid-size banks. Are we over-buffered or under-buffered?",
    },
    {
        "category": "Liquidity — LCR",
        "text": "What contingency funding plan triggers should we monitor given our current LCR level?",
    },
    # ── Net Stable Funding Ratio ───────────────────────────────────────────
    {
        "category": "Liquidity — NSFR",
        "text": "What is our NSFR position and what does the ASF surplus tell us about our structural funding strength?",
    },
    {
        "category": "Liquidity — NSFR",
        "text": "What is driving our Required Stable Funding (RSF) — is it long-tenor assets or off-balance sheet commitments?",
    },
    {
        "category": "Liquidity — NSFR",
        "text": "What term-extension strategies could improve our Available Stable Funding (ASF) score?",
    },
    {
        "category": "Liquidity — NSFR",
        "text": "How does our NSFR complement our LCR — what does the gap between them reveal about our structural vs. short-term liquidity risk?",
    },
    {
        "category": "Liquidity — NSFR",
        "text": "What is the NSFR reporting obligation and what would a breach require us to disclose to RBI?",
    },
    # ── Capital Adequacy ───────────────────────────────────────────────────
    {
        "category": "Capital",
        "text": "Provide a comprehensive assessment of our capital adequacy position across all four Basel III ratios.",
    },
    {
        "category": "Capital",
        "text": "How much of our Capital Conservation Buffer (CCB) headroom is available, and at what CET1 level do dividend restrictions begin?",
    },
    {
        "category": "Capital",
        "text": "What is our leverage ratio and does it constrain our balance sheet growth plans?",
    },
    {
        "category": "Capital",
        "text": "Break down our RWA composition — how much credit, market, and operational risk RWA are we carrying?",
    },
    {
        "category": "Capital",
        "text": "What AT1 instruments could we issue to optimise our Tier 1 ratio without diluting CET1?",
    },
    {
        "category": "Capital",
        "text": "What is our Return on RWA (RoRWA) and how does the current capital level affect shareholder returns?",
    },
    {
        "category": "Capital",
        "text": "If we needed to raise capital to meet a RBI Pillar 2A add-on, what options should the board consider?",
    },
    {
        "category": "Capital",
        "text": "Explain what the MDA (Maximum Distributable Amount) restrictions mean for our current CET1 position.",
    },
    {
        "category": "Capital",
        "text": "What are the PCA (Prompt Corrective Action) framework thresholds and how far are we from each trigger?",
    },
    # ── Balance Sheet ──────────────────────────────────────────────────────
    {
        "category": "Balance Sheet",
        "text": "Give me a structural overview of our balance sheet — what does our asset-liability mix tell you about our business model?",
    },
    {
        "category": "Balance Sheet",
        "text": "What is our leverage multiple and how does it compare to Basel III leverage ratio implications?",
    },
    {
        "category": "Balance Sheet",
        "text": "How do our off-balance-sheet exposures affect the Basel III leverage ratio calculation?",
    },
    {
        "category": "Balance Sheet",
        "text": "What does our equity base imply for our capacity to absorb credit losses before breaching CET1 minimums?",
    },
    {
        "category": "Balance Sheet",
        "text": "Identify the top balance sheet structural vulnerabilities we should address in the next planning cycle.",
    },
    {
        "category": "Balance Sheet",
        "text": "How does our loan-to-deposit ratio position us relative to RBI guidance and sector peers?",
    },
    # ── Asset-Liability Management ─────────────────────────────────────────
    {
        "category": "ALM",
        "text": "Provide an integrated ALM assessment covering both our 30-day (LCR) and 12-month (NSFR) liquidity horizons.",
    },
    {
        "category": "ALM",
        "text": "What does our liquidity position tell us about our maturity transformation profile — how long are we borrowing short to lend long?",
    },
    {
        "category": "ALM",
        "text": "If interest rates rise 200bp, what are the key IRRBB transmission mechanisms we should model in our ICAAP?",
    },
    {
        "category": "ALM",
        "text": "What is the relationship between our MCLR-linked loan book and our funding costs — where is our repricing risk?",
    },
    {
        "category": "ALM",
        "text": "How should we structure our investment portfolio to optimise HQLA quality while managing duration risk?",
    },
    {
        "category": "ALM",
        "text": "What ALM instruments — repos, CD issuance, IRS, term deposits — would most efficiently close our structural funding gap?",
    },
    {
        "category": "ALM",
        "text": "How do we assess basis risk between our floating-rate liabilities and fixed-rate loan book?",
    },
    # ── Stress Testing ─────────────────────────────────────────────────────
    {
        "category": "Stress Testing",
        "text": "Walk me through how our LCR would perform under a moderate stress scenario with 25% higher deposit run-off rates.",
    },
    {
        "category": "Stress Testing",
        "text": "Simulate the capital impact of a severe GDP contraction scenario on our CET1 ratio.",
    },
    {
        "category": "Stress Testing",
        "text": "What stress scenarios should we include in our RBI ICAAP submission for this reporting period?",
    },
    {
        "category": "Stress Testing",
        "text": "How resilient is our NSFR to a sudden inability to roll over short-term wholesale funding?",
    },
    {
        "category": "Stress Testing",
        "text": "Explain the difference between pre-management-action and post-management-action stress outcomes for our ICAAP.",
    },
    {
        "category": "Stress Testing",
        "text": "What would a combined idiosyncratic and market stress event look like for our liquidity and capital simultaneously?",
    },
    # ── Regulatory & Compliance ────────────────────────────────────────────
    {
        "category": "Regulatory",
        "text": "Provide a complete regulatory compliance dashboard — LCR, NSFR, CET1, Leverage — against both Basel III and RBI minimums.",
    },
    {
        "category": "Regulatory",
        "text": "What are the current RBI-enhanced capital requirements (including CCB) and how do we stack up against each one?",
    },
    {
        "category": "Regulatory",
        "text": "What are the LCR disclosure obligations under Pillar 3 and what are the key tables we need to publish?",
    },
    {
        "category": "Regulatory",
        "text": "Explain the Basel III NSFR requirement and how RBI implemented it in the October 2021 circular.",
    },
    {
        "category": "Regulatory",
        "text": "What is the D-SIB (Domestic Systemically Important Bank) surcharge and does it apply to us?",
    },
    {
        "category": "Regulatory",
        "text": "What are the key regulatory reporting deadlines for LCR, NSFR, and CRAR to RBI this quarter?",
    },
    {
        "category": "Regulatory",
        "text": "What are the Large Exposures Framework limits and how do they interact with our capital position?",
    },
    # ── Executive / Board Synthesis ────────────────────────────────────────
    {
        "category": "Executive",
        "text": "Prepare a board-level risk summary of our current regulatory capital and liquidity position.",
    },
    {
        "category": "Executive",
        "text": "What are the top three risks to our regulatory compliance position that the board should be aware of this quarter?",
    },
    {
        "category": "Executive",
        "text": "Draft a risk appetite statement framing for our CET1, LCR, and NSFR management buffers.",
    },
    {
        "category": "Executive",
        "text": "Give me a traffic-light regulatory dashboard — GREEN / AMBER / RED — for each of our Basel III ratios.",
    },
    {
        "category": "Executive",
        "text": "What does our overall risk profile look like heading into the next planning cycle? What are the forward-looking watchpoints?",
    },
    {
        "category": "Executive",
        "text": "Summarise our balance sheet, capital, and liquidity positions in under 200 words as if presenting to the CFO.",
    },
]
