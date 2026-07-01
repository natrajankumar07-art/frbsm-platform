# FRBSM Platform — Final Demo Guide

> **Version:** v1.0-demo  
> **Audience:** Sales, Marketing, Investor Relations, Recruiters  
> **Purpose:** End-to-end demo walkthrough for the BSM Platform

---

## Quick Start

1. Open the platform at `http://localhost:3000` (or the deployed URL)
2. Click **"Launch Demo"** on the landing page
3. The platform loads Demo Bank with pre-seeded data — no setup required
4. Follow the guided product tour (first launch only)

---

## Demo Flow (20-Minute Script)

### 1. Landing Page (2 min)
**What to show:**
- Professional landing page with platform overview
- SAM introduction panel — emphasise the "AI advisor who never computes ratios"
- Three-Layer Architecture explanation
- Regulatory coverage (Basel III, BCBS 238/295, CRR, PRA, RBI, APRA)
- "Launch Demo" CTA

**Key talking point:**  
*"Most AI platforms bolt AI onto existing calculations. We've built them architecturally separate. SAM reads engine outputs — he never touches the math."*

---

### 2. Executive Dashboard (5 min)
**What to show:**
- Select Demo Bank from the entity selector
- Bank Health Indicator — shows overall regulatory posture
- SAM's greeting panel — dynamically adjusts to health status and time of day
- Regulatory Status Grid — 6 live metrics with pass/fail indicators
- Risk Heatmap — 6 risk categories with hover explanations
- Click "Ask SAM" on LCR → navigated to Copilot with pre-filled context

**Key talking points:**
- *"This is the view a CEO sees every morning. All six key ratios at a glance."*
- *"The Risk Heatmap is SAM's interpretation — he doesn't compute these, he reads the engine outputs and explains them."*

---

### 3. AI Copilot / SAM (5 min)
**What to show:**
- Ask: *"What is our current LCR position?"* — SAM explains with evidence
- Ask: *"Generate a CEO summary report"* — full report in markdown
- Ask: *"What should we do about our capital position?"* — prioritised recommendations
- Show the tool execution timeline (SAM's internal reasoning steps)
- Show the suggested prompts panel

**Key talking points:**
- *"Every answer SAM gives is grounded in your actual data — he calls tools that read your database, not generic AI knowledge."*
- *"Notice the tool call trace — you can see exactly what data SAM consulted."*

---

### 4. Regulatory Analytics (3 min)
**What to show:**
- LCR Dashboard — waterfall chart, HQLA breakdown, maturity ladder
- NSFR Dashboard — ASF/RSF breakdown
- Balance Sheet — asset/liability structure

**Key talking point:**  
*"These calculations are done by our validated Python engines, not the AI. The AI only explains them."*

---

### 5. Autonomous Intelligence (3 min)
**What to show:**
- Dashboard Row 6: AlertCenter, Recommendations, ActivityFeed
- Navigate to Briefings page — show a generated morning briefing
- Navigate to Issues page — show open issues and status lifecycle
- Navigate to Scheduled Reports — show how to configure recurring reports

**Key talking points:**
- *"SAM monitors your bank every 15 minutes automatically."*
- *"Morning briefings are generated at 06:00 UTC — the CEO's inbox gets this before they arrive."*

---

### 6. About SAM (2 min)
**What to show:**
- SAM's avatar, role, and capabilities list
- Financial boundaries section — "SAM NEVER computes LCR, NSFR…"
- AI Safety Statement

**Key talking point:**  
*"For regulators, this is the critical point. The AI layer is completely read-only. It cannot compute, cannot modify data, cannot submit filings."*

---

## Handling Common Questions

| Question | Answer |
|----------|--------|
| "Is this production-ready?" | The financial engines are production-grade. The demo runs on a local PostgreSQL with seeded data. |
| "What happens with real bank data?" | The architecture is the same — connect real position data to the API, and all 7 engines run automatically. |
| "Who provides the AI?" | Anthropic (Claude). The platform is model-agnostic at the architecture level. |
| "Can this run on-premise?" | Yes. Docker Compose deployment, no cloud dependencies required. |
| "Is SAM compliant with MAS/FCA/PRA AI guidance?" | SAM is advisory-only. All financial calculations remain with deterministic engines. Human approval required for any action. |
| "How do you prevent hallucinations?" | SAM only has access to 15 structured tools that return real database data. He cannot invent numbers. |

---

## Reset Demo State

To reset to a clean demo state:
```bash
# From the project root
docker compose exec api python -c "from app.scripts.seed import seed_demo; seed_demo()"
```

Or trigger a fresh monitoring run:
```
POST /api/v1/autonomous/monitor/run
```

---

## Demo Environment URLs

| Environment | URL | Notes |
|-------------|-----|-------|
| Local | http://localhost:3000 | Requires `docker compose up` |
| Staging | https://staging.bsmplatform.in | Always-on |
| Production | https://bsmplatform.in | Approval required |
