# BSM Platform — AI Safety Statement

> **Version:** v1.0-demo  
> **Audience:** Regulators, Compliance, Legal, Risk Committees, Investors

---

## Executive Summary

The FRBSM Platform uses AI (Claude by Anthropic) exclusively for **interpretation and communication** of financial data — never for computation. All regulatory ratios are calculated by deterministic Python engines. The AI layer is architecturally prevented from computing, modifying, or originating financial data.

---

## Core Safety Principles

### 1. Strict Computational Isolation

**The AI never computes financial ratios.**

This is not a policy — it is enforced by architecture:
- The AI reasoning layer (`apps/api/app/services/ai/`) has no imports from the financial engine layer
- The financial engine layer (`shared/engines/`) has no imports from Anthropic SDK
- Import boundary enforcement is validated by `import-linter` on every CI run

**What the AI reads:**
```
LCR result from engine: { lcr_ratio: 1.287, hqla_total: 45200000, net_cash_outflows: 35120000 }
```

**What the AI never does:**
```python
# This cannot happen — AI has no access to position data or engine logic
lcr_ratio = hqla / net_outflows  # Never
```

### 2. Read-Only AI Access

SAM (the AI advisor) cannot:
- Write to the database
- Modify positions, scenarios, or snapshots
- Submit regulatory filings
- Execute transactions
- Access external systems (blocked by tool sandboxing)

SAM can only:
- Call the 15 defined tools
- Read tool return values
- Generate text responses
- Raise alerts (which require human acknowledgement)

### 3. Human-in-the-Loop

**Every SAM output is advisory and requires human review.**

SAM generates recommendations, briefings, and analysis. He does not:
- Approve his own recommendations
- Execute his own suggested actions
- Modify data based on his analysis
- Auto-close regulatory issues

The platform enforces this by having no "execute" pathway for AI outputs. A human must read, review, and take action.

### 4. Tool Sandboxing

SAM accesses exactly 15 predefined tools. Each tool:
- Has a typed input schema (Pydantic validation)
- Reads only from specified database tables
- Returns structured JSON only
- Logs all calls and responses for audit

SAM cannot call arbitrary functions, execute SQL, or access filesystem resources.

### 5. Audit Trail

Every AI interaction is logged:
- Session ID, user, timestamp
- Every tool call: name, inputs, outputs
- Every response generated
- Autonomous monitoring runs

This audit trail is immutable and accessible to compliance teams.

---

## Regulatory Compliance Considerations

### Model Risk Management (SR 11-7)

| Requirement | How BSM Addresses It |
|------------|---------------------|
| Model Inventory | SAM is a single, documented AI model with defined scope |
| Validation | Engine outputs validated independently before AI sees them |
| Ongoing Monitoring | Tool call logs provide continuous monitoring of AI behaviour |
| Human Review | All SAM outputs require human review before action |

### MAS Technology Risk Guidelines

| Requirement | How BSM Addresses It |
|------------|---------------------|
| AI Explainability | Tool call timeline shows every data source SAM consulted |
| AI Accountability | Human override required; SAM cannot act autonomously |
| Model Governance | Separation of compute and AI layers enforces governance |

### PRA / FCA AI Guidance

The platform follows the FCA/PRA AI Principles:
- **Safety** — AI cannot compute financial data or take autonomous action
- **Fairness** — All entities receive the same engine-computed ratios
- **Transparency** — Tool audit trail available to regulators on request
- **Accountability** — All recommendations require human approval

---

## What SAM Is (and Is Not)

| SAM IS | SAM IS NOT |
|--------|-----------|
| An AI advisor for interpretation | A financial calculator |
| A briefing generator | A regulatory system |
| A monitoring assistant | A decision-making system |
| An analytical communicator | A trading system |
| Advisory (outputs require human review) | Autonomous (cannot act without human) |

---

## Known Limitations

1. **SAM's responses depend on data quality** — If position data is incorrect, SAM's analysis will be based on incorrect inputs. Data quality is a prerequisite.

2. **SAM may occasionally misinterpret edge cases** — For highly unusual balance sheet structures, SAM's contextualisation may not be optimal. Human review is always required.

3. **SAM cannot predict future market conditions** — SAM analyses historical and current data. Scenario analysis requires explicit human input through the Scenarios module.

4. **SAM's knowledge has a training cutoff** — For regulations enacted after the model's training cutoff, SAM should be prompted with the relevant regulatory text.

---

## Third-Party AI Provider

SAM is powered by **Anthropic Claude** via the Anthropic API.

- Anthropic maintains Claude's safety guidelines and RLHF training
- Data sent to the Anthropic API is limited to tool return values and user messages
- No position-level financial data (individual counterparty data) is sent to Anthropic — only aggregated engine results
- BSM Platform does not train Anthropic models on customer data

Refer to Anthropic's privacy policy and data processing agreement for specific data handling terms.

---

## Contact

For AI safety and model risk questions, contact:
- Chief Risk Officer
- Head of Model Risk
- Technology Risk Committee

*This statement reflects the platform at v1.0-demo. Update upon any change to the AI integration.*
