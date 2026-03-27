"""
Blog 01 — Google ADK Initial Launch (April 2025)
Example 4: Bidirectional Streaming Agent

Source: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/

ADK's built-in streaming enables real-time, human-like conversation with
agents. This example demonstrates token-by-token streaming output, which
reduces perceived latency for the user.
"""

import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Define a streaming-ready agent ───────────────────────────────────────────
streaming_agent = Agent(
    name="streaming_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful assistant. Provide detailed, thoughtful answers. "
        "Write responses in a natural, conversational style."
    ),
    description="An assistant with real-time streaming responses.",
)


# ── Stream tokens as they arrive ─────────────────────────────────────────────
async def stream_response(runner: Runner, session_id: str, message: str):
    """Prints each token as it streams from the model."""
    print(f"User: {message}")
    print("Agent: ", end="", flush=True)

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session_id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=message)]
        ),
    ):
        # Partial text events arrive before is_final_response()
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)

        # Final event signals the end of the stream
        if event.is_final_response():
            print("\n")  # newline after full response


# ── Run with streaming ────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="streaming_app", user_id="user_01"
    )
    runner = Runner(
        agent=streaming_agent,
        app_name="streaming_app",
        session_service=session_service,
    )

    prompts = [
        "Explain the benefits of multi-agent AI systems in three paragraphs.",
        "What makes Google ADK different from LangChain or CrewAI?",
    ]

    for prompt in prompts:
        await stream_response(runner, session.id, prompt)


if __name__ == "__main__":
    asyncio.run(main())
