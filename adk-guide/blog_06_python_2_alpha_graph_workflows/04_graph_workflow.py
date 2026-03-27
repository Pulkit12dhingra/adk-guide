"""
Blog 06 — ADK Python 2.0 Alpha: Graph-Based Workflows (March 2026)
Example 4: Graph-Based Multi-Agent DAG Orchestration

Source: https://google.github.io/adk-docs/

ADK Python 2.0 Alpha introduces graph-based workflows where agents form
a Directed Acyclic Graph (DAG). Unlike linear sequential pipelines,
graph workflows allow:
  - Multiple agents running in parallel branches
  - Conditional merging of parallel results
  - Non-linear execution paths
  - Diamond-shaped dependency patterns

Use case: Content pipeline with parallel processing and conditional merge.
"""

import asyncio
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types


# ── STAGE 1: Input Analysis (single entry point) ──────────────────────────────
input_analyser = LlmAgent(
    name="input_analyser",
    model="gemini-2.5-flash",
    instruction=(
        "Analyse the user's content request. Extract: "
        "1. Topic\n2. Target audience\n3. Desired tone\n4. Required length\n"
        "Save as structured JSON to session state key 'content_spec'."
    ),
    description="Analyses and structures the content request.",
    output_key="content_spec",
)


# ── STAGE 2a: Research Branch (parallel) ─────────────────────────────────────
fact_researcher = LlmAgent(
    name="fact_researcher",
    model="gemini-2.5-flash",
    instruction=(
        "Using the content_spec from session state, research factual information "
        "and recent data for the topic. Save findings to 'factual_research'."
    ),
    description="Researches facts and data.",
    tools=[google_search],
    output_key="factual_research",
)


# ── STAGE 2b: SEO Branch (parallel) ──────────────────────────────────────────
seo_analyser = LlmAgent(
    name="seo_analyser",
    model="gemini-2.5-flash",
    instruction=(
        "Using the content_spec from session state, identify: "
        "primary keywords, LSI keywords, and semantic topics. "
        "Save to session state key 'seo_analysis'."
    ),
    description="Analyses SEO opportunities.",
    output_key="seo_analysis",
)


# ── STAGE 2c: Competitor Branch (parallel) ────────────────────────────────────
competitor_analyst = LlmAgent(
    name="competitor_analyst",
    model="gemini-2.5-flash",
    instruction=(
        "Using the content_spec from session state, research how competitors "
        "cover this topic. Identify content gaps and angles. "
        "Save to session state key 'competitor_insights'."
    ),
    description="Analyses competitor content.",
    tools=[google_search],
    output_key="competitor_insights",
)


# ── STAGE 2: Parallel block ───────────────────────────────────────────────────
parallel_stage = ParallelAgent(
    name="parallel_research_seo",
    description="Runs fact research, SEO analysis, and competitor research in parallel.",
    sub_agents=[fact_researcher, seo_analyser, competitor_analyst],
)


# ── STAGE 3: Synthesis (merge point after parallel stage) ────────────────────
content_synthesiser = LlmAgent(
    name="content_synthesiser",
    model="gemini-2.5-flash",
    instruction=(
        "You have three research inputs in session state:\n"
        "- 'factual_research': facts and data\n"
        "- 'seo_analysis': keywords and semantic topics\n"
        "- 'competitor_insights': content gaps to fill\n"
        "- 'content_spec': the original content specification\n\n"
        "Create a comprehensive content outline that:\n"
        "1. Incorporates key facts\n"
        "2. Naturally integrates SEO keywords\n"
        "3. Addresses competitor content gaps\n"
        "4. Matches the specified audience and tone\n\n"
        "Save the outline to session state key 'content_outline'."
    ),
    description="Synthesises parallel research into a unified outline.",
    output_key="content_outline",
)


# ── STAGE 4a: Draft Writer ────────────────────────────────────────────────────
draft_writer = LlmAgent(
    name="draft_writer",
    model="gemini-2.5-flash",
    instruction=(
        "Using 'content_outline' and 'content_spec' from session state, "
        "write the full draft content. Match the specified tone, audience, "
        "and length. Save to 'draft_content'."
    ),
    description="Writes the full content draft.",
    output_key="draft_content",
)


# ── STAGE 4b: Meta Writer (parallel with draft) ───────────────────────────────
meta_writer = LlmAgent(
    name="meta_writer",
    model="gemini-2.5-flash",
    instruction=(
        "Using 'seo_analysis' and 'content_spec' from session state, "
        "write: SEO title, meta description (155 chars), and 5 social media posts. "
        "Save to 'meta_content'."
    ),
    description="Writes meta content and social posts.",
    output_key="meta_content",
)


# ── STAGE 4: Parallel content creation ───────────────────────────────────────
parallel_creation = ParallelAgent(
    name="parallel_content_creation",
    description="Creates main draft and meta content in parallel.",
    sub_agents=[draft_writer, meta_writer],
)


# ── STAGE 5: Final Assembly ───────────────────────────────────────────────────
final_assembler = LlmAgent(
    name="final_assembler",
    model="gemini-2.5-flash",
    instruction=(
        "Assemble the final content package from session state:\n"
        "- 'draft_content': the main article\n"
        "- 'meta_content': SEO metadata and social posts\n\n"
        "Create a complete, publication-ready package with:\n"
        "1. SEO Title\n2. Meta Description\n3. Full Article\n4. Social Media Posts"
    ),
    description="Assembles all content into final publication package.",
)


# ── Full DAG Pipeline: Stage 1 → [2a||2b||2c] → 3 → [4a||4b] → 5 ───────────
#
#   input_analyser
#         ↓
#   [fact || seo || competitor]  ← ParallelAgent (Stage 2)
#         ↓
#   content_synthesiser           ← merge point (Stage 3)
#         ↓
#   [draft || meta]              ← ParallelAgent (Stage 4)
#         ↓
#   final_assembler               ← final assembly (Stage 5)

content_dag = SequentialAgent(
    name="content_production_dag",
    description="Full content production DAG: analyse → [research||SEO||competitor] → synthesise → [draft||meta] → assemble",
    sub_agents=[
        input_analyser,        # Stage 1
        parallel_stage,        # Stage 2: parallel branches
        content_synthesiser,   # Stage 3: merge
        parallel_creation,     # Stage 4: parallel creation
        final_assembler,       # Stage 5: final assembly
    ],
)


# ── Run the DAG ───────────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="content_dag_app", user_id="user_01"
    )
    runner = Runner(
        agent=content_dag,
        app_name="content_dag_app",
        session_service=session_service,
    )

    request = (
        "Write a 1200-word blog post about Google ADK 2.0's graph-based workflows "
        "for an audience of senior software engineers. Professional but engaging tone."
    )

    print(f"Content request: {request}\n")
    print("Running DAG: analyse → [research||SEO||competitor] → synthesise → [draft||meta] → assemble\n")

    async for event in runner.run_async(
        user_id="user_01",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=request)]
        ),
    ):
        if event.is_final_response():
            print("=== Final Content Package ===")
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
