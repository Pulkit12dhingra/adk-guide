"""
Blog 04 — Building Agents with the ADK and the New Interactions API (Dec 2025)
Example 3: Background Execution for Long-Running Tasks

Source: https://developers.googleblog.com/building-agents-with-the-adk-and-the-new-interactions-api/

The Interactions API supports background mode: set `background=True` and the
API immediately returns an interaction_id. The model then runs asynchronously
on the server. You poll for completion using the interaction_id.

This is perfect for tasks that could take minutes (deep research, complex analysis).
"""

import os
import asyncio
import time
import google.generativeai as genai
from google.generativeai.types import InteractionsApiConfig


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
client = genai.GenerativeModel("gemini-2.5-pro")


# ── Submit a long-running task in the background ──────────────────────────────
async def submit_background_task(prompt: str) -> str:
    """
    Submits a task for background execution.
    Returns the interaction_id immediately — the model is still running.
    """
    print(f"Submitting background task: {prompt[:80]}...")

    response = await client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=InteractionsApiConfig(
            background=True,   # ← key flag: run asynchronously
            generation_config={"thinking_summaries": "auto"},
        ),
    )

    interaction_id = response.interaction_id
    print(f"✓ Task submitted. Interaction ID: {interaction_id}")
    print("  Model is running in the background...\n")
    return interaction_id


# ── Poll until the background task completes ──────────────────────────────────
async def poll_for_completion(interaction_id: str, poll_interval: float = 3.0) -> str:
    """
    Polls the Interactions API until the background task finishes.
    Returns the final response text.
    """
    print(f"Polling for completion (every {poll_interval}s)...")
    start_time = time.time()
    attempts = 0

    while True:
        attempts += 1
        elapsed = time.time() - start_time

        # Fetch current status
        status = await client.interactions.get_async(interaction_id)

        print(f"  [{elapsed:.1f}s] Status: {status.state}")

        if status.state == "COMPLETED":
            print(f"✓ Completed after {elapsed:.1f}s ({attempts} polls)\n")
            return status.candidates[0].content.parts[0].text

        elif status.state == "FAILED":
            raise RuntimeError(f"Background task failed: {status.error}")

        elif status.state in ("RUNNING", "PENDING"):
            await asyncio.sleep(poll_interval)

        else:
            raise ValueError(f"Unexpected state: {status.state}")


# ── Cancel a background task ──────────────────────────────────────────────────
async def cancel_background_task(interaction_id: str):
    """Cancels a running background task."""
    await client.interactions.cancel_async(interaction_id)
    print(f"✓ Task {interaction_id[:20]}... cancelled")


# ── Full demo: submit, do other work, then collect result ─────────────────────
async def main():
    print("=== Background Execution Demo ===\n")

    # Submit a complex, long-running task
    long_task_prompt = (
        "Write a comprehensive technical comparison of Google ADK, LangChain, "
        "and CrewAI for building production multi-agent systems. Cover: "
        "architecture philosophy, tool ecosystem, state management, deployment "
        "options, performance characteristics, and ideal use cases for each. "
        "Include concrete code examples for each framework."
    )

    interaction_id = await submit_background_task(long_task_prompt)

    # While the model runs in the background, do other work
    print("While waiting, doing other work...\n")
    for i in range(3):
        await asyncio.sleep(1)
        print(f"  Other work step {i + 1} completed")

    print()

    # Now collect the result
    result = await poll_for_completion(interaction_id)

    print("=== Final Report ===")
    print(result[:1000] + "..." if len(result) > 1000 else result)


if __name__ == "__main__":
    asyncio.run(main())
