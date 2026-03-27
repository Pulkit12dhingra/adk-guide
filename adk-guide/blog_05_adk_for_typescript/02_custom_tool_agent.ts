/**
 * Blog 05 — ADK for TypeScript (December 2025)
 * Example 2: Agent with Custom TypeScript Tools
 *
 * Source: https://developers.googleblog.com/introducing-agent-development-kit-for-typescript-build-ai-agents-with-the-power-of-a-code-first-approach/
 *
 * Custom TypeScript functions can be registered as ADK tools using FunctionTool.
 * The type annotations and JSDoc comments help ADK generate the correct schema
 * for the LLM to understand when and how to call each function.
 *
 * Run:
 *   export GOOGLE_API_KEY="your-api-key"
 *   npx ts-node 02_custom_tool_agent.ts
 */

import { LlmAgent, FunctionTool, InMemorySessionService, Runner } from '@google/adk';

// ── Tool types ────────────────────────────────────────────────────────────────
interface WeatherResult {
  city: string;
  temperature: string;
  condition: string;
  humidity: string;
  feelsLike: string;
}

interface ConversionResult {
  original: number;
  originalUnit: string;
  converted: number;
  convertedUnit: string;
}

// ── Tool 1: Weather lookup ────────────────────────────────────────────────────
/**
 * Retrieves the current weather for a specified city.
 * @param city - The city name to look up weather for (e.g., "Tokyo", "London")
 * @returns Current weather data including temperature, condition, and humidity
 */
function getWeather(city: string): WeatherResult {
  const weatherData: Record<string, WeatherResult> = {
    london: {
      city: 'London',
      temperature: '15°C',
      condition: 'Cloudy',
      humidity: '78%',
      feelsLike: '13°C',
    },
    tokyo: {
      city: 'Tokyo',
      temperature: '22°C',
      condition: 'Sunny',
      humidity: '55%',
      feelsLike: '24°C',
    },
    'new york': {
      city: 'New York',
      temperature: '18°C',
      condition: 'Partly Cloudy',
      humidity: '62%',
      feelsLike: '17°C',
    },
    sydney: {
      city: 'Sydney',
      temperature: '25°C',
      condition: 'Clear',
      humidity: '45%',
      feelsLike: '27°C',
    },
  };

  return (
    weatherData[city.toLowerCase()] ?? {
      city,
      temperature: 'N/A',
      condition: 'Unknown',
      humidity: 'N/A',
      feelsLike: 'N/A',
    }
  );
}

// ── Tool 2: Currency conversion ───────────────────────────────────────────────
/**
 * Converts an amount from one currency to another using approximate rates.
 * @param amount - The numeric amount to convert
 * @param fromCurrency - The source currency code (e.g., "USD", "EUR", "GBP")
 * @param toCurrency - The target currency code (e.g., "USD", "EUR", "JPY")
 * @returns The converted amount with both original and converted values
 */
function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string
): ConversionResult {
  // Approximate exchange rates relative to USD
  const ratesUSD: Record<string, number> = {
    USD: 1.0,
    EUR: 0.92,
    GBP: 0.79,
    JPY: 149.5,
    AUD: 1.52,
    CAD: 1.36,
    INR: 83.2,
    CHF: 0.9,
  };

  const fromRate = ratesUSD[fromCurrency.toUpperCase()] ?? 1;
  const toRate = ratesUSD[toCurrency.toUpperCase()] ?? 1;

  // Convert: source → USD → target
  const inUSD = amount / fromRate;
  const converted = inUSD * toRate;

  return {
    original: amount,
    originalUnit: fromCurrency.toUpperCase(),
    converted: Math.round(converted * 100) / 100,
    convertedUnit: toCurrency.toUpperCase(),
  };
}

// ── Tool 3: Text statistics ───────────────────────────────────────────────────
/**
 * Calculates statistics for a given text string.
 * @param text - The text to analyse
 * @returns Statistics including word count, character count, and reading time
 */
function analyseText(text: string): {
  wordCount: number;
  charCount: number;
  sentenceCount: number;
  avgWordLength: number;
  estimatedReadingTimeSeconds: number;
} {
  const words = text.trim().split(/\s+/).filter(Boolean);
  const sentences = text.split(/[.!?]+/).filter(Boolean);
  const avgWordLen =
    words.reduce((sum, w) => sum + w.length, 0) / (words.length || 1);

  return {
    wordCount: words.length,
    charCount: text.length,
    sentenceCount: sentences.length,
    avgWordLength: Math.round(avgWordLen * 10) / 10,
    estimatedReadingTimeSeconds: Math.ceil((words.length / 200) * 60), // avg 200 wpm
  };
}

// ── Define the agent with multiple tools ──────────────────────────────────────
const utilityAgent = new LlmAgent({
  name: 'utility_assistant',
  model: 'gemini-2.5-flash',
  description:
    'A versatile assistant with weather lookup, currency conversion, and text analysis.',
  instruction:
    'You are a helpful utility assistant. Use your tools to: ' +
    'check weather with getWeather, convert currencies with convertCurrency, ' +
    'and analyse text with analyseText. Always present results clearly.',
  tools: [
    new FunctionTool(getWeather),
    new FunctionTool(convertCurrency),
    new FunctionTool(analyseText),
  ],
});

// ── Run queries ───────────────────────────────────────────────────────────────
async function main(): Promise<void> {
  const sessionService = new InMemorySessionService();
  const session = await sessionService.createSession({
    appName: 'utility_app',
    userId: 'user_01',
  });

  const runner = new Runner({
    agent: utilityAgent,
    appName: 'utility_app',
    sessionService,
  });

  const queries = [
    "What's the weather in Tokyo?",
    'Convert 500 USD to Japanese Yen.',
    'Analyse this text: "Google ADK makes it incredibly easy to build powerful multi-agent AI systems in TypeScript."',
  ];

  for (const query of queries) {
    console.log(`User: ${query}`);

    const events = runner.runAsync({
      userId: 'user_01',
      sessionId: session.id,
      newMessage: { role: 'user', parts: [{ text: query }] },
    });

    for await (const event of events) {
      if (event.isFinalResponse()) {
        console.log(`Agent: ${event.content?.parts?.[0]?.text ?? ''}\n`);
      }
    }
  }
}

main().catch(console.error);
