# Blog 03 — Announcing the Agent Development Kit for Go
**Published:** November 7, 2025
**Source:** https://developers.googleblog.com/announcing-the-agent-development-kit-for-go-build-powerful-ai-agents-with-your-favorite-languages/

## What This Blog Covers
Google expanded the ADK family to Go — ideal for cloud-native applications leveraging
Go's concurrency model and performance. Key highlights:
- **Idiomatic Go** — designed to feel natural to Go developers
- **Agent2Agent (A2A) Protocol** — multi-agent collaboration across services
- **MCP Toolbox for Databases** — 30+ database integrations out of the box
- **Cloud-native deployment** — Cloud Run and GKE ready

## Files in This Folder
- `01_basic_agent/main.go` — Simple agent with Google Search
- `02_custom_tool_agent/main.go` — Agent with a custom Go tool
- `03_multi_agent_a2a/main.go` — Multi-agent system using A2A protocol
- `04_database_agent/main.go` — Agent with MCP Toolbox for Databases
- `go.mod` — Go module definition

## Setup
```bash
go get google.golang.org/adk
export GOOGLE_API_KEY="your-gemini-api-key"

# Run an example
cd 01_basic_agent && go run main.go
```
