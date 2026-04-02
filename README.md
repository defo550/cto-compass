# CTO Compass 🧭

Navigate the complexities of technology leadership with the Strategy, Execution, and Culture (SEC) Framework — and the tools that put it into practice.

A practical guide and toolset for CTOs, aspiring technology leaders, and "accidental CTOs" who need structure in balancing Strategy, Execution, and Culture.

## Background & Purpose

This framework was developed through real experience as a co-founder and CTO of a healthcare technology company. It addresses the common challenge of the "accidental CTO" — technical professionals thrust into leadership without formal training or clear role definition.

CTO Compass provides:

- **Clear structure** for the often ambiguous CTO role
- **Time allocation guidance** to balance competing priorities
- **Practical tagging system** for tracking where your time actually goes
- **Career development roadmap** for aspiring technology leaders
- **Executable tools** that implement the framework in your daily workflow

---

## The SEC Framework

Technology leadership organized into three essential domains:

### Strategy

_Setting direction and external positioning_

- Technology Planning
- Market Positioning
- Partnership Strategy
- Stakeholder Management

### Execution

_Delivering results and operational excellence_

- Data & Infrastructure
- Security & Compliance
- Product & Engineering Delivery
- Business Operations

### Culture

_Building teams and organizational capability_

- Team Development
- Personal Development

---

## Tools

### monday-task-agent

A CLI tool that converts loosely described work into structured, SEC-tagged task cards and posts them directly to Monday.com.

**The interaction pattern is simple:**

```bash
python agent.py
```

```bash
> What are you working on?
  Review NLP engineer briefing on PED package frameworks

> Drafted:
  Title: Review NLP briefing on PED frameworks
  SEC: Execution.Product & Engineering Delivery.Product roadmap execution
  Priority: B | 2 Pomodoros
  Post it? (y/n/edit)

> y
  ✓ Posted — item #4821933
```

The tool applies the SEC Framework, ABCDE prioritization, and Pomodoro estimation automatically. The intelligence lives in the skill definition — the code is thin scaffolding around it.

**[→ monday-task-agent README](tools/monday-task-agent/README.md)**

---

## Quick Start

1. **Explore the Framework**: Read the [complete guide](docs/framework.md)
2. **See It Applied**: Check out [real-world tagging examples](docs/examples.md)
3. **Get Started Fast**: Follow the [quickstart guide](docs/quickstart.md)
4. **Implement in Your Role**: Use the [implementation roadmap](docs/implementation.md)
5. **Try the Tool**: Set up the [monday-task-agent](tools/monday-task-agent/README.md)

---

## Who This Is For

- **New CTOs** struggling with role definition and time management
- **Aspiring CTOs** preparing for technology leadership
- **Technical Founders** wearing multiple hats (CTO/CIO/CISO)
- **VP Engineers** transitioning to executive roles
- **Technology Leaders** seeking structure and benchmarks

---

## Project Structure

```bash
cto-compass/
├── CLAUDE.md                           # Project conventions for Claude Code
├── .claude/
│   └── skills/
│       └── monday-task-agent/
│           ├── SKILL.md                # Agent skill definition
│           └── context/
│               └── company.example.md  # Template for your private context
├── docs/
│   ├── framework.md                    # Complete framework guide
│   ├── quickstart.md                   # Getting started
│   ├── examples.md                     # Real-world tagging examples
│   └── implementation.md               # Implementation roadmap
├── tools/
│   └── monday-task-agent/
│       ├── agent.py                    # CLI entrypoint
│       ├── integrations/
│       │   └── monday.py               # Monday.com GraphQL integration
│       ├── requirements.txt            # Python dependencies
│       ├── .env.example                # API key template
│       └── README.md                   # Tool setup and usage guide
├── mindmap.mermaid                     # SEC framework visualization
└── README.md
```

---

## License

MIT — fork it, adapt it, build on it. If you use the framework, a mention is appreciated but not required.

---

## Acknowledgments

- Developed through the challenges of small company technology leadership
- Refined through startup accelerator programs and peer CTO discussions
- Battle-tested through platform crises, team scaling, and competing priorities

---

_The best compass is one you actually use. Start simple, track consistently, adjust as you grow._
