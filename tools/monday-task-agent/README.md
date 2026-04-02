# monday-task-agent

A CLI tool that converts loosely described CTO work into structured task cards and posts them to Monday.com.

Built on the [SEC Framework](../../docs/framework.md) (Strategy, Execution, Culture) — a practical taxonomy for technology leadership work.

## What it does

1. You describe work in plain language
2. The agent classifies it against the SEC Framework, assigns an ABCDE priority, and estimates Pomodoros
3. You review the drafted card and confirm before anything is posted
4. The agent creates the item on your Monday.com board via GraphQL

## Setup

```bash
cd tools/monday-task-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in your API keys and board ID
```

### Required environment variables

| Variable            | Description                           |
| ------------------- | ------------------------------------- |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude          |
| `MONDAY_API_KEY`    | Monday.com API v2 token               |
| `MONDAY_BOARD_ID`   | Target board ID (from your board URL) |

### Company context (optional but recommended)

Copy the example template and fill in your specifics:

```bash
cp ../../.claude/skills/monday-task-agent/context/company.example.md \
   ../../.claude/skills/monday-task-agent/context/company.md
```

This file is gitignored. It gives the agent context about your active workstreams, team, and priorities so classification and prioritization are more accurate.

## Usage

```bash
source .venv/bin/activate
source .env
python agent.py
```

Then describe your work:

```text
> Review the NLP vendor's API rate limit changes and decide if we need to renegotiate

Task Title: Review NLP vendor API rate limit changes
Objective: Assess updated rate limits and determine whether renegotiation is needed to maintain pipeline throughput.
SEC Tag: Strategy.Partnership Strategy.Data licensing negotiation
Priority: B
Estimated Time: 2 Pomodoros (50 minutes)
...

Post it? (yes/edit/skip)
```

## Project structure

```bash
tools/monday-task-agent/
├── agent.py                # CLI entrypoint and conversation loop
├── integrations/
│   └── monday.py           # Monday.com GraphQL tool definition + implementation
├── .env.example            # API key template
└── README.md               # This file
```

## How it works

- **Intelligence layer**: The SEC Framework taxonomy, classification rules, and behavioral contract live in `.claude/skills/monday-task-agent/SKILL.md` — loaded as the system prompt
- **Company context**: Private context (team, workstreams, priorities) loaded from `context/company.md` at runtime
- **Tool use**: The agent uses Anthropic's tool-use API to call `monday_create_task` only after explicit user confirmation
