"""
Blog 02 — ADK Python v1.0 & Java ADK (Google I/O, May 2025)
Example 1: Sequential Agent Pipeline

Source: https://developers.googleblog.com/agents-adk-agent-engine-a2a-enhancements-google-io/

A SequentialAgent runs its sub-agents one after another in order.
Each agent's output is passed into the session state so the next agent
can build upon it. Perfect for multi-step pipelines.

Pipeline: Researcher → Summariser → Report Writer
"""

import asyncio
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Step 1: Research Agent ────────────────────────────────────────────────────
researcher = LlmAgent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction=(
        "You are a web researcher. Search the web for information on the topic "
        "provided by the user. Collect key facts, data, and quotes. "
        "Save your raw research notes to the session state key 'research_notes'."
    ),
    description="Searches the web and collects raw research notes.",
    tools=[google_search],
    output_key="research_notes",   # saves output to session state
)


# ── Step 2: Summariser Agent ──────────────────────────────────────────────────
summariser = LlmAgent(
    name="summariser",
    model="gemini-2.5-flash",
    instruction=(
        "You are an expert editor. Read the research notes from session state "
        "(key: 'research_notes') and distil them into 5 clear bullet points. "
        "Save your summary to session state key 'summary'."
    ),
    description="Distils raw research into 5 bullet-point summary.",
    output_key="summary",
)


# ── Step 3: Report Writer Agent ───────────────────────────────────────────────
report_writer = LlmAgent(
    name="report_writer",
    model="gemini-2.5-flash",
    instruction=(
        "You are a professional report writer. Read the summary from session "
        "state (key: 'summary') and expand it into a polished 3-paragraph report "
        "with an introduction, main findings, and conclusion. "
        "Save the final report to session state key 'final_report'."
    ),
    description="Expands the summary into a polished written report.",
    output_key="final_report",
)


# ── Sequential Pipeline ───────────────────────────────────────────────────────
research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="End-to-end pipeline: research → summarise → write report.",
    sub_agents=[researcher, summariser, report_writer],
)


# ── Run the pipeline ──────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="pipeline_app", user_id="user_01"
    )
    runner = Runner(
        agent=research_pipeline,
        app_name="pipeline_app",
        session_service=session_service,
    )

    topic = "Google Agent Development Kit (ADK) features and capabilities in 2025"
    print(f"Pipeline topic: {topic}\n")
    print("Running: Researcher → Summariser → Report Writer\n")

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=topic)]
        ),
    ):
        if event.is_final_response():
            print("=== Final Report ===")
            print(event.content.parts[0].text)

    # Inspect session state after pipeline completes
    session_data = await session_service.get_session(
        app_name="pipeline_app", user_id="user_01", session_id=session.id
    )
    print("\n=== Session State Keys ===")
    for key in ["research_notes", "summary", "final_report"]:
        if key in session_data.state:
            print(f"✓ {key}: {len(session_data.state[key])} characters")


if __name__ == "__main__":
    asyncio.run(main())
