/**
 * Blog 05 — ADK for TypeScript (December 2025)
 * Example 1: Basic Agent with Google Search
 *
 * Source: https://developers.googleblog.com/introducing-agent-development-kit-for-typescript-build-ai-agents-with-the-power-of-a-code-first-approach/
 *
 * The simplest ADK TypeScript agent — uses Google Search to answer questions.
 *
 * Run:
 *   export GOOGLE_API_KEY="your-api-key"
 *   npx ts-node 01_basic_agent.ts
 */

import { LlmAgent, GOOGLE_SEARCH, InMemorySessionService, Runner } from '@google/adk';

// ── Define the agent ──────────────────────────────────────────────────────────
const rootAgent = new LlmAgent({
  name: 'search_assistant',
  model: 'gemini-2.5-flash',
  description: 'An assistant that can search the web.',
  instruction:
    'You are a helpful assistant. Answer user questions using Google Search ' +
    'when needed. Be concise and accurate.',
  tools: [GOOGLE_SEARCH],
});

// ── Run the agent ─────────────────────────────────────────────────────────────
async function main(): Promise<void> {
  const sessionService = new InMemorySessionService();

  const session = await sessionService.createSession({
    appName: 'search_app',
    userId: 'user_01',
  });

  const runner = new Runner({
    agent: rootAgent,
    appName: 'search_app',
    sessionService,
  });

  const query = 'What are the latest features of Google ADK for TypeScript?';
  console.log(`User: ${query}\n`);

  const eventStream = runner.runAsync({
    userId: 'user_01',
    sessionId: session.id,
    newMessage: {
      role: 'user',
      parts: [{ text: query }],
    },
  });

  for await (const event of eventStream) {
    if (event.isFinalResponse()) {
      console.log(`Agent: ${event.content?.parts?.[0]?.text ?? ''}`);
    }
  }
}

main().catch(console.error);
