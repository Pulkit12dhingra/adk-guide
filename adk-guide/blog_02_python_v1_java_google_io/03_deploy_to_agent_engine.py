"""
Blog 02 — ADK Python v1.0 & Java ADK (Google I/O, May 2025)
Example 3: Deploy Agent to Vertex AI Agent Engine

Source: https://developers.googleblog.com/agents-adk-agent-engine-a2a-enhancements-google-io/

Vertex AI Agent Engine is Google's managed service for running ADK agents
in production. It provides persistent sessions, monitoring, and a UI dashboard
in the Google Cloud Console.

Prerequisites:
    pip install google-adk google-cloud-aiplatform
    gcloud auth application-default login
"""

import asyncio
import vertexai
from vertexai.preview import reasoning_engines
from google.adk.agents import Agent
from google.adk.tools import google_search


# ── 1. Initialise Vertex AI ───────────────────────────────────────────────────
PROJECT_ID = "your-gcp-project-id"     # replace with your project
LOCATION   = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)


# ── 2. Define the agent ───────────────────────────────────────────────────────
def create_root_agent():
    """Factory function — Agent Engine calls this to instantiate the agent."""
    return Agent(
        name="production_assistant",
        model="gemini-2.5-flash",
        instruction=(
            "You are a helpful production assistant. Answer questions accurately "
            "using Google Search when needed. Be concise and professional."
        ),
        description="Production-grade assistant deployed on Vertex AI Agent Engine.",
        tools=[google_search],
    )


# ── 3. Wrap in AdkApp for deployment ─────────────────────────────────────────
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

app = reasoning_engines.AdkApp(
    agent=create_root_agent(),
    enable_tracing=True,
)


# ── 4. Deploy to Agent Engine ─────────────────────────────────────────────────
def deploy_agent():
    """Deploy the agent to Vertex AI Agent Engine."""
    print("Deploying agent to Vertex AI Agent Engine...")

    remote_app = reasoning_engines.ReasoningEngine.create(
        app,
        requirements=[
            "google-adk>=1.0.0",
            "google-cloud-aiplatform>=1.70.0",
        ],
        display_name="Production Assistant",
        description="ADK agent deployed via Vertex AI Agent Engine",
    )

    print(f"✓ Deployed! Resource name: {remote_app.resource_name}")
    return remote_app


# ── 5. Query a deployed agent ─────────────────────────────────────────────────
def query_deployed_agent(resource_name: str, query: str):
    """Query an already-deployed Agent Engine instance."""
    remote_app = reasoning_engines.ReasoningEngine(resource_name)

    session = remote_app.create_session(user_id="user_01")
    print(f"Session created: {session['id']}")

    response = remote_app.stream_query(
        user_id="user_01",
        session_id=session["id"],
        message=query,
    )

    for chunk in response:
        if "content" in chunk and chunk["content"]:
            print(chunk["content"]["parts"][0]["text"], end="", flush=True)
    print()


# ── 6. Local test before deploying ───────────────────────────────────────────
async def test_locally():
    """Run the agent locally before deploying to Agent Engine."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    session_service = InMemorySessionService()
    agent = create_root_agent()
    session = await session_service.create_session(
        app_name="test_app", user_id="user_01"
    )
    runner = Runner(
        agent=agent, app_name="test_app", session_service=session_service
    )

    query = "What are the main features of Vertex AI Agent Engine?"
    print(f"[LOCAL TEST] User: {query}")
    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=query)]
        ),
    ):
        if event.is_final_response():
            print(f"[LOCAL TEST] Agent: {event.content.parts[0].text}")


if __name__ == "__main__":
    # Test locally first
    asyncio.run(test_locally())

    # Uncomment to deploy:
    # remote_app = deploy_agent()
    # query_deployed_agent(remote_app.resource_name, "Hello! What can you do?")
