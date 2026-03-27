"""
Blog 04 — Building Agents with the ADK and the New Interactions API (Dec 2025)
Example 4: Using the Built-in Deep Research Agent

Source: https://developers.googleblog.com/building-agents-with-the-adk-and-the-new-interactions-api/

The Interactions API provides a unified interface to both standard Gemini models
AND built-in managed agents like Deep Research. The same API call works for both —
you just change the `agent` parameter.

Deep Research is Gemini's fully managed research agent that autonomously
searches the web, synthesises information, and generates structured reports.
"""

import os
import asyncio
from interactions_api_transport import InteractionsApiTransport
from a2a.client import ClientFactory, ClientConfig
import google.generativeai as genai


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


# ── Option A: Direct Interactions API call with Deep Research ─────────────────
async def deep_research_direct(research_question: str) -> str:
    """
    Calls the Deep Research agent directly via the Interactions API.
    Returns a comprehensive research report.
    """
    client = genai.GenerativeModel("gemini-2.5-pro")

    print(f"Sending to Deep Research: {research_question}")
    print("This may take several minutes...\n")

    # Use background=True since Deep Research can take minutes
    response = await client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": research_question}]}],
        config={
            "agent": "deep-research-pro-preview-12-2025",  # specify Deep Research agent
            "background": True,
        },
    )
    return response.interaction_id


# ── Option B: Deep Research via A2A protocol (ADK integration) ───────────────
async def deep_research_via_a2a(research_question: str):
    """
    Connects to Deep Research using the A2A protocol via Interactions API transport.
    This approach integrates seamlessly with ADK's multi-agent framework.
    """
    # 1. Configure the A2A client factory to support Interactions API
    client_config = ClientConfig()
    client_factory = ClientFactory(client_config)
    InteractionsApiTransport.setup(client_factory)

    # 2. Create an AgentCard pointing to the Deep Research agent
    deep_research_card = InteractionsApiTransport.make_card(
        url="https://generativelanguage.googleapis.com",
        agent="deep-research-pro-preview-12-2025",
    )

    # 3. Create a client for the Deep Research agent
    dr_client = await client_factory.get_client(deep_research_card)

    print(f"Connected to Deep Research agent: {deep_research_card.name}")

    # 4. Send the research request
    task = await dr_client.send_task(
        message=research_question,
        session_id="research_session_01",
    )
    print(f"Research task ID: {task.id}")
    print("Polling for completion...")

    # 5. Wait for the research to complete
    while True:
        task = await dr_client.get_task(task.id)
        print(f"  Status: {task.status.state}")

        if task.status.state == "completed":
            break
        elif task.status.state == "failed":
            raise RuntimeError("Deep Research task failed")
        await asyncio.sleep(5)

    # 6. Extract the report
    report = task.result.parts[0].text
    return report


# ── Option C: Compare model vs Deep Research on the same question ─────────────
async def compare_model_vs_agent(question: str):
    """
    Sends the same research question to both a standard Gemini model
    and the Deep Research agent, then compares the responses.
    Demonstrates the unified Interactions API interface.
    """
    genai_client = genai.GenerativeModel("gemini-2.5-flash")

    print(f"Question: {question}\n")

    # Standard model response
    print("1. Standard Gemini 2.5 Flash response:")
    model_response = await genai_client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": question}]}],
    )
    model_text = model_response.candidates[0].content.parts[0].text
    print(f"   {model_text[:400]}...\n" if len(model_text) > 400 else f"   {model_text}\n")

    # Deep Research response (background mode)
    print("2. Deep Research Agent response (background mode):")
    dr_response = await genai_client.interactions.create_async(
        contents=[{"role": "user", "parts": [{"text": question}]}],
        config={
            "agent": "deep-research-pro-preview-12-2025",
            "background": True,
        },
    )
    print(f"   Research task submitted. ID: {dr_response.interaction_id}")
    print("   (Poll with: client.interactions.get_async(interaction_id))")


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    print("=== Deep Research Agent via Interactions API ===\n")

    question = (
        "What are the practical production deployment patterns for Google ADK agents "
        "in 2025, including performance benchmarks and cost comparisons?"
    )

    await compare_model_vs_agent(question)


if __name__ == "__main__":
    asyncio.run(main())
