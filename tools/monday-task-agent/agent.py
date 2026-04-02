"""
monday-task-agent — CLI entrypoint and conversation loop.

Converts loosely described CTO work into structured SEC-tagged task cards
and posts them to Monday.com via the Anthropic API and Monday.com GraphQL API.

Flow:
    1. Load company context from .claude/skills/monday-task-agent/context/company.md
    2. Build system prompt from SKILL.md + company context
    3. Enter conversation loop: user describes work → agent drafts card → user confirms → post
    4. Tool call to monday_create_task triggers the Monday.com integration

Usage:
    python agent.py
"""

import json
import os
import sys

import anthropic

from integrations.monday import (
    COLUMN_FORMAT_HINTS,
    build_tool_definition,
    monday_create_task,
    query_board_columns,
)

MODEL = "claude-sonnet-4-20250514"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SKILL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", ".claude", "skills", "monday-task-agent", "SKILL.md",
)

COMPANY_CONTEXT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", ".claude", "skills", "monday-task-agent", "context", "company.md",
)


def load_system_prompt(columns: list[dict] | None = None) -> str:
    """Read SKILL.md and company context, combine into a system prompt."""
    try:
        with open(SKILL_PATH) as f:
            skill = f.read()
    except FileNotFoundError:
        print(f"Error: SKILL.md not found at {SKILL_PATH}")
        sys.exit(1)

    company_context = ""
    try:
        with open(COMPANY_CONTEXT_PATH) as f:
            company_context = f.read().strip()
    except FileNotFoundError:
        pass

    prompt = skill
    if company_context:
        prompt += "\n\n---\n\n## Company Context\n\n" + company_context

    board_id = os.environ.get("MONDAY_BOARD_ID", "")
    if board_id:
        prompt += f"\n\n---\n\nMonday.com Board ID: {board_id}"

    if columns:
        prompt += "\n\n---\n\n## Monday.com Board Columns\n\n"
        prompt += (
            "When calling monday_create_task, use these column IDs in column_values. "
            "You MUST populate all relevant fields — not just item_name.\n\n"
        )
        prompt += "| Column ID | Title | Type | Format |\n"
        prompt += "|-----------|-------|------|--------|\n"
        for col in columns:
            if col["type"] == "name":
                continue
            fmt = COLUMN_FORMAT_HINTS.get(col["type"], '"value"')
            prompt += f"| `{col['id']}` | {col['title']} | {col['type']} | `{fmt}` |\n"

        prompt += (
            "\n**Tags column:** For any `tags`-type column, pass the full dotted SEC Tag "
            'as a single string inside tag_ids — e.g. `{"tag_ids": ["Strategy.Technology Planning.Roadmaps"]}`. '
            "The agent automatically splits it into separate tags per level "
            "(STRATEGY, TechnologyPlanning, Roadmaps) and resolves them to Monday.com tag IDs.\n"
        )

    return prompt


def build_tools(columns: list[dict] | None = None) -> list[dict]:
    """Return the tool definitions list exposed to the Anthropic messages API."""
    if columns:
        return [build_tool_definition(columns)]
    return [build_tool_definition([])]


def handle_tool_call(tool_name: str, tool_input: dict, columns: list[dict] | None = None) -> str:
    """Dispatch a tool call from the model to the appropriate integration."""
    if tool_name != "monday_create_task":
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    try:
        board_id = tool_input.get("board_id") or os.environ.get("MONDAY_BOARD_ID", "")
        result = monday_create_task(
            board_id=board_id,
            item_name=tool_input["item_name"],
            column_values=tool_input.get("column_values"),
            columns=columns,
        )
        return json.dumps(result)
    except RuntimeError as e:
        return json.dumps({"error": str(e)})


def conversation_loop() -> None:
    """Run the interactive conversation loop.

    Steps per turn:
        - Collect user input
        - Send messages to Anthropic API with system prompt + tools
        - If response contains a tool_use block, execute and feed result back
        - If response contains text, print it and wait for next input
        - Exit on 'quit' / 'exit' / Ctrl-C
    """
    board_id = os.environ.get("MONDAY_BOARD_ID", "")

    columns = None
    if board_id:
        try:
            columns = query_board_columns(board_id)
            print(f"Connected to Monday.com board — discovered {len(columns)} columns.")
        except RuntimeError as e:
            print(f"Warning: Could not fetch board columns: {e}")
            print("Continuing without column mapping — only item name will be set.\n")

    system_prompt = load_system_prompt(columns)
    tools = build_tools(columns)
    client = anthropic.Anthropic()
    messages: list[dict] = []

    print("Monday Task Agent — describe your work, and I'll draft a task card.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye.")
            break

        messages.append({"role": "user", "content": user_input})

        # Inner loop: handle tool-use round-trips until model returns text only
        while True:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            tool_use_blocks = [b for b in assistant_content if b.type == "tool_use"]

            # Print any text blocks in this response
            for block in assistant_content:
                if block.type == "text" and block.text.strip():
                    print(f"\n{block.text}\n")

            if not tool_use_blocks:
                break

            # Execute tool calls and feed results back
            tool_results = []
            for tool_block in tool_use_blocks:
                result_str = handle_tool_call(tool_block.name, tool_block.input, columns)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result_str,
                })

            messages.append({"role": "user", "content": tool_results})


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    """Validate environment, load context, and start the conversation loop."""
    required_vars = ["ANTHROPIC_API_KEY", "MONDAY_API_KEY", "MONDAY_BOARD_ID"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your values.")
        sys.exit(1)

    conversation_loop()


if __name__ == "__main__":
    main()
