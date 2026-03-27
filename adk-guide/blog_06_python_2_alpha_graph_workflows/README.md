# Blog 06 — ADK Python 2.0 Alpha: Graph-Based Workflows & Security Advisory
**Published:** March 2026
**Source:** https://google.github.io/adk-docs/

## What This Blog Covers
ADK Python 2.0 Alpha brings major orchestration upgrades:
- **Graph-based workflows** — replace linear pipelines with flexible DAG (directed acyclic graph) orchestration
- **Enhanced conditional routing** — dynamic branching between agents based on runtime state
- **Loop agents** — agents that iterate until a condition is met
- **Human-in-the-loop** — approval workflows with tool confirmation
- ⚠️ **Security advisory** — unauthorized code in LiteLLM 1.82.7–1.82.8 (rotate credentials)

## Files in This Folder
- `01_loop_agent.py` — Agent that iterates until a goal is reached
- `02_conditional_routing.py` — Dynamic branching based on content classification
- `03_human_in_the_loop.py` — Tool confirmation and approval workflows
- `04_graph_workflow.py` — Graph-based multi-agent DAG orchestration
- `05_custom_orchestrator.py` — Building a custom BaseAgent orchestrator

## Setup
```bash
pip install google-adk>=2.0.0a1
export GOOGLE_API_KEY="your-gemini-api-key"

# Security note: if you have LiteLLM installed, ensure it is NOT 1.82.7 or 1.82.8
pip install litellm!=1.82.7,!=1.82.8
```

## ⚠️ Security Advisory
Unauthorized code was found in LiteLLM versions 1.82.7 and 1.82.8 on PyPI (March 24, 2026).
If you used ADK Python with `eval` or `extensions` extras, rotate all secrets and credentials immediately.
