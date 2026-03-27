"""
Blog 04 — Building Agents with the ADK and the New Interactions API (Dec 2025)
Example 1: Basic Interactions API Call with Gemini

Source: https://developers.googleblog.com/building-agents-with-the-adk-and-the-new-interactions-api/

The Interactions API is a single unified endpoint that works with both:
  - Standard Gemini models (for custom agent loops)
  - Built-in Gemini agents like Deep Research

This example shows the simplest possible usage: a single-turn request.
"""

import os
import asyncio
import google.generativeai as genai
from google.generativeai.types import InteractionsApiConfig


# ── Configure the client ──────────────────────────────────────────────────────
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


# ── Basic single-turn Interactions API request ────────────────────────────────
async def basic_interaction(prompt: str) -> str:
    """
    Sends a single message to the Gemini model via the Interactions API.
    Returns the response text and the interaction_id for follow-up turns.
    """
    client = genai.GenerativeModel("gemini-2.5-pro")

    response = await client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=InteractionsApiConfig(
            # thinking_summaries="auto" enables chain-of-thought visibility
            generation_config={"thinking_summaries": "auto"},
        ),
    )

    print(f"Interaction ID: {response.interaction_id}")
    print(f"Model: {response.model_version}")

    # Extract the response text
    text = response.candidates[0].content.parts[0].text
    return text, response.interaction_id


# ── Example: Analyse a code snippet ──────────────────────────────────────────
async def analyse_code():
    """Use the Interactions API to analyse a Python code snippet."""
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    prompt = f"Analyse this Python function for performance issues and suggest improvements:\n{code}"

    print(f"Prompt: {prompt}\n")
    response_text, interaction_id = await basic_interaction(prompt)

    print("=== Response ===")
    print(response_text)
    print(f"\n✓ Interaction ID saved: {interaction_id}")
    print("  (Use this ID in the next turn for stateful conversation)")

    return interaction_id


# ── Example: Structured output ────────────────────────────────────────────────
async def structured_request():
    """Request structured JSON output via the Interactions API."""
    import json

    prompt = (
        "List the top 5 Google ADK features as a JSON array. "
        "Each item should have 'feature' and 'description' fields."
    )

    client = genai.GenerativeModel("gemini-2.5-flash")
    response = await client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=InteractionsApiConfig(
            generation_config={
                "response_mime_type": "application/json",
            }
        ),
    )

    text = response.candidates[0].content.parts[0].text
    data = json.loads(text)

    print("\n=== Structured ADK Features ===")
    for i, item in enumerate(data, 1):
        print(f"{i}. {item['feature']}: {item['description']}")


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    print("=== Interactions API — Basic Usage ===\n")

    interaction_id = await analyse_code()
    print("\n" + "─" * 60 + "\n")
    await structured_request()


if __name__ == "__main__":
    asyncio.run(main())
