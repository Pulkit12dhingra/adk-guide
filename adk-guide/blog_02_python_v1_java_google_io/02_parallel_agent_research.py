"""
Blog 02 — ADK Python v1.0 & Java ADK (Google I/O, May 2025)
Example 2: Parallel Agent Research

Source: https://developers.googleblog.com/agents-adk-agent-engine-a2a-enhancements-google-io/

A ParallelAgent runs all its sub-agents simultaneously, which is ideal
for tasks that don't depend on each other. A SequentialAgent then
combines the results with a synthesis agent.

Pattern: [Researcher A || Researcher B || Researcher C] → Synthesiser
"""

import asyncio
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Concurrent Researchers (run in parallel) ──────────────────────────────────
tech_researcher = LlmAgent(
    name="tech_researcher",
    model="gemini-2.5-flash",
    instruction=(
        "Research the TECHNICAL aspects of the topic given by the user: "
        "architecture, implementation, APIs, and developer experience. "
        "Store your findings in session state key 'tech_findings'."
    ),
    description="Researches technical implementation details.",
    tools=[google_search],
    output_key="tech_findings",
)

business_researcher = LlmAgent(
    name="business_researcher",
    model="gemini-2.5-flash",
    instruction=(
        "Research the BUSINESS and adoption aspects of the topic: "
        "use cases, market adoption, enterprise use, and ROI. "
        "Store your findings in session state key 'business_findings'."
    ),
    description="Researches business use cases and market adoption.",
    tools=[google_search],
    output_key="business_findings",
)

comparison_researcher = LlmAgent(
    name="comparison_researcher",
    model="gemini-2.5-flash",
    instruction=(
        "Research how the topic COMPARES to alternatives and competitors: "
        "strengths, weaknesses, and differentiators. "
        "Store your findings in session state key 'comparison_findings'."
    ),
    description="Researches competitive landscape and comparisons.",
    tools=[google_search],
    output_key="comparison_findings",
)


# ── Parallel research block ───────────────────────────────────────────────────
parallel_research = ParallelAgent(
    name="parallel_research",
    description="Runs three topic researchers concurrently.",
    sub_agents=[tech_researcher, business_researcher, comparison_researcher],
)


# ── Synthesis Agent (runs after parallel block) ───────────────────────────────
synthesis_agent = LlmAgent(
    name="synthesis_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a senior analyst. Read the three research findings from session state:\n"
        "- 'tech_findings'       (technical details)\n"
        "- 'business_findings'   (business & adoption)\n"
        "- 'comparison_findings' (competitive landscape)\n\n"
        "Synthesise all three into one comprehensive, well-structured analysis report "
        "with clear sections: Overview, Technical Analysis, Business Impact, and "
        "Competitive Positioning."
    ),
    description="Synthesises parallel research into a unified report.",
)


# ── Full pipeline: parallel research → synthesis ─────────────────────────────
full_pipeline = SequentialAgent(
    name="full_research_pipeline",
    description="Parallel research followed by synthesis.",
    sub_agents=[parallel_research, synthesis_agent],
)


# ── Run ───────────────────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="parallel_app", user_id="user_01"
    )
    runner = Runner(
        agent=full_pipeline,
        app_name="parallel_app",
        session_service=session_service,
    )

    topic = "Google Agent Development Kit (ADK)"
    print(f"Researching: {topic}")
    print("Running 3 researchers in parallel, then synthesising...\n")

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=topic)]
        ),
    ):
        if event.is_final_response():
            print("=== Synthesised Analysis ===")
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
