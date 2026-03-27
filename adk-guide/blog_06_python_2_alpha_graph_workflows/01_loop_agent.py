"""
Blog 06 — ADK Python 2.0 Alpha: Graph-Based Workflows (March 2026)
Example 1: Loop Agent — Iterative Refinement

Source: https://google.github.io/adk-docs/

A LoopAgent runs its sub-agents repeatedly in a sequential loop until
an exit condition is met (e.g., quality threshold reached, max iterations,
or an agent sets a specific state flag).

Use case: Iterative code improvement — loop until tests pass or quality threshold met.
"""

import asyncio
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Draft Writer Agent ────────────────────────────────────────────────────────
draft_writer = LlmAgent(
    name="draft_writer",
    model="gemini-2.5-flash",
    instruction=(
        "You are a content writer. Read the current draft from session state "
        "key 'current_draft' (or write the first draft if it's empty). "
        "Write or improve the content based on the topic in 'writing_topic'. "
        "Save the new draft to session state key 'current_draft'."
    ),
    description="Writes or improves the current draft.",
    output_key="current_draft",
)


# ── Quality Evaluator Agent ───────────────────────────────────────────────────
quality_evaluator = LlmAgent(
    name="quality_evaluator",
    model="gemini-2.5-flash",
    instruction=(
        "You are a quality evaluator. Read the draft from session state key 'current_draft'. "
        "Score it from 1-10 on: clarity, completeness, and engagement. "
        "If the average score >= 8, set session state key 'quality_approved' to 'true'. "
        "Otherwise set it to 'false'. "
        "Also save a brief critique to session state key 'critique' to guide the next draft."
    ),
    description="Evaluates draft quality and sets approval flag.",
    output_key="quality_approved",
)


# ── Loop Agent: writer + evaluator loop ──────────────────────────────────────
refinement_loop = LoopAgent(
    name="refinement_loop",
    description="Iteratively refines the draft until quality is approved.",
    sub_agents=[draft_writer, quality_evaluator],
    # Loop exits when quality_approved == "true" OR after max_iterations
    exit_condition="quality_approved == 'true'",
    max_iterations=5,
)


# ── Final Polish Agent (runs after loop exits) ────────────────────────────────
final_polisher = LlmAgent(
    name="final_polisher",
    model="gemini-2.5-flash",
    instruction=(
        "You are a professional editor. Read the approved draft from session state "
        "key 'current_draft'. Give it a final polish: fix any grammar, improve flow, "
        "and ensure it's ready for publication. Output the final polished version."
    ),
    description="Final polish pass on the approved draft.",
)


# ── Full pipeline: loop until good enough, then polish ───────────────────────
writing_pipeline = SequentialAgent(
    name="writing_pipeline",
    description="Iterative writing with quality gate, then final polish.",
    sub_agents=[refinement_loop, final_polisher],
)


# ── Run ───────────────────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()

    # Pre-populate the writing topic in session state
    session = await session_service.create_session(
        app_name="writing_app",
        user_id="user_01",
        state={"writing_topic": "Why Google ADK 2.0's graph-based workflows change everything"},
    )

    runner = Runner(
        agent=writing_pipeline,
        app_name="writing_app",
        session_service=session_service,
    )

    print("Starting iterative writing pipeline...")
    print("Loop will exit when quality score >= 8/10 (max 5 iterations)\n")

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Please write a blog post on the configured topic.")],
        ),
    ):
        if event.is_final_response():
            print("=== Final Polished Content ===")
            print(event.content.parts[0].text)

    # Show iteration stats
    final_session = await session_service.get_session(
        app_name="writing_app", user_id="user_01", session_id=session.id
    )
    print(f"\n✓ Quality approved: {final_session.state.get('quality_approved')}")


if __name__ == "__main__":
    asyncio.run(main())
