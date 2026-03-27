"""
Blog 04 — Building Agents with the ADK and the New Interactions API (Dec 2025)
Example 5: ADK Agent Using Interactions API as a Sub-Agent Tool

Source: https://developers.googleblog.com/building-agents-with-the-adk-and-the-new-interactions-api/

This shows how to plug Deep Research (or any Interactions API endpoint) into
an ADK multi-agent system as a sub-agent tool — the cleanest production pattern.

Architecture:
  User → ADK Coordinator → [Research Tool (Deep Research via Interactions API)]
                          → [Summary Agent]
                          → [Action Planner Agent]
"""

import os
import asyncio
import google.generativeai as genai
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


# ── Interactions API wrapper as an ADK tool ───────────────────────────────────
async def deep_research_tool(research_question: str) -> dict:
    """
    Conducts deep web research on a topic using the Gemini Deep Research agent.
    Use this for comprehensive research that requires searching multiple sources.

    Args:
        research_question: The research question or topic to investigate.

    Returns:
        A dictionary with 'report' (full research report) and 'interaction_id'.
    """
    client = genai.GenerativeModel("gemini-2.5-pro")

    # Submit as background task
    response = await client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": research_question}]}],
        config={
            "agent": "deep-research-pro-preview-12-2025",
            "background": True,
        },
    )

    interaction_id = response.interaction_id

    # Poll until complete
    import asyncio as _asyncio
    while True:
        status = await client.interactions.get_async(interaction_id)
        if status.state == "COMPLETED":
            report = status.candidates[0].content.parts[0].text
            return {"report": report, "interaction_id": interaction_id}
        elif status.state == "FAILED":
            return {"error": "Research failed", "interaction_id": interaction_id}
        await _asyncio.sleep(5)


def quick_search_tool(query: str) -> str:
    """
    Performs a quick single-turn question using Gemini for fast lookups.
    Use for simple factual questions that don't require deep research.

    Args:
        query: A simple factual question.

    Returns:
        A concise answer string.
    """
    client = genai.GenerativeModel("gemini-2.5-flash")
    # Synchronous call for the tool
    response = client.generate_content(query)
    return response.text


# ── Sub-agents ────────────────────────────────────────────────────────────────
action_planner = LlmAgent(
    name="action_planner",
    model="gemini-2.5-flash",
    description="Converts research findings into a concrete, prioritised action plan.",
    instruction=(
        "You are a strategic planner. Given research findings, create a "
        "concrete 5-step action plan with priorities, timelines, and success metrics."
    ),
)


# ── Main ADK coordinator ──────────────────────────────────────────────────────
coordinator = LlmAgent(
    name="research_coordinator",
    model="gemini-2.5-flash",
    instruction=(
        "You are a research and planning coordinator. For the user's request:\n"
        "1. Use 'deep_research_tool' for comprehensive, multi-source research.\n"
        "2. Use 'quick_search_tool' for simple factual lookups.\n"
        "3. Delegate to 'action_planner' to turn findings into an action plan.\n"
        "Always combine research insights with actionable recommendations."
    ),
    tools=[
        FunctionTool(deep_research_tool),
        FunctionTool(quick_search_tool),
    ],
    sub_agents=[action_planner],
)


# ── Run ───────────────────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="research_app", user_id="user_01"
    )
    runner = Runner(
        agent=coordinator,
        app_name="research_app",
        session_service=session_service,
    )

    request = (
        "I want to build a production-grade multi-agent system using Google ADK. "
        "Research the best practices and create an action plan for implementation."
    )

    print(f"User: {request}\n")

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=request)]
        ),
    ):
        if event.is_final_response():
            print("=== Coordinator Response ===")
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
