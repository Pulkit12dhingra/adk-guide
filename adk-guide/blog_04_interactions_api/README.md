# Blog 04 — Building Agents with the ADK and the New Interactions API
**Published:** December 11, 2025
**Source:** https://developers.googleblog.com/building-agents-with-the-adk-and-the-new-interactions-api/

## What This Blog Covers
The Interactions API (beta) provides a unified gateway to both raw Gemini models
and the fully managed Gemini Deep Research Agent. Key features:
- **Unified endpoint** — same API for raw models and built-in Gemini agents
- **Server-side state management** — offload conversation history using `previous_interaction_id`
- **Background execution** — long-running tasks with `background=True`
- **Deep Research Agent** — built-in access to Gemini's research capabilities

## Files in This Folder
- `01_basic_interactions_api.py` — Basic Interactions API call with Gemini
- `02_stateful_conversation.py` — Multi-turn conversation using `previous_interaction_id`
- `03_background_execution.py` — Long-running tasks with background mode
- `04_deep_research_agent.py` — Using the built-in Deep Research Agent
- `05_adk_with_interactions_transport.py` — Connecting ADK agents via Interactions API transport

## Setup
```bash
pip install google-adk google-generativeai interactions-api-transport
export GOOGLE_API_KEY="your-gemini-api-key"
```
