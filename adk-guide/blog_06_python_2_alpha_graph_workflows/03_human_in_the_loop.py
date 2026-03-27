"""
Blog 06 — ADK Python 2.0 Alpha: Graph-Based Workflows (March 2026)
Example 3: Human-in-the-Loop (Tool Confirmation)

Source: https://google.github.io/adk-docs/

ADK 2.0 supports guarded execution: before an agent calls a sensitive tool,
it pauses and waits for explicit human approval. This is critical for
production systems where agents take irreversible actions.

Use case: An agent that can send emails or make API calls — requires approval first.
"""

import asyncio
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


# ── Sensitive tools that require confirmation ─────────────────────────────────
async def send_email(
    to: str,
    subject: str,
    body: str,
    tool_context: ToolContext,
) -> dict:
    """
    Sends an email to the specified recipient.
    ⚠️ This tool requires human confirmation before execution.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content

    Returns:
        Confirmation with message_id and timestamp
    """
    # In production, integrate with SendGrid, Gmail API, etc.
    print(f"\n📧 Email would be sent:")
    print(f"   To:      {to}")
    print(f"   Subject: {subject}")
    print(f"   Body:    {body[:100]}...")

    return {
        "status": "sent",
        "message_id": "msg_abc123",
        "recipient": to,
        "timestamp": "2026-03-27T10:30:00Z",
    }


async def delete_record(
    record_id: str,
    table: str,
    tool_context: ToolContext,
) -> dict:
    """
    Permanently deletes a record from the database.
    ⚠️ This is a DESTRUCTIVE operation requiring human confirmation.

    Args:
        record_id: The unique ID of the record to delete
        table: The database table name

    Returns:
        Confirmation of deletion
    """
    print(f"\n🗑️  Record deletion requested:")
    print(f"   Table:     {table}")
    print(f"   Record ID: {record_id}")

    return {
        "status": "deleted",
        "record_id": record_id,
        "table": table,
        "timestamp": "2026-03-27T10:30:00Z",
    }


def read_database(query: str) -> list[dict]:
    """
    Reads records from the database (safe, no confirmation needed).

    Args:
        query: A description of what records to retrieve

    Returns:
        List of matching records
    """
    # Mock data
    return [
        {"id": "rec_001", "name": "Alice Johnson", "email": "alice@example.com", "status": "active"},
        {"id": "rec_002", "name": "Bob Smith", "email": "bob@example.com", "status": "inactive"},
    ]


# ── Confirmation callback ─────────────────────────────────────────────────────
async def require_confirmation(
    tool_name: str,
    tool_args: dict[str, Any],
    tool_context: ToolContext,
) -> bool:
    """
    Called before any tool execution. Returns True to proceed, False to cancel.
    In production, this would show a UI prompt or send a Slack approval request.
    """
    SENSITIVE_TOOLS = {"send_email", "delete_record"}

    if tool_name not in SENSITIVE_TOOLS:
        return True  # safe tools proceed automatically

    print(f"\n⚠️  CONFIRMATION REQUIRED")
    print(f"   Tool: {tool_name}")
    print(f"   Args: {tool_args}")
    print("   Type 'yes' to approve, anything else to cancel: ", end="")

    response = input().strip().lower()
    approved = response == "yes"

    if approved:
        print("   ✓ Approved — executing tool")
    else:
        print("   ✗ Cancelled — tool will not execute")

    return approved


# ── Agent with sensitive tools ────────────────────────────────────────────────
admin_agent = LlmAgent(
    name="admin_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "You are an administrative assistant with access to database and email tools. "
        "Use read_database to look up records safely. "
        "Use send_email when asked to contact someone. "
        "Use delete_record ONLY when explicitly asked to delete data. "
        "Always explain what you're about to do before doing it."
    ),
    description="Administrative agent with database and email capabilities.",
    tools=[
        FunctionTool(send_email),
        FunctionTool(delete_record),
        FunctionTool(read_database),
    ],
    # before_tool_callback fires before EVERY tool call
    before_tool_callback=require_confirmation,
)


# ── Run demo ───────────────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="admin_app", user_id="user_01"
    )
    runner = Runner(
        agent=admin_agent,
        app_name="admin_app",
        session_service=session_service,
    )

    print("=== Human-in-the-Loop Demo ===")
    print("Sensitive tools require 'yes' confirmation.\n")

    queries = [
        "Show me all users in the database.",
        "Send an email to alice@example.com with subject 'Welcome Back' and body 'We miss you! Come check out our new features.'",
    ]

    for query in queries:
        print(f"User: {query}")
        async for event in runner.run_async(
            user_id="user_01",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=query)]
            ),
        ):
            if event.is_final_response():
                print(f"Agent: {event.content.parts[0].text}\n")


if __name__ == "__main__":
    asyncio.run(main())
