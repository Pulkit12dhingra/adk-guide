"""
Blog 01 — Google ADK Initial Launch (April 2025)
Example 3: Multi-Agent System with a Coordinator

Source: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/

ADK enables hierarchical multi-agent systems where a coordinator agent
routes tasks to specialised sub-agents. Each sub-agent is an independent
LlmAgent focused on a single responsibility.
"""

import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Sub-Agent 1: Greeter ──────────────────────────────────────────────────────
greeter_agent = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction=(
        "You are a warm and friendly greeter. Welcome users enthusiastically "
        "and ask how you can help them today. Keep responses brief and cheerful."
    ),
    description=(
        "Handles all user greeting and welcome messages. "
        "Use this agent when the user says hello, hi, or introduces themselves."
    ),
)


# ── Sub-Agent 2: Research Specialist ─────────────────────────────────────────
research_agent = LlmAgent(
    name="research_specialist",
    model="gemini-2.5-flash",
    instruction=(
        "You are a research expert. Search the web thoroughly and provide "
        "well-structured, factual answers with key points highlighted. "
        "Always cite your sources."
    ),
    description=(
        "Handles research questions, fact-finding, and web searches. "
        "Use this agent when the user asks for information, facts, or research."
    ),
    tools=[google_search],
)


# ── Sub-Agent 3: Task Manager ─────────────────────────────────────────────────
task_manager_agent = LlmAgent(
    name="task_manager",
    model="gemini-2.5-flash",
    instruction=(
        "You are a productivity and task-management expert. Help users break "
        "down goals into actionable steps, prioritise tasks, and create "
        "clear action plans."
    ),
    description=(
        "Handles task planning, to-do lists, and productivity questions. "
        "Use this agent when the user wants to plan tasks or organise work."
    ),
)


# ── Coordinator Agent ─────────────────────────────────────────────────────────
coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.5-flash",
    instruction=(
        "You are the main coordinator of a multi-agent assistant system. "
        "Analyse each user request and route it to the most appropriate sub-agent:\n"
        "- Use 'greeter' for introductions and greetings.\n"
        "- Use 'research_specialist' for questions needing facts or web search.\n"
        "- Use 'task_manager' for planning, to-dos, and productivity.\n"
        "Always delegate — do not answer questions yourself."
    ),
    description="Top-level coordinator that routes requests to specialised sub-agents.",
    sub_agents=[greeter_agent, research_agent, task_manager_agent],
)


# ── Run the multi-agent system ────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="multi_agent_app", user_id="user_01"
    )
    runner = Runner(
        agent=coordinator,
        app_name="multi_agent_app",
        session_service=session_service,
    )

    queries = [
        "Hi there, I'm new here!",
        "What is Google ADK and how does it support multi-agent systems?",
        "Help me plan my week to learn ADK from scratch.",
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
