/**
 * Blog 05 — ADK for TypeScript (December 2025)
 * Example 4: Real-Time Streaming Agent
 *
 * Source: https://developers.googleblog.com/introducing-agent-development-kit-for-typescript-build-ai-agents-with-the-power-of-a-code-first-approach/
 *
 * ADK TypeScript supports real-time streaming for immediate feedback.
 * Tokens appear as they are generated, reducing perceived latency.
 * This example also shows how to use the @google/adk-devtools dev UI.
 *
 * Run:
 *   export GOOGLE_API_KEY="your-api-key"
 *   npx ts-node 04_streaming_agent.ts
 *
 * Or launch the dev UI:
 *   npx adk web
 */

import { LlmAgent, GOOGLE_SEARCH, InMemorySessionService, Runner } from '@google/adk';
import * as process from 'process';

// ── Streaming agent definition ────────────────────────────────────────────────
const streamingAgent = new LlmAgent({
  name: 'streaming_assistant',
  model: 'gemini-2.5-flash',
  description: 'A helpful assistant with real-time streaming responses.',
  instruction:
    'You are a helpful assistant. Provide detailed, well-structured answers. ' +
    'Use Google Search when you need current information.',
  tools: [GOOGLE_SEARCH],
});

// ── Streaming helper ──────────────────────────────────────────────────────────
async function streamResponse(
  runner: Runner,
  sessionId: string,
  userId: string,
  message: string
): Promise<void> {
  process.stdout.write(`User: ${message}\nAgent: `);

  const events = runner.runAsync({
    userId,
    sessionId,
    newMessage: { role: 'user', parts: [{ text: message }] },
  });

  for await (const event of events) {
    // Partial events stream tokens as they arrive
    if (event.content?.parts) {
      for (const part of event.content.parts) {
        if (part.text) {
          process.stdout.write(part.text);
        }
      }
    }

    if (event.isFinalResponse()) {
      process.stdout.write('\n\n');
    }
  }
}

// ── Session callback: log agent actions ───────────────────────────────────────
function createDebugRunner(agent: LlmAgent, appName: string): Runner {
  const sessionService = new InMemorySessionService();

  return new Runner({
    agent,
    appName,
    sessionService,
    // Callback fires on every event for debugging
    onEvent: (event) => {
      if (event.isToolCall()) {
        const toolName = event.toolCall?.name ?? 'unknown';
        console.log(`\n[DEBUG] Tool called: ${toolName}`);
      }
      if (event.isToolResponse()) {
        console.log(`[DEBUG] Tool response received`);
      }
    },
  });
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main(): Promise<void> {
  const sessionService = new InMemorySessionService();

  const session = await sessionService.createSession({
    appName: 'streaming_ts_app',
    userId: 'user_01',
  });

  const runner = new Runner({
    agent: streamingAgent,
    appName: 'streaming_ts_app',
    sessionService,
  });

  console.log('=== ADK TypeScript Streaming Demo ===\n');

  const prompts = [
    'Explain why TypeScript is a great choice for building AI agent systems.',
    'What are the differences between ADK TypeScript and ADK Python?',
  ];

  for (const prompt of prompts) {
    await streamResponse(runner, session.id, 'user_01', prompt);
  }

  console.log('\n=== Dev UI ===');
  console.log('To launch the interactive dev UI, run:');
  console.log('  npx adk web');
  console.log('\nThe dev UI lets you:');
  console.log('  ✓ Chat with your agents interactively');
  console.log('  ✓ Inspect tool calls and responses');
  console.log('  ✓ View session state in real-time');
  console.log('  ✓ Debug agent decision-making');
}

main().catch(console.error);
