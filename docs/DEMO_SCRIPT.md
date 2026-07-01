# BSM Platform — Demo Script

> **Duration:** 20 minutes  
> **Format:** Presenter-led live demo  
> **Version:** v1.0-demo

---

## Pre-Demo Checklist

- [ ] Platform running locally (`docker compose up`)
- [ ] Demo Bank entity exists with at least 3 snapshots
- [ ] Latest monitoring run is recent (< 1 hour old)
- [ ] At least one executive briefing generated
- [ ] Browser set to 1920×1080, zoom at 100%
- [ ] Dark mode enabled (more visually striking for demos)

---

## Script

### OPENING (0:00–1:00)

> "What you're about to see is a new category of banking software. Not a dashboard with charts, not a BI tool. This is an AI platform that reads your actual balance sheet and talks to your regulators' requirements."

**Action:** Navigate to `/welcome`

> "This is the landing page. Notice the three-layer architecture — financial engines, tools, and reasoning. That separation is the key design principle of the entire platform."

---

### DEMO MODE (1:00–1:30)

> "One click. No setup. Pre-loaded with Demo Bank data."

**Action:** Click "Launch Interactive Demo"

---

### EXECUTIVE DASHBOARD (1:30–6:00)

> "This is what a CEO sees when they open their laptop. All six Basel III metrics, SAM's assessment, risk exposure by category."

**Action:** Point to Bank Health Indicator

> "This traffic light is SAM's interpretation. Green means all six ratios pass their regulatory minimums. Let's look at the detail."

**Action:** Point to Regulatory Status Grid

> "LCR, NSFR, CET1, Tier 1, Total Capital, Leverage. Each with its actual value, regulatory minimum, and whether it's in buffer."

**Action:** Hover over a Risk Heatmap cell

> "The Risk Heatmap. SAM reads the engine outputs and maps them to risk domains. Hover over any cell to see his reasoning."

**Action:** Click "Ask SAM" on the LCR cell

---

### AI COPILOT (6:00–11:00)

> "Here is SAM. A senior banking AI advisor available 24 hours a day."

**Action:** Show the pre-filled LCR question, press Enter

> "Notice what happens. SAM doesn't make something up. He calls tools — lcr_analysis, get_alerts, maybe nsfr_analysis — gets your actual data, and then explains it."

**Action:** Show the tool execution timeline

> "This is the audit trail. Every data source SAM consulted. Regulators love this — it's completely explainable AI."

**Action:** Click "CEO Summary" report button

> "Now watch this. SAM generates a full executive report — with your actual numbers, current compliance status, risks, and recommended actions."

**Action:** Read the first paragraph of the generated report

---

### AUTONOMOUS MONITORING (11:00–15:00)

**Action:** Scroll to Row 6 on the Executive Dashboard

> "This section runs without anyone pressing anything. SAM monitors your balance sheet every 15 minutes."

**Action:** Point to AlertCenter

> "If a ratio breaches its threshold, SAM raises an alert — Critical, Warning, Notice, or Info. You can acknowledge and resolve them directly here."

**Action:** Navigate to `/autonomous/briefings`

> "Every morning at 6 AM UTC, SAM generates an executive briefing. Here's last night's. It includes key metrics, material changes, top risks, and recommended actions — formatted for the CEO."

**Action:** Click to expand a briefing

**Action:** Navigate to `/autonomous/issues`

> "Outstanding issues. SAM identifies them, you manage the lifecycle. Open → Monitoring → Resolved. Your audit trail is built in."

---

### ABOUT SAM (15:00–17:00)

**Action:** Navigate to `/about-sam`

> "This is the page for your compliance and legal team. Let me show you the financial boundaries section."

**Action:** Scroll to Financial Boundaries

> "SAM never computes LCR. Never computes CET1. Never computes leverage. These are hard architectural boundaries. The compute layer runs Python — deterministic, auditable, no AI. SAM only reads what the engines produce."

**Action:** Scroll to AI Safety Statement

> "And this is our AI safety statement. SAM is advisory-only. Human approval required for every action. He cannot modify data. He cannot submit filings."

---

### CLOSE (17:00–20:00)

> "What you've just seen: real-time Basel III analytics, an AI advisor grounded in your actual data, autonomous monitoring that runs without human intervention, and a safety architecture designed for regulated environments."

> "The question most banks ask is: how long does it take to go from here to production? With your data format, typically 4–6 weeks for data integration. The platform itself is already built."

**Action:** Return to landing page

> "Any questions?"

---

## Common Objections

| Objection | Response |
|-----------|----------|
| "We already have a BI dashboard" | "This isn't a dashboard. Your BI shows you what happened. SAM tells you what to do about it — in language your CRO can act on." |
| "AI can't be trusted with regulatory data" | "It doesn't touch the calculations. Our Python engines do the math. SAM reads the outputs." |
| "We need on-premise deployment" | "Docker Compose, fully containerised, no cloud APIs required except for the Claude API call." |
| "What about model risk?" | "The only model risk is in the financial engines — and those use the same Basel III formulas your current vendor uses." |
