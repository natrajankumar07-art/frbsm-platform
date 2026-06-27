# UI Polish

**Purpose:** Final visual, interaction, and copy polish required before the platform is considered production-grade. This document complements the design system and component library, focusing on the gaps that typically remain after functional UI delivery.

**Status:** Phase 27 Workstream G deliverable
**Owner:** Design + Frontend Engineering

---

## 1. Operating Principle

The platform is used by serious people doing regulated work. The UI should feel like a precision instrument — quiet, confident, dense where density helps, calm where calm matters. The reasoning layer's natural language outputs sit alongside dense quantitative tables; the UI must make that combination feel coherent rather than disjointed.

Three guiding constraints:

1. **Density without clutter.** Risk teams compare hundreds of figures at once; whitespace generosity has limits.
2. **Calm under high stakes.** Colour and motion are used sparingly; alerts must mean alerts.
3. **Reasoning transparency.** Where the LLM contributed, the user can see what it produced, what it was given, and how to verify the underlying compute.

---

## 2. Design Tokens (Final)

### 2.1 Colour

The palette is intentionally restrained. Five semantic roles, plus chart accents.

| Role | Light | Dark | Use |
|---|---|---|---|
| Surface | `#FAFAF7` | `#0E0F12` | Page background |
| Surface raised | `#FFFFFF` | `#16181D` | Cards, tables |
| Text primary | `#0E1116` | `#E6E8EC` | Body |
| Text secondary | `#5A6270` | `#8B93A1` | Captions, hints |
| Border | `#E6E4DE` | `#23262D` | Dividers |
| Accent | `#2B5BD7` | `#5C82E6` | Primary action, links |
| Warning | `#B8730F` | `#E0972E` | Reviewable but non-blocking |
| Critical | `#B0312C` | `#E25852` | Breach, error |
| Positive | `#1F7A4A` | `#3FA972` | Pass, completed |

Charts use a 7-colour categorical palette tuned for colour-blind safety. Heatmaps use a single-hue sequential scale; diverging palettes only where a true mid-point exists (e.g., over/under budget).

### 2.2 Type

| Token | Family | Size | Weight | Use |
|---|---|---|---|---|
| Display | Inter / system | 28px | 600 | Page titles |
| Heading | Inter / system | 18px | 600 | Section heads |
| Body | Inter / system | 14px | 400 | Default |
| Caption | Inter / system | 12px | 400 | Metadata |
| Numeric | JetBrains Mono / system mono | 14px | 400 | All quantitative cells |

Numeric values render in a monospace font with tabular figures so columns align without manual tweaking. Negatives use a minus sign, not parentheses (configurable per tenant; some prefer accounting style).

### 2.3 Spacing

4px grid. Common rhythms: 4, 8, 12, 16, 24, 32, 48. Table row height defaults to 32px; dense tables 28px.

### 2.4 Motion

- Transitions: 120ms ease-out for everyday state changes
- Loading shimmer: 1.5s subtle gradient
- No bouncing, no overshoot, no celebration animations
- Reduced-motion preference fully respected; all non-essential motion suppressed

---

## 3. State Coverage

A common gap in functional builds: missing states. The polish pass ensures **every view has all five states** unless there is a documented reason it does not.

### 3.1 The Five States

| State | When |
|---|---|
| **Loading** | Data fetch in progress |
| **Empty** | Successful fetch returned nothing |
| **Partial** | Some data present but expected dimensions missing |
| **Error** | Fetch failed |
| **Stale** | Data older than expected; user should know |

### 3.2 State Specifications

**Loading.** Skeleton rows that match the eventual layout — same column widths, same alignment. Never a centred spinner on a full page. Skeleton displays only after 200ms (avoids flicker on fast loads).

**Empty.** A short, specific sentence describing why it's empty, plus the next action. Never a generic "No data". Examples:

- Workpaper list: *"No workpapers prepared for this reporting date. Create one to begin."*
- Exception queue: *"No open exceptions. Recheck after the next data load."*
- Conversational history: *"Start a conversation — ask about the latest LCR movement, an open exception, or a regulatory rule."*

**Partial.** A line at the top of the view explicitly stating what is missing and what was loaded. Example: *"Showing 4 of 6 portfolios — Retail and Treasury position files have not arrived yet for 2026-03-31."*

**Error.** Plain language explanation, the action that was being attempted, and what to do. Internal error code visible but not dominant; copy-to-clipboard for support. Never "Something went wrong" alone. Example: *"Couldn't load the LCR computation for 2026-03-31. The compute service responded with an internal error. Try again, or contact platform support with code ENGINE-4421-LCR."*

**Stale.** A small chip near the title showing the data's age relative to expected freshness. Examples: "as of 2 days ago", "running computation now…", "data load delayed".

### 3.3 State Audit

A polish pass deliverable is a checklist: every view, every state, present or explicitly waived.

---

## 4. Tables

Tables are the dominant primitive of this platform. They deserve disproportionate attention.

### 4.1 Specifications

- **Column alignment:** text left; numbers right; categorical chips left
- **Numeric formatting:** thousands separators per locale, decimals consistent within a column, negative styling consistent
- **Currency:** unit shown in column header, not in every cell (e.g., "Notional (₹ crore)")
- **Zero:** rendered as `—` for empty/null distinguishable from a true zero (true zero is `0` or `0.00`)
- **Large numbers:** truncated with a precise tooltip showing full value
- **Pinning:** first column pinnable; header row pinned by default on scroll
- **Sorting:** every column sortable except where it makes no sense; sort direction indicated with a subtle chevron
- **Filtering:** per-column filter accessible via a quiet icon; advanced filters via a sheet
- **Density toggle:** comfortable / compact, persisted per user per view
- **Selection:** checkbox column; bulk actions appear in a docked bar at the bottom when a selection exists
- **Resizable columns:** drag-resize, persisted per user
- **Export:** every table exports to Excel and CSV, with the same column order, names, and formatting as on screen

### 4.2 Drill-down

Every aggregated cell that can be drilled is visually marked (subtle dotted underline on the value). Click opens a panel showing the underlying rows; never navigates away.

### 4.3 Cell-Level Provenance

Hovering a regulatory number for ≥800ms shows a small popover:

- The compute function name and version
- The snapshot ID
- A link to the workpaper for that figure

This is the user-facing surface of the audit trail described in `Final_Build_Pack.md` §2.3.

---

## 5. Charts

### 5.1 Chart Inventory

The platform uses a tight chart vocabulary. Six types cover ≥95% of needs:

1. **Time series line** — ratio trends (LCR, CET1) over time
2. **Stacked bar** — composition over time (RWA by asset class)
3. **Horizontal bar** — ranked comparison (top 20 exposures)
4. **Waterfall** — variance attribution (drivers of CET1 change)
5. **Heatmap** — sensitivity grids (EVE under shock combinations)
6. **Sankey** — funding flows (deposit sources → asset uses)

Exotic chart types (radar, treemap, donut) require explicit approval.

### 5.2 Chart Specifications

- **Axes:** zero-baseline by default; non-zero baseline only with explicit annotation
- **Gridlines:** horizontal only, low contrast
- **Legend:** below the chart for time series; right for comparison
- **Tooltips:** show all series at the hovered x-position, formatted as in tables
- **Colour:** uses the categorical palette in §2.1; never relies on colour alone for distinction (line style or labels accompany)
- **Empty:** chart-shaped placeholder with the message in §3.2 conventions
- **Loading:** skeleton chart-shape
- **Export:** every chart exports to PNG (at 2x) and SVG; data behind the chart exports to CSV

### 5.3 Annotations

Charts support annotations for:

- Reporting date markers (vertical line + label)
- Policy events ("RBI repo rate change")
- Internal events ("Treasury reallocation")
- Threshold lines (regulatory minima)

Annotations come from a dedicated store, are editable by approved users, and are versioned.

---

## 6. The Conversational Surface

The conversational UI is the most distinctive interaction in the platform and deserves the most polish.

### 6.1 Placement

- Persistent slide-in panel from the right
- Keyboard shortcut: `⌘ K` opens; `Esc` closes
- Context-aware: when opened from a specific view, the conversation is seeded with that view's structured context

### 6.2 Interaction Model

- User types a question; Claude streams a response
- Streaming uses a subtle text reveal; no character-by-character animation
- When Claude is calling a Python compute function, a chip appears: *"Calculating LCR for 2026-03-31…"* — the user always knows when a number is being produced deterministically vs. when the reasoning layer is explaining
- Responses include inline citations to specific compute outputs (clickable) and to underlying positions (drilldown opens in the main view)
- Suggested follow-ups appear as quiet chips below each response

### 6.3 Trust Affordances

The user always sees:

- The model version answering
- The compute runs the answer depends on (collapsed by default; expand to view)
- A "show me how this number was computed" link on every figure in the response
- A flag-for-review button for any response a user wants escalated

### 6.4 Failure Modes

When Claude:

- Cannot answer due to missing structured data: response is "I don't have the data to answer that — the [X] computation hasn't run for this date. Run it now?"
- Disagrees with available data: response defers to compute; never overrides
- Hits rate limits: clear message, time to retry, no silent failure
- Produces a response that fails schema validation: surfaced as a system error, never partially rendered

### 6.5 History & Privacy

- Conversation history per user, searchable
- "New conversation" clears context cleanly
- All conversations logged for audit; user notified in onboarding
- Export conversation to PDF preserves citations and timestamps

---

## 7. Forms & Workpapers

### 7.1 Workpaper Editor

The workpaper editor is where preparers tie regulatory figures to source data and add narrative.

- Two-pane layout: cells on the left, narrative + supporting docs on the right
- Cells auto-populated from compute layer are marked with a small lock icon
- Cells edited manually require a justification comment
- Narrative supports Claude-assisted drafting; the assistant insertion is visually distinct (subtle background tint) until accepted
- Sign-off bar at the top shows: prepared by, reviewed by, approved by, with timestamps

### 7.2 Form Patterns

- Labels above fields; never beside (better for translation, mobile)
- Required fields marked with `*`; optional fields not marked
- Validation: inline, after blur, never on every keystroke
- Save state: explicit "Save draft" + autosave every 10s with a "Saved 12:04" timestamp
- Destructive actions: confirm only when truly destructive; "Are you sure?" overuse trains users to click through

---

## 8. Navigation

### 8.1 Information Architecture

Top-level nav:

1. **Today** — daily working view, exceptions, alerts
2. **Workpapers** — preparation surface for filings
3. **Reports** — finalised regulatory and management outputs
4. **Analytics** — exploratory: ALM, stress, drill-down
5. **Reference** — counterparties, products, policies
6. **Admin** — users, roles, audit log

### 8.2 Breadcrumbs

Every view shows a breadcrumb. Reporting date is a chip in the breadcrumb, clickable, opens a date picker.

### 8.3 Search

Global search reachable via `⌘ /`. Searches across:

- Counterparties
- Positions
- Workpapers
- Reports
- Policies
- Recent conversations

Results grouped by type, ranked by recency + relevance.

---

## 9. Notifications & Alerts

Three notification severities:

| Severity | Use | Visual |
|---|---|---|
| **Info** | Status updates ("Snapshot frozen for 2026-03-31") | Quiet chip, dismissible |
| **Warning** | Reviewable but non-blocking ("LCR forecast trends down 5% over 5 days") | Coloured chip, persistent until acknowledged |
| **Critical** | Breach or filing-blocker ("CET1 buffer breach: 8.95% vs. 9.0% minimum") | Inline banner + email + (configurable) PagerDuty |

Critical alerts have runbooks per `Phase27.md` §7. The runbook link is on the alert itself.

---

## 10. Print & Export

Anything visible on screen must be exportable in a form suitable for distribution:

- **PDF:** print stylesheet hides chrome, expands collapsed sections, paginates tables, places page numbers and confidentiality marks
- **Excel:** preserves grouping, formatting, formulas where possible; reasoning narrative becomes a sheet of its own
- **CSV:** raw values, no formatting, for downstream tooling
- **Image (PNG/SVG):** for individual charts

All exports carry: report name, reporting date, generated-at timestamp, user, snapshot ID. Demo exports carry the demo watermark per `Demo_Mode.md`.

---

## 11. Accessibility

Phase 27 target: WCAG 2.1 AA.

- All interactive elements keyboard-reachable
- Focus rings visible and clear; never removed
- Colour contrast meets AA on all text (verified with automated tooling)
- All charts have an accessible data-table fallback
- Form errors announced to screen readers
- All icons that carry meaning have text labels or `aria-label`
- Reduced-motion respected
- Zoom to 200% does not break layouts

Screen-reader testing performed against the three guided demo tours.

---

## 12. Microcopy

A pass over every piece of UI text. Principles:

- **Be specific.** "Couldn't load LCR" not "Error loading data".
- **Name actions concretely.** "Lock for filing" not "Submit".
- **Avoid jargon where simpler words work.** "Run computation" beats "Execute compute pipeline".
- **Keep regulatory terms precise.** "RWA" stays "RWA"; do not paraphrase a regulatory term into something less correct.
- **Don't apologise.** "Try again" beats "Sorry, please try again".
- **Use sentence case** for everything except product names and acronyms.
- **No exclamation points** outside of confirmation success states.

A microcopy review precedes go-live; the conversational layer can assist with rewrites but every change is human-reviewed.

---

## 13. Polish Acceptance Criteria

The polish pass is complete when:

1. State audit complete: every view has all required states or documented exemption
2. Table specification compliance: all tables conform to §4
3. Chart specification compliance: all charts conform to §5
4. Conversational UI conforms to §6 in full
5. WCAG 2.1 AA pass via automated + manual review
6. Microcopy review complete; no "Something went wrong", no orphan strings
7. All export formats produce well-formed outputs
8. Keyboard-only navigation tested through three core flows
9. Reduced-motion verified
10. Demo tours run cleanly with no visual glitches

---

## 14. Companion Documents

- `Final_Build_Pack.md` — overall architecture; component reference
- `Phase27.md` — Workstream G consumes this document
- `Demo_Mode.md` — demo-mode exercising of polished UI
- `Deployment_Checklist.md` — UI polish items appear in the pre-go-live gate

---

*End of UI Polish specification.*
