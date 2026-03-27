# Blog 01 — Agent Development Kit: Making it Easy to Build Multi-Agent Applications
**Published:** April 9, 2025 (Google Cloud NEXT 2025)
**Source:** https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/

## What This Blog Covers
Google introduced ADK as an open-source, code-first Python framework for building multi-agent applications.
Key themes: rich tool ecosystem, built-in streaming, model-agnostic design, and multi-agent orchestration.

## Files in This Folder
- `01_single_agent.py` — A single agent using Google Search
- `02_custom_tool_agent.py` — Agent with a custom Python tool
- `03_multi_agent_system.py` — Multi-agent system with coordinator, greeter, and task executor
- `04_streaming_agent.py` — Real-time bidirectional streaming agent
- `05_mcp_tool_agent.py` — Agent using Model Context Protocol (MCP) tools

## Setup
```bash
pip install google-adk
export GOOGLE_API_KEY="your-gemini-api-key"
```
