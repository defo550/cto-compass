"""
Monday.com GraphQL integration for the monday-task-agent.

Provides the monday_create_task tool definition (for the Anthropic tool-use
schema) and the implementation that executes the GraphQL mutation against
the Monday.com API.
"""

import json
import os
import re

import requests

MONDAY_API_URL = "https://api.monday.com/v2"

# Monday.com column value format by type
COLUMN_FORMAT_HINTS: dict[str, str] = {
    "long_text": '{"text": "content"}',
    "text": '"content"',
    "numbers": '"123"',
    "status": '{"label": "Label"}',
    "date": '{"date": "2026-01-15"}',
    "checkbox": '{"checked": "true"}',
    "tags": '{"tag_ids": [TAG_ID]}  — pass tag names as strings, they will be resolved automatically',
}


# ---------------------------------------------------------------------------
# Board column discovery
# ---------------------------------------------------------------------------

def query_board_columns(board_id: str) -> list[dict]:
    """Fetch the column schema for a Monday.com board.

    Args:
        board_id: The board to query.

    Returns:
        List of dicts, each with 'id', 'title', and 'type' keys.

    Raises:
        RuntimeError: If the API call fails or MONDAY_API_KEY is missing.
    """
    api_key = os.environ.get("MONDAY_API_KEY")
    if not api_key:
        raise RuntimeError("MONDAY_API_KEY environment variable is not set.")

    query = f'{{ boards(ids: [{board_id}]) {{ columns {{ id title type }} }} }}'

    response = requests.post(
        MONDAY_API_URL,
        json={"query": query},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Monday.com API returned {response.status_code}: {response.text}"
        )

    data = response.json()

    if "errors" in data:
        error_msgs = "; ".join(e.get("message", str(e)) for e in data["errors"])
        raise RuntimeError(f"Monday.com GraphQL error: {error_msgs}")

    boards = data["data"]["boards"]
    if not boards:
        raise RuntimeError(f"Board {board_id} not found.")

    return boards[0]["columns"]


# ---------------------------------------------------------------------------
# Tool definition (Anthropic tool-use schema)
# ---------------------------------------------------------------------------

_BASE_TOOL_DEFINITION: dict = {
    "name": "monday_create_task",
    "description": (
        "Create a task item on a Monday.com board. "
        "Called only after the user explicitly confirms the drafted card."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "board_id": {
                "type": "string",
                "description": "The Monday.com board ID to create the item on.",
            },
            "item_name": {
                "type": "string",
                "description": "The task title (verb + object, plain language).",
            },
            "column_values": {
                "type": "object",
                "description": (
                    "Column values to set on the new item. Keys are Monday.com "
                    "column IDs; values follow Monday.com's column value format."
                ),
            },
        },
        "required": ["board_id", "item_name"],
    },
}


def build_tool_definition(columns: list[dict]) -> dict:
    """Return a tool definition with column info embedded in the description.

    Args:
        columns: Column schema from query_board_columns().

    Returns:
        A copy of the tool definition with column details in column_values description.
    """
    col_descriptions = []
    for col in columns:
        col_type = col["type"]
        if col_type == "name":
            continue  # item_name handles this
        fmt = COLUMN_FORMAT_HINTS.get(col_type, '"value"')
        col_descriptions.append(
            f"  - {col['id']} ({col['title']}, {col_type}): {fmt}"
        )

    if not col_descriptions:
        return _BASE_TOOL_DEFINITION

    col_desc_text = (
        "Column values to set on the new item. Keys are Monday.com column IDs. "
        "Available columns:\n" + "\n".join(col_descriptions)
    )

    tool = json.loads(json.dumps(_BASE_TOOL_DEFINITION))
    tool["input_schema"]["properties"]["column_values"]["description"] = col_desc_text
    return tool


# ---------------------------------------------------------------------------
# Tag resolution
# ---------------------------------------------------------------------------

def format_sec_tags(sec_tag: str) -> list[str]:
    """Split a dotted SEC tag into individually formatted Monday.com tag names.

    Formatting conventions:
        - Domain (level 1): Capitalized — e.g. "Execution"
        - Focus Area (level 2): PascalCase, no special characters — e.g. "ProductEngineeringDelivery"
        - Activity (level 3): Capitalize first word, kebab-case — e.g. "Technical-debt-reduction"

    Args:
        sec_tag: Dotted SEC tag like "Execution.Product & Engineering Delivery.Technical debt reduction"

    Returns:
        List of 1–3 formatted tag name strings.
    """
    parts = [p.strip() for p in sec_tag.split(".")]
    tags = []

    if len(parts) >= 1:
        tags.append(parts[0].capitalize())

    if len(parts) >= 2:
        words = re.sub(r"[^a-zA-Z\s]", "", parts[1]).split()
        tags.append("".join(w.capitalize() for w in words))

    if len(parts) >= 3:
        words = parts[2].split()
        if words:
            formatted = [words[0].capitalize()] + [w.lower() for w in words[1:]]
            tags.append("-".join(formatted))

    return tags


def create_or_get_tag(tag_name: str) -> int:
    """Find or create a Monday.com tag by name.

    Args:
        tag_name: A single formatted tag name (e.g. "EXECUTION").

    Returns:
        The Monday.com tag ID (integer).

    Raises:
        RuntimeError: If the API call fails.
    """
    api_key = os.environ.get("MONDAY_API_KEY")
    if not api_key:
        raise RuntimeError("MONDAY_API_KEY environment variable is not set.")

    safe_name = tag_name.replace('"', '\\"')
    query = f'mutation {{ create_or_get_tag(tag_name: "{safe_name}") {{ id }} }}'

    response = requests.post(
        MONDAY_API_URL,
        json={"query": query},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Monday.com API returned {response.status_code}: {response.text}"
        )

    data = response.json()

    if "errors" in data:
        error_msgs = "; ".join(e.get("message", str(e)) for e in data["errors"])
        raise RuntimeError(f"Monday.com GraphQL error: {error_msgs}")

    return int(data["data"]["create_or_get_tag"]["id"])


def resolve_tags_in_column_values(
    column_values: dict, columns: list[dict]
) -> dict:
    """Resolve tag name strings to Monday.com tag IDs in column_values.

    For any column of type 'tags', replaces string tag names in the tag_ids
    list with actual Monday.com tag IDs via create_or_get_tag.

    Args:
        column_values: The column values dict from the model.
        columns: Column schema from query_board_columns().

    Returns:
        Updated column_values with resolved tag IDs.
    """
    tag_column_ids = {col["id"] for col in columns if col["type"] == "tags"}

    for col_id in tag_column_ids:
        if col_id not in column_values:
            continue

        col_val = column_values[col_id]
        if not isinstance(col_val, dict) or "tag_ids" not in col_val:
            continue

        # Expand dotted SEC tags into individual formatted tag names
        expanded_names: list[str] = []
        for tag in col_val["tag_ids"]:
            if isinstance(tag, str) and "." in tag:
                expanded_names.extend(format_sec_tags(tag))
            elif isinstance(tag, str):
                expanded_names.append(tag)
            else:
                expanded_names.append(tag)

        resolved_ids = []
        for tag in expanded_names:
            if isinstance(tag, str):
                resolved_ids.append(create_or_get_tag(tag))
            else:
                resolved_ids.append(tag)

        column_values[col_id] = {"tag_ids": resolved_ids}

    return column_values


# ---------------------------------------------------------------------------
# Implementation
# ---------------------------------------------------------------------------

def monday_create_task(
    board_id: str,
    item_name: str,
    column_values: dict | None = None,
    columns: list[dict] | None = None,
) -> dict:
    """Create an item on a Monday.com board via the GraphQL API.

    Args:
        board_id: Target board ID.
        item_name: Display name for the new item.
        column_values: Optional mapping of column IDs to values.
        columns: Optional column schema for resolving tags-type columns.

    Returns:
        dict with at least {"item_id": str} on success.

    Raises:
        RuntimeError: If the API call fails or MONDAY_API_KEY is missing.
    """
    api_key = os.environ.get("MONDAY_API_KEY")
    if not api_key:
        raise RuntimeError("MONDAY_API_KEY environment variable is not set.")

    # Resolve tag names → tag IDs for any tags-type columns
    if column_values and columns:
        column_values = resolve_tags_in_column_values(column_values, columns)

    # Monday.com expects column_values as a JSON-encoded string inside the
    # GraphQL mutation. Double-serialize: inner dumps → JSON object string,
    # outer dumps → escaped string literal for the GraphQL query.
    col_values_str = json.dumps(json.dumps(column_values)) if column_values else '"{}"'

    # Escape double quotes in item_name for safe embedding in the query string.
    safe_name = item_name.replace('"', '\\"')

    query = (
        "mutation { create_item ("
        f'board_id: {board_id}, '
        f'item_name: "{safe_name}", '
        f"column_values: {col_values_str}"
        ") { id } }"
    )

    response = requests.post(
        MONDAY_API_URL,
        json={"query": query},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Monday.com API returned {response.status_code}: {response.text}"
        )

    data = response.json()

    if "errors" in data:
        error_msgs = "; ".join(e.get("message", str(e)) for e in data["errors"])
        raise RuntimeError(f"Monday.com GraphQL error: {error_msgs}")

    return {"item_id": data["data"]["create_item"]["id"]}
