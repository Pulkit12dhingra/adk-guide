"""
Blog 06 — ADK Python 2.0 Alpha: Graph-Based Workflows (March 2026)
Example 2: Conditional Routing Agent

Source: https://google.github.io/adk-docs/

ADK 2.0 supports dynamic branching: a router agent classifies the request
and transfers control to the most appropriate specialist agent.
The routing decision is made at runtime based on content.

Use case: Customer support triage — route to billing, technical, or general support.
"""

import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Specialist Agents ─────────────────────────────────────────────────────────
billing_agent = LlmAgent(
    name="billing_support",
    model="gemini-2.5-flash",
    instruction=(
        "You are a billing specialist. Help customers with payment issues, "
        "invoices, subscription changes, refunds, and account charges. "
        "Be empathetic and solution-focused."
    ),
    description="Handles billing, payment, and subscription issues.",
)

technical_agent = LlmAgent(
    name="technical_support",
    model="gemini-2.5-flash",
    instruction=(
        "You are a technical support engineer. Help customers troubleshoot "
        "errors, API issues, integration problems, and bugs. "
        "Ask clarifying questions and provide step-by-step solutions."
    ),
    description="Handles technical issues, bugs, and API problems.",
)

general_agent = LlmAgent(
    name="general_support",
    model="gemini-2.5-flash",
    instruction=(
        "You are a general customer support agent. Help with account questions, "
        "general inquiries, product information, and anything not covered by "
        "billing or technical support."
    ),
    description="Handles general inquiries and account questions.",
)

escalation_agent = LlmAgent(
    name="escalation_specialist",
    model="gemini-2.5-flash",
    instruction=(
        "You are a senior support specialist handling escalated cases. "
        "The customer is frustrated or has a complex unresolved issue. "
        "Acknowledge their frustration, apologise sincerely, and provide "
        "a concrete resolution path with specific timelines."
    ),
    description="Handles escalated or urgent cases requiring senior attention.",
)


# ── Triage Router Agent ────────────────────────────────────────────────────────
# In ADK 2.0, the router uses transfer_to_agent() to hand off control.
# The sub_agents list defines which agents the router can transfer to.
triage_router = LlmAgent(
    name="triage_router",
    model="gemini-2.5-flash",
    instruction=(
        "You are a customer support triage agent. Analyse the customer's message "
        "and route to the most appropriate specialist:\n\n"
        "- billing_support: for payment, invoice, subscription, refund questions\n"
        "- technical_support: for errors, bugs, API issues, integration problems\n"
        "- general_support: for account questions, general inquiries, product info\n"
        "- escalation_specialist: if the customer mentions urgency, is clearly "
        "  frustrated, or says they want to cancel\n\n"
        "IMPORTANT: Do NOT answer yourself — always transfer to a specialist."
    ),
    description="Triages customer requests and routes to appropriate specialists.",
    sub_agents=[billing_agent, technical_agent, general_agent, escalation_agent],
)


# ── Run triage system ──────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="support_app", user_id="user_01"
    )
    runner = Runner(
        agent=triage_router,
        app_name="support_app",
        session_service=session_service,
    )

    test_cases = [
        "I was charged twice for my subscription this month. I need a refund.",
        "I'm getting a 401 Unauthorized error when calling the API with my key.",
        "How do I update my email address on my account?",
        "This is absolutely unacceptable! My service has been down for 3 days and nobody has helped me. I want to cancel everything!",
    ]

    print("=== Customer Support Triage System ===\n")

    for case in test_cases:
        print(f"Customer: {case}")
        async for event in runner.run_async(
            user_id="user_01",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=case)]
            ),
        ):
            if event.is_final_response():
                text = event.content.parts[0].text
                print(f"Support: {text[:300]}..." if len(text) > 300 else f"Support: {text}")
        print("─" * 60)


if __name__ == "__main__":
    asyncio.run(main())
