"""
Blog 04 — Building Agents with the ADK and the New Interactions API (Dec 2025)
Example 2: Stateful Multi-Turn Conversation

Source: https://developers.googleblog.com/building-agents-with-the-adk-and-the-new-interactions-api/

The Interactions API supports server-side state management. Instead of
sending the full conversation history with every request, you pass
`previous_interaction_id` and the server maintains the context.

This dramatically simplifies stateful agentic loops.
"""

import os
import asyncio
import google.generativeai as genai
from google.generativeai.types import InteractionsApiConfig


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
client = genai.GenerativeModel("gemini-2.5-flash")


# ── Turn 1: Start a new conversation ─────────────────────────────────────────
async def start_conversation(user_message: str) -> tuple[str, str]:
    """
    Starts a new conversation. Returns (response_text, interaction_id).
    The interaction_id is used to continue this conversation.
    """
    response = await client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": user_message}]}],
    )
    text = response.candidates[0].content.parts[0].text
    return text, response.interaction_id


# ── Turn 2+: Continue an existing conversation ────────────────────────────────
async def continue_conversation(
    user_message: str,
    previous_interaction_id: str,
) -> tuple[str, str]:
    """
    Continues an existing conversation using the previous interaction ID.
    The server maintains the full history — no need to resend it.
    """
    response = await client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": user_message}]}],
        config=InteractionsApiConfig(
            # Server-side history management — key feature of Interactions API
            previous_interaction_id=previous_interaction_id,
        ),
    )
    text = response.candidates[0].content.parts[0].text
    return text, response.interaction_id


# ── Full multi-turn conversation demo ────────────────────────────────────────
async def run_conversation():
    """
    Demonstrates a multi-turn conversation where the server maintains state.
    The client only sends each new message, not the full history.
    """
    conversation_turns = [
        "I'm learning Google ADK. What's the most important concept to understand first?",
        "Can you give me a simple code example of that?",
        "How does this compare to LangChain's approach?",
        "What's the best way to deploy an ADK agent to production?",
    ]

    print("=== Stateful Multi-Turn Conversation ===")
    print("(Server manages history via previous_interaction_id)\n")

    interaction_id = None

    for turn_num, user_message in enumerate(conversation_turns, 1):
        print(f"Turn {turn_num} — User: {user_message}")

        if interaction_id is None:
            # First turn: start a fresh conversation
            response_text, interaction_id = await start_conversation(user_message)
        else:
            # Subsequent turns: continue with server-side history
            response_text, interaction_id = await continue_conversation(
                user_message, interaction_id
            )

        print(f"Agent: {response_text[:300]}..." if len(response_text) > 300 else f"Agent: {response_text}")
        print(f"[Interaction ID: {interaction_id[:20]}...]\n")

    print(f"✓ Full conversation completed across {len(conversation_turns)} turns")
    print("  All history managed server-side — no local storage needed")


if __name__ == "__main__":
    asyncio.run(run_conversation())
