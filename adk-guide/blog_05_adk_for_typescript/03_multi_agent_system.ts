/**
 * Blog 05 — ADK for TypeScript (December 2025)
 * Example 3: Multi-Agent System with Coordinator Pattern
 *
 * Source: https://developers.googleblog.com/introducing-agent-development-kit-for-typescript-build-ai-agents-with-the-power-of-a-code-first-approach/
 *
 * ADK for TypeScript supports the same multi-agent patterns as Python:
 * a coordinator routes to specialised sub-agents. Type safety makes
 * agent configurations self-documenting.
 *
 * Run:
 *   export GOOGLE_API_KEY="your-api-key"
 *   npx ts-node 03_multi_agent_system.ts
 */

import {
  LlmAgent,
  GOOGLE_SEARCH,
  FunctionTool,
  InMemorySessionService,
  Runner,
  type Content,
} from '@google/adk';

// ── Tool: code execution (mock) ───────────────────────────────────────────────
/**
 * Executes a TypeScript/JavaScript code snippet and returns the result.
 * @param code - The code snippet to execute
 * @param language - The programming language ('typescript' or 'javascript')
 * @returns Execution result or error message
 */
function executeCode(code: string, language: string = 'javascript'): string {
  // In production, use a sandboxed execution environment
  try {
    if (language === 'javascript' || language === 'typescript') {
      // Safe eval for simple expressions only
      const result = new Function(`"use strict"; return (${code})`)();
      return `Result: ${JSON.stringify(result)}`;
    }
    return `Language '${language}' not supported in this sandbox.`;
  } catch (err) {
    return `Error: ${err instanceof Error ? err.message : String(err)}`;
  }
}

// ── Sub-Agent 1: Research Agent ───────────────────────────────────────────────
const researchAgent = new LlmAgent({
  name: 'research_agent',
  model: 'gemini-2.5-flash',
  description:
    'Specialises in web research and information retrieval. ' +
    'Use for questions requiring up-to-date facts, documentation, or news.',
  instruction:
    'You are a research specialist. Search the web for accurate, current information. ' +
    'Always cite sources and present findings in a structured way.',
  tools: [GOOGLE_SEARCH],
});

// ── Sub-Agent 2: Code Assistant ───────────────────────────────────────────────
const codeAgent = new LlmAgent({
  name: 'code_assistant',
  model: 'gemini-2.5-flash',
  description:
    'Specialises in writing, reviewing, and executing TypeScript/JavaScript code. ' +
    'Use for coding questions, code generation, and technical implementation.',
  instruction:
    'You are an expert TypeScript/JavaScript developer. Write clean, well-typed, ' +
    'idiomatic code with clear explanations. Use executeCode to test snippets.',
  tools: [new FunctionTool(executeCode)],
});

// ── Sub-Agent 3: Writing Assistant ───────────────────────────────────────────
const writingAgent = new LlmAgent({
  name: 'writing_assistant',
  model: 'gemini-2.5-flash',
  description:
    'Specialises in writing, editing, and improving text content. ' +
    'Use for content creation, summaries, documentation, and editing tasks.',
  instruction:
    'You are a professional writer and editor. Produce clear, engaging, well-structured ' +
    'content. Adapt tone and style to the audience and purpose.',
});

// ── Coordinator Agent ─────────────────────────────────────────────────────────
const coordinator = new LlmAgent({
  name: 'coordinator',
  model: 'gemini-2.5-flash',
  description: 'Routes requests to the most appropriate specialised sub-agent.',
  instruction: `You are the main coordinator for a TypeScript AI assistant.
Analyse the user's request and route to the best sub-agent:
- "research_agent": for facts, documentation, current events, web searches
- "code_assistant": for coding, TypeScript, JavaScript, technical implementation
- "writing_assistant": for content creation, editing, summaries, documentation

Always delegate — do not answer directly. After receiving the sub-agent's
response, present it clearly to the user with any relevant context.`,
  subAgents: [researchAgent, codeAgent, writingAgent],
});

// ── Run the multi-agent system ────────────────────────────────────────────────
async function main(): Promise<void> {
  const sessionService = new InMemorySessionService();
  const session = await sessionService.createSession({
    appName: 'multi_agent_ts_app',
    userId: 'user_01',
  });

  const runner = new Runner({
    agent: coordinator,
    appName: 'multi_agent_ts_app',
    sessionService,
  });

  const queries: string[] = [
    'What are the latest features in TypeScript 5.4?',
    'Write a TypeScript function that debounces another function with generic types.',
    'Write a short blog introduction about why TypeScript is perfect for AI agent development.',
  ];

  for (const query of queries) {
    console.log(`User: ${query}`);

    const newMessage: Content = {
      role: 'user',
      parts: [{ text: query }],
    };

    const events = runner.runAsync({
      userId: 'user_01',
      sessionId: session.id,
      newMessage,
    });

    for await (const event of events) {
      if (event.isFinalResponse()) {
        const text = event.content?.parts?.[0]?.text ?? '';
        console.log(`Agent: ${text.slice(0, 400)}${text.length > 400 ? '...' : ''}\n`);
      }
    }
  }
}

main().catch(console.error);
