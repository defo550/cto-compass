# CTO Compass - CLAUDE.md

## Project Overview

CTO Compass is a public portfolio and tooling repository built around the S.E.C. (Strategy-Execution-Culture) Framework — a practical system for technology leadership in small-to-medium companies where the CTO wears CTO/CIO/CISO hats simultaneously.

The repository serves two purposes:

1. **Framework documentation** — the SEC Framework as a reference, tagging system, and career development tool for CTOs
2. **Tools** — executable implementations of the framework, starting with the `monday-task-agent` CLI

This is a public repository. No company-specific or proprietary information belongs in committed files. Sensitive context lives in gitignored local files.

---

## Repository Structure

```bash
cto-compass/
├── CLAUDE.md                              # This file
├── .claude/
│   └── skills/
│       └── monday-task-agent/
│           ├── SKILL.md                   # Agent skill definition (committed)
│           └── context/
│               ├── company.example.md     # Public template (committed)
│               └── company.md             # Private context (gitignored)
├── docs/
│   ├── framework.md                       # Complete SEC framework guide
│   ├── quickstart.md                      # Getting started guide
│   ├── examples.md                        # Real-world tagging examples
│   └── implementation.md                  # How to implement the framework
├── tools/
│   └── monday-task-agent/
│       ├── agent.py                       # CLI entrypoint
│       ├── integrations/
│       │   └── monday.py                  # Monday.com GraphQL tool definition
│       ├── requirements.txt               # Python dependencies
│       ├── .env.example                   # API key template (no secrets)
│       └── README.md                      # Portfolio narrative for this tool
├── mindmap.mermaid                        # SEC framework visualization
├── README.md                              # Public-facing project overview
└── LICENSE
```

---

## SEC Framework

The core of this repository. Three domains, each with focus areas and activities:

**Strategy** — work that shapes direction

- Technology Planning, Market Positioning, Partnership Strategy, Stakeholder Management

**Execution** — work that delivers results

- Data & Infrastructure, Security & Compliance, Product & Engineering Delivery, Business Operations

**Culture** — work that builds people

- Team Development, Personal Development

Tagging format: `Domain.Focus Area.Activity`
Example: `Execution.Product & Engineering Delivery.Technical debt reduction`

Full taxonomy in `docs/framework.md`. Real-world examples in `docs/examples.md`.

---

## Tools

### monday-task-agent

A CLI tool that converts loosely described work into structured SEC-tagged task cards and posts them to Monday.com via GraphQL API.

**Interaction pattern**: think → act → confirm

- User describes work in natural language
- Agent classifies against SEC Framework, estimates Pomodoros, assigns ABCDE priority
- User reviews and confirms before anything is posted

**Key files:**

- `.claude/skills/monday-task-agent/SKILL.md` — the intelligence layer; system prompt and reasoning context
- `tools/monday-task-agent/agent.py` — CLI entrypoint and conversation loop
- `tools/monday-task-agent/integrations/monday.py` — Monday.com GraphQL tool definition

**Runtime dependencies:**

- Python 3.10+
- `anthropic` and `requests` packages
- `ANTHROPIC_API_KEY` and `MONDAY_API_KEY` environment variables
- `.claude/skills/monday-task-agent/context/company.md` (local only, gitignored)

---

## Coding Standards & Privacy

Public repository. Keep it lightweight:

- Main should always be in a clean, readable state
- Commit messages should be descriptive enough to scan in GitHub history
- Feature branches for new tools (e.g. `feature/monday-task-agent`)
- Small commits preferred but not required
- No company names, client names, or internal strategy details in committed files
- No API keys or credentials anywhere in the repo
- Company-specific context belongs only in `.claude/skills/monday-task-agent/context/company.md` (gitignored)
- Use `company.example.md` as the public-facing template

**Gitignored sensitive paths:**

```bash
.claude/skills/monday-task-agent/context/company.md
.env
```

---

## Key Principles

1. **The framework is the prompt** — SEC taxonomy, ZTD conventions, and priority logic are expressed as model context, not application code
2. **Practical over theoretical** — every element emerged from real CTO experience
3. **Portfolio narrative matters** — tools live alongside the frameworks they implement; code and methodology tell a coherent story together
4. **Public by design** — generic enough for any CTO to fork and adapt with their own `company.md`
