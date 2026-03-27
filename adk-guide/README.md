# Google ADK Guide — Code from All 6 Official Blogs

A structured collection of runnable code examples extracted and adapted from the
6 official Google Agent Development Kit (ADK) blog posts.

---

## Blog Index

| # | Blog | Date | Language | Folder |
|---|------|------|----------|--------|
| 1 | [Making it Easy to Build Multi-Agent Applications](https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/) | Apr 2025 | Python | `blog_01_initial_launch_multi_agent/` |
| 2 | [ADK Python v1.0, Java ADK & Agent Engine (Google I/O)](https://developers.googleblog.com/agents-adk-agent-engine-a2a-enhancements-google-io/) | May 2025 | Python + Java | `blog_02_python_v1_java_google_io/` |
| 3 | [Announcing ADK for Go](https://developers.googleblog.com/announcing-the-agent-development-kit-for-go-build-powerful-ai-agents-with-your-favorite-languages/) | Nov 2025 | Go | `blog_03_adk_for_go/` |
| 4 | [Building Agents with the ADK and the Interactions API](https://developers.googleblog.com/building-agents-with-the-adk-and-the-new-interactions-api/) | Dec 2025 | Python | `blog_04_interactions_api/` |
| 5 | [Introducing ADK for TypeScript](https://developers.googleblog.com/introducing-agent-development-kit-for-typescript-build-ai-agents-with-the-power-of-a-code-first-approach/) | Dec 2025 | TypeScript | `blog_05_adk_for_typescript/` |
| 6 | [ADK Python 2.0 Alpha: Graph-Based Workflows](https://google.github.io/adk-docs/) | Mar 2026 | Python | `blog_06_python_2_alpha_graph_workflows/` |

---

## Quick Setup

```bash
# Python blogs (1, 2, 4, 6)
pip install google-adk google-cloud-aiplatform
export GOOGLE_API_KEY="your-gemini-api-key"

# Go blog (3)
go get google.golang.org/adk
export GOOGLE_API_KEY="your-gemini-api-key"

# TypeScript blog (5)
cd blog_05_adk_for_typescript
npm install
export GOOGLE_API_KEY="your-gemini-api-key"
```

---

## What Each Blog Covers

### Blog 1 — Initial Launch (April 2025)
- Single agent with Google Search
- Custom Python tool agents
- Multi-agent coordinator + sub-agents
- Real-time streaming
- MCP (Model Context Protocol) tool integration

### Blog 2 — Python v1.0 & Java ADK (Google I/O, May 2025)
- Sequential agent pipelines
- Parallel research agents
- Deploy to Vertex AI Agent Engine
- Session state for inter-agent communication
- Java ADK basic agent

### Blog 3 — ADK for Go (November 2025)
- Basic Go agent
- Custom Go tool functions
- Multi-agent with A2A protocol
- Database agent with MCP Toolbox

### Blog 4 — Interactions API (December 2025)
- Basic Interactions API call
- Stateful multi-turn conversation (`previous_interaction_id`)
- Background execution for long-running tasks
- Deep Research Agent integration
- ADK + Interactions API transport

### Blog 5 — ADK for TypeScript (December 2025)
- Basic TypeScript agent
- Custom TypeScript tools with type safety
- Multi-agent coordinator system
- Streaming agent with dev UI

### Blog 6 — Python 2.0 Alpha: Graph Workflows (March 2026)
- Loop agent (iterative refinement)
- Conditional routing / triage
- Human-in-the-loop with tool confirmation
- Full DAG (directed acyclic graph) pipeline
- Custom BaseAgent orchestrator

---

## Key Concepts Across All Blogs

| Concept | Description |
|---------|-------------|
| `LlmAgent` | Core agent powered by a Gemini (or other) LLM |
| `SequentialAgent` | Runs sub-agents one after another |
| `ParallelAgent` | Runs sub-agents concurrently |
| `LoopAgent` | Runs sub-agents in a loop until condition met |
| `BaseAgent` | Base class for custom orchestrators |
| `FunctionTool` | Wraps any function as an agent tool |
| `MCPToolset` | Connects to MCP servers for external tools |
| `Runner` | Executes agents and manages the event loop |
| `InMemorySessionService` | Local session management (dev/testing) |
| Session state | Shared key-value store for inter-agent data |

---

⚠️ **Security Note (March 2026):** Unauthorized code was found in LiteLLM 1.82.7–1.82.8.
If you use ADK with `eval` or `extensions` extras, run: `pip install litellm!=1.82.7,!=1.82.8`
and rotate all secrets.
