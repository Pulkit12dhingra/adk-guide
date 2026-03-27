// Blog 03 — ADK for Go (November 2025)
// Example 1: Basic Agent with Google Search
//
// Source: https://developers.googleblog.com/announcing-the-agent-development-kit-for-go-build-powerful-ai-agents-with-your-favorite-languages/
//
// The simplest ADK Go agent — connects to Gemini and uses Google Search
// to answer user questions.
//
// Run:
//   export GOOGLE_API_KEY="your-api-key"
//   go run main.go

package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/adk/agents"
	"google.golang.org/adk/models/google_llm"
	"google.golang.org/adk/runners"
	"google.golang.org/adk/sessions"
	"google.golang.org/adk/tools"
)

func main() {
	ctx := context.Background()

	// ── Create the Gemini model ──────────────────────────────────────────────
	model, err := google_llm.NewGemini("gemini-2.5-flash")
	if err != nil {
		log.Fatalf("failed to create model: %v", err)
	}

	// ── Build the agent ──────────────────────────────────────────────────────
	rootAgent, err := agents.NewLlmAgent(agents.LlmAgentConfig{
		Name:        "search_assistant",
		Model:       model,
		Description: "An assistant that can search the web.",
		Instruction: "You are a helpful assistant. Answer user questions using " +
			"Google Search when needed. Be concise and accurate.",
		Tools: []tools.Tool{
			tools.GoogleSearch, // built-in Google Search tool
		},
	})
	if err != nil {
		log.Fatalf("failed to create agent: %v", err)
	}

	// ── Set up session service and runner ────────────────────────────────────
	sessionService := sessions.NewInMemorySessionService()
	session, err := sessionService.CreateSession(ctx, "search_app", "user_01", nil)
	if err != nil {
		log.Fatalf("failed to create session: %v", err)
	}

	runner, err := runners.NewRunner(runners.RunnerConfig{
		Agent:          rootAgent,
		AppName:        "search_app",
		SessionService: sessionService,
	})
	if err != nil {
		log.Fatalf("failed to create runner: %v", err)
	}

	// ── Run a query ──────────────────────────────────────────────────────────
	query := "What are the main features of Google ADK for Go?"
	fmt.Printf("User: %s\n\n", query)

	eventCh := runner.RunAsync(ctx, "user_01", session.ID, query)

	for event := range eventCh {
		if event.Error != nil {
			log.Printf("error: %v", event.Error)
			continue
		}
		if event.IsFinalResponse() {
			fmt.Printf("Agent: %s\n", event.Content.Parts[0].Text)
		}
	}
}
