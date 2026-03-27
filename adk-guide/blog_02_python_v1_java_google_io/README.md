# Blog 02 — What's New with Agents: ADK Python v1.0, Java ADK & Agent Engine
**Published:** May 20, 2025 (Google I/O 2025)
**Source:** https://developers.googleblog.com/agents-adk-agent-engine-a2a-enhancements-google-io/

## What This Blog Covers
- **Python ADK v1.0.0** — stable, production-ready release
- **Java ADK v0.1.0** — initial release bringing ADK to the Java ecosystem
- **Vertex AI Agent Engine** — managed deployment for agents with a UI dashboard
- **Agent2Agent (A2A) Protocol** enhancements for multi-agent collaboration
- Sequential and parallel workflow agents

## Files in This Folder
- `01_sequential_agent_pipeline.py` — Pipeline: agents run one after another
- `02_parallel_agent_research.py` — Parallel web research agents
- `03_deploy_to_agent_engine.py` — Deploy to Vertex AI Agent Engine
- `04_agent_with_session_state.py` — Using session state for inter-agent communication
- `HelloTimeAgent.java` — Java ADK basic agent example

## Setup (Python)
```bash
pip install google-adk google-cloud-aiplatform
export GOOGLE_API_KEY="your-gemini-api-key"
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
```

## Setup (Java)
```xml
<!-- pom.xml dependency -->
<dependency>
  <groupId>com.google.adk</groupId>
  <artifactId>google-adk</artifactId>
  <version>0.1.0</version>
</dependency>
```
