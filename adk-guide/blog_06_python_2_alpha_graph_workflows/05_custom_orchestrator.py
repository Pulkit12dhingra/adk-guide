"""
Blog 06 — ADK Python 2.0 Alpha: Graph-Based Workflows (March 2026)
Example 5: Custom BaseAgent Orchestrator

Source: https://google.github.io/adk-docs/

For maximum flexibility, ADK 2.0 lets you build custom orchestrators by
subclassing BaseAgent and overriding _run_async_impl(). This gives you
full programmatic control over agent execution flow.

Use case: Dynamic agent selection based on runtime context and cost budgets.
"""

import asyncio
from typing import AsyncGenerator, Optional
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Specialist Agents ─────────────────────────────────────────────────────────
fast_agent = LlmAgent(
    name="fast_agent",
    model="gemini-2.5-flash",         # faster, cheaper model
    instruction=(
        "You are a quick-response assistant. Provide concise, direct answers "
        "in 2-3 sentences. Prioritise speed over depth."
    ),
    description="Fast, concise responses for simple queries.",
)

deep_agent = LlmAgent(
    name="deep_agent",
    model="gemini-2.5-pro",           # slower, more powerful model
    instruction=(
        "You are a deep analysis expert. Provide thorough, comprehensive "
        "analysis with reasoning, examples, and nuanced perspectives."
    ),
    description="Deep, comprehensive analysis for complex queries.",
)

creative_agent = LlmAgent(
    name="creative_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a creative writing expert. Generate imaginative, engaging, "
        "original content with vivid language and compelling narratives."
    ),
    description="Creative writing and ideation.",
)

code_agent = LlmAgent(
    name="code_agent",
    model="gemini-2.5-pro",
    instruction=(
        "You are a senior software engineer. Write clean, well-documented, "
        "production-quality code with proper error handling and tests."
    ),
    description="Code generation and technical implementation.",
)


# ── Custom Orchestrator ───────────────────────────────────────────────────────
class SmartOrchestrator(BaseAgent):
    """
    A custom orchestrator that dynamically selects agents based on:
    - Query complexity (simple → fast, complex → deep)
    - Query type (creative, code, analytical)
    - Available token budget
    """

    def __init__(self):
        super().__init__(
            name="smart_orchestrator",
            description=(
                "Dynamically routes to the optimal agent based on query type and complexity."
            ),
            sub_agents=[fast_agent, deep_agent, creative_agent, code_agent],
        )

    def _classify_query(self, query: str) -> tuple[str, str]:
        """
        Classifies query type and complexity.
        Returns (agent_name, reasoning).
        In production, use an LLM call for classification.
        """
        query_lower = query.lower()

        # Code-related keywords
        code_keywords = ["code", "function", "class", "implement", "python", "typescript", "debug", "refactor"]
        if any(k in query_lower for k in code_keywords):
            return "code_agent", "Code/technical query detected"

        # Creative keywords
        creative_keywords = ["write", "story", "poem", "creative", "imagine", "invent", "blog post"]
        if any(k in query_lower for k in creative_keywords):
            return "creative_agent", "Creative writing query detected"

        # Complexity heuristic: question length and complexity words
        complex_keywords = ["analyse", "compare", "evaluate", "pros and cons", "comprehensive", "explain in depth", "why"]
        if len(query) > 100 or any(k in query_lower for k in complex_keywords):
            return "deep_agent", "Complex analytical query detected"

        # Default: fast response for simple queries
        return "fast_agent", "Simple query — fast response appropriate"

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Custom orchestration logic: classify then delegate to chosen agent.
        """
        # Get the user's latest message
        user_message = ""
        if ctx.user_content and ctx.user_content.parts:
            user_message = ctx.user_content.parts[0].text or ""

        # Classify the query
        chosen_agent_name, reasoning = self._classify_query(user_message)
        print(f"\n[Orchestrator] Routing to: {chosen_agent_name}")
        print(f"[Orchestrator] Reason: {reasoning}")

        # Find the chosen sub-agent
        chosen_agent = next(
            (a for a in self.sub_agents if a.name == chosen_agent_name),
            fast_agent,  # fallback
        )

        # Delegate to chosen agent and yield all its events
        async for event in ctx.invoke_agent(chosen_agent):
            yield event


# ── Run the smart orchestrator ────────────────────────────────────────────────
async def main():
    orchestrator = SmartOrchestrator()

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="smart_orchestrator_app", user_id="user_01"
    )
    runner = Runner(
        agent=orchestrator,
        app_name="smart_orchestrator_app",
        session_service=session_service,
    )

    queries = [
        "What is ADK?",   # simple → fast_agent
        "Write a Python function that implements a binary search tree with insert, delete, and search operations.",  # code → code_agent
        "Write a short creative story about an AI agent discovering it can dream.",  # creative → creative_agent
        "Comprehensively analyse the pros and cons of graph-based vs sequential agent orchestration in production AI systems.",  # complex → deep_agent
    ]

    print("=== Smart Orchestrator Demo ===\n")

    for query in queries:
        print(f"User: {query}")
        async for event in runner.run_async(
            user_id="user_01",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=query)]
            ),
        ):
            if event.is_final_response():
                text = event.content.parts[0].text
                print(f"Agent: {text[:400]}..." if len(text) > 400 else f"Agent: {text}")
        print("─" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
