"""
Blog 02 — ADK Python v1.0 & Java ADK (Google I/O, May 2025)
Example 4: Using Session State for Inter-Agent Communication

Source: https://developers.googleblog.com/agents-adk-agent-engine-a2a-enhancements-google-io/

Session state is a shared key-value store used by agents in a pipeline to
pass data between steps. This example shows how to read and write state,
and how to initialise state before a pipeline runs.
"""

import asyncio
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Agent 1: Profile Builder — writes initial user profile to state ──────────
profile_builder = LlmAgent(
    name="profile_builder",
    model="gemini-2.5-flash",
    instruction=(
        "Extract the user's name, goals, and skill level from their message. "
        "Save a structured profile to session state key 'user_profile' in this format:\n"
        "Name: <name>\nGoals: <goals>\nSkill Level: <beginner/intermediate/advanced>"
    ),
    description="Extracts user profile information.",
    output_key="user_profile",
)


# ── Agent 2: Plan Creator — reads profile, writes learning plan ───────────────
plan_creator = LlmAgent(
    name="plan_creator",
    model="gemini-2.5-flash",
    instruction=(
        "Read the user profile from session state key 'user_profile'. "
        "Create a 7-day personalised learning plan tailored to their goals and skill level. "
        "Format as a numbered day-by-day plan. "
        "Save the plan to session state key 'learning_plan'."
    ),
    description="Creates a personalised learning plan based on the user profile.",
    output_key="learning_plan",
)


# ── Agent 3: Resource Curator — reads plan, writes recommended resources ──────
resource_curator = LlmAgent(
    name="resource_curator",
    model="gemini-2.5-flash",
    instruction=(
        "Read the learning plan from session state key 'learning_plan'. "
        "For each day in the plan, suggest 2 specific resources (docs, videos, or tutorials). "
        "Prioritise official Google ADK documentation and GitHub samples. "
        "Save curated resources to session state key 'resources'."
    ),
    description="Curates learning resources for each step of the plan.",
    output_key="resources",
)


# ── Agent 4: Summary Agent — reads all state, produces final output ───────────
final_summary = LlmAgent(
    name="final_summary",
    model="gemini-2.5-flash",
    instruction=(
        "Read these session state keys: 'user_profile', 'learning_plan', 'resources'. "
        "Combine them into a beautifully formatted personalised learning guide. "
        "Structure it with: Welcome message, User Profile, 7-Day Plan with Resources, "
        "and a motivational closing."
    ),
    description="Combines all session state into a final personalised guide.",
)


# ── Pipeline ──────────────────────────────────────────────────────────────────
onboarding_pipeline = SequentialAgent(
    name="onboarding_pipeline",
    description="Personalised user onboarding: profile → plan → resources → guide.",
    sub_agents=[profile_builder, plan_creator, resource_curator, final_summary],
)


# ── Run with pre-populated session state ─────────────────────────────────────
async def main():
    session_service = InMemorySessionService()

    # Pre-populate session state with any global context
    initial_state = {
        "app_version": "1.0",
        "supported_languages": ["Python", "TypeScript", "Go", "Java"],
    }

    session = await session_service.create_session(
        app_name="onboarding_app",
        user_id="user_01",
        state=initial_state,
    )

    runner = Runner(
        agent=onboarding_pipeline,
        app_name="onboarding_app",
        session_service=session_service,
    )

    user_intro = (
        "Hi! I'm Alex. I want to learn Google ADK to build multi-agent AI systems. "
        "I have intermediate Python experience but I'm new to LLM frameworks."
    )

    print(f"User: {user_intro}\n")
    print("Pipeline running: Profile Builder → Plan Creator → Resource Curator → Summary\n")

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=user_intro)]
        ),
    ):
        if event.is_final_response():
            print("=== Personalised Learning Guide ===")
            print(event.content.parts[0].text)

    # Show final session state
    final_session = await session_service.get_session(
        app_name="onboarding_app", user_id="user_01", session_id=session.id
    )
    print("\n=== Session State After Pipeline ===")
    for key, value in final_session.state.items():
        preview = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
        print(f"  {key}: {preview}")


if __name__ == "__main__":
    asyncio.run(main())
