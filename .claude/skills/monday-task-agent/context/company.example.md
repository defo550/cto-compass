# Company Context — company.example.md

> Copy this file to `context/company.md` and fill in your details.
> `context/company.md` is gitignored and never committed to the repository.

---

## Company Overview

**Company name**: [Your company name]

**Industry**: [e.g. healthcare analytics, fintech, SaaS]

**Description**: [One or two sentences describing what the company does and who it serves.]

**Stage**: [e.g. seed, series A, growth — informs how the agent weights strategic vs. execution work]

---

## CTO Role Context

**Direct reports**: [List or describe — informs D-priority (delegate) suggestions]

**Teams overseen**: [e.g. engineering, data science, product]

**Key client or stakeholder segments**: [e.g. enterprise, mid-market, internal stakeholders]

---

## Strategic Priorities

**Primary objective for this year**:
[e.g. "Grow share of market to X%" or "Achieve SOC 2 Type II certification"]

**Current OKRs** (summarized):

- [Objective 1 and its key results]
- [Objective 2 and its key results]

These should inform Priority A/B assignments — tasks that directly advance an OKR should be weighted higher.

---

## Active Workstreams

List the 4–8 workstreams currently in flight. The agent uses these to resolve classification ambiguity and assess priority.

- [Workstream 1 — brief description]
- [Workstream 2 — brief description]
- [Workstream 3 — brief description]
- [Add as needed]

---

## Classification Notes

Use this section to capture any company-specific classification overrides or patterns the agent should learn. Examples:

- "[Activity X] at this company is always `Execution`, not `Strategy`, because..."
- "Client deliverable reviews map to `Execution.Product & Engineering Delivery`, not `Culture`"
- "Learning tasks only qualify as `Culture.Personal Development` if they include a concrete takeaway tied to an active workstream"

---

## Standing Meetings (Optional)

If you want the agent to be aware of recurring time commitments when estimating weekly capacity:

| Meeting                    | Cadence  | Duration      |
| -------------------------- | -------- | ------------- |
| [e.g. Engineering standup] | [Daily]  | [15 min]      |
| [e.g. 1:1s]                | [Weekly] | [30 min each] |
| [e.g. Executive sync]      | [Weekly] | [60 min]      |
