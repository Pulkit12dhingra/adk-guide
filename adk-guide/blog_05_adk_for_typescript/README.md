# Blog 05 — Introducing Agent Development Kit for TypeScript
**Published:** December 17, 2025
**Source:** https://developers.googleblog.com/introducing-agent-development-kit-for-typescript-build-ai-agents-with-the-power-of-a-code-first-approach/

## What This Blog Covers
Google expanded ADK to TypeScript, bringing code-first agent development to the
JavaScript/TypeScript ecosystem. Key features:
- **Full TypeScript support** — type safety, IntelliSense, and modern tooling
- **Same ADK concepts** — agents, tools, sessions, runners — all in TypeScript
- **Built-in dev UI** — `@google/adk-devtools` for testing and debugging
- **Gemini-optimised** — works best with Gemini models, but model-agnostic
- **npm ecosystem** — integrates with any npm library as a tool

## Files in This Folder
- `01_basic_agent.ts` — Simple agent with Google Search
- `02_custom_tool_agent.ts` — Agent with custom TypeScript tools
- `03_multi_agent_system.ts` — Coordinator with sub-agents
- `04_streaming_agent.ts` — Real-time streaming responses
- `package.json` — Project dependencies
- `tsconfig.json` — TypeScript configuration

## Setup
```bash
npm install
export GOOGLE_API_KEY="your-gemini-api-key"

# Run with ts-node
npx ts-node 01_basic_agent.ts

# Or use the built-in dev UI
npx adk web
```
