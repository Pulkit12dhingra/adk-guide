"""
Blog 01 — Google ADK Initial Launch (April 2025)
Example 1: Single Agent with Google Search Tool

Source: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/

A minimal ADK agent that uses the built-in Google Search tool to answer questions.
"""

import asyncio
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Define the agent ──────────────────────────────────────────────────────────
root_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful assistant. Answer user questions using "
        "Google Search when needed. Be concise and accurate."
    ),
    description="An assistant that can search the web.",
    tools=[google_search],
)


# ── Run the agent ─────────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name="search_app",
        user_id="user_01",
    )

    runner = Runner(
        agent=root_agent,
        app_name="search_app",
        session_service=session_service,
    )

    user_message = "What are the latest updates to Google ADK in 2025?"
    print(f"User: {user_message}\n")

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=user_message)],
        ),
    ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
