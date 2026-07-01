# BSM Platform — User Guide

> **Version:** v1.0-demo  
> **Audience:** Risk Analysts, Treasury Officers, Risk Managers, CROs

---

## Getting Started

### 1. Launch the Platform
- Navigate to `http://localhost:3000` (local) or the deployed URL
- Click **"Launch Demo"** for instant access with pre-loaded data
- Or sign in with your credentials

### 2. Select Your Entity
Use the **entity selector** in the top bar to choose your legal entity. All analytics and SAM's responses are scoped to the selected entity.

### 3. Guided Tour
On first launch, a guided tour walks you through the platform's key features. Dismiss it at any time — restart from **Sidebar → Product Tour**.

---

## Executive Dashboard

The default view provides a complete regulatory overview.

### Bank Health Indicator
A traffic-light status showing whether all six key ratios pass regulatory minimums:
- 🟢 **Healthy** — All checks passing
- 🟡 **Warning** — One metric below threshold
- 🔴 **Critical** — Multiple metrics in breach

### SAM Panel
SAM's dynamic greeting adapts to your bank's health status and time of day. Click **"Ask SAM"** for an instant full briefing, or **"Recommended Actions"** for remediation guidance.

### Regulatory Status Grid
Six metrics displayed in a 3×2 grid:

| Metric | Regulatory Minimum |
|--------|-------------------|
| LCR | 100% |
| NSFR | 100% |
| CET1 | 4.5% |
| Tier 1 | 6.0% |
| Total Capital | 8.0% |
| Leverage | 3.0% |

Each cell shows the actual value, pass/fail status, and an "Ask SAM" button for instant analysis.

### Risk Heatmap
6 risk categories mapped by SAM from engine outputs: Liquidity, Capital, Funding, Market, Operational, Interest Rate. Hover over any cell for SAM's explanation.

### Insight Cards
4 summary cards (Liquidity, Capital, Funding Stability, Stress Position) with key drivers and SAM's recommendation.

### Trend Charts
LCR/NSFR trends and CET1/Leverage trends across the last 5 reporting snapshots.

### Autonomous Intelligence Row
Bottom section showing:
- **Alert Center** — Live alerts from SAM's monitoring engine
- **SAM Recommendations** — Priority-ranked actionable recommendations
- **Activity Feed** — Recent autonomous actions (monitoring runs, briefings, alerts)

---

## AI Copilot

Access from the sidebar or press **Ctrl+K**.

### Asking Questions
Type any banking question in plain language:
- *"What is our current LCR position?"*
- *"Explain the NSFR shortfall"*
- *"What are the main risks to our capital position?"*
- *"Generate a weekly risk summary"*

### Context Injection
Clicking **"Ask SAM"** on any dashboard element pre-fills the Copilot with relevant context. SAM receives both your question and the metric context.

### Report Generation
Click report buttons to generate formatted reports:
- CEO Summary
- CRO Report
- Board Pack
- ICAAP Snapshot
- ILAAP Snapshot
- Liquidity Summary
- Capital Summary

### Tool Call Transparency
The execution timeline shows every tool SAM called and what data he received. This is your AI audit trail.

---

## Analytics

### LCR Analytics
- LCR ratio vs. 100% minimum
- HQLA breakdown by tier (Level 1, Level 2A, Level 2B)
- Inflow/outflow waterfall
- Net cash outflows and inflow cap

### NSFR Analytics
- NSFR ratio vs. 100% minimum
- Available Stable Funding (ASF) by source
- Required Stable Funding (RSF) by asset class

### Balance Sheet Analytics
- Total assets/liabilities/equity
- Asset breakdown by class
- Funding mix analysis

---

## Autonomous Intelligence

### Briefings
SAM generates 5 briefing types automatically:
- **Morning** — Daily at 06:00 UTC
- **Daily Summary** — End-of-day position
- **Weekly Summary** — 7-day trend
- **Monthly Board** — Board-ready format
- **Quarterly Executive** — Senior management review

Generate any briefing on demand from the Briefings page.

### Issues
Track regulatory and operational issues with a 3-stage lifecycle:
1. **Open** — Identified, awaiting action
2. **Monitoring** — Under observation
3. **Resolved** — Closed

Create issues manually or let SAM identify them through monitoring.

### Scheduled Reports
Configure recurring automated reports. Set report type and frequency (daily/weekly/monthly). SAM generates them automatically on schedule.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `G H` | Go to Executive Dashboard |
| `G C` | Go to AI Copilot |
| `G L` | Go to LCR Analytics |
| `G N` | Go to NSFR Analytics |
| `Ctrl+K` | Open AI Copilot |
| `?` | Open Help Center |
| `Escape` | Dismiss modals and dialogs |

---

## Tips for Getting the Most from SAM

1. **Be specific** — "Explain LCR for Demo Bank as of Q4 2025" gets better results than "Explain LCR"
2. **Ask for reports** — "Generate a CRO report" produces a complete formatted document
3. **Chain questions** — SAM maintains context across the conversation
4. **Use dashboard buttons** — "Ask SAM" pre-fills context from the specific metric
5. **Ask about regulations** — "What does BCBS 238 say about Level 2B haircuts?" is a valid question
