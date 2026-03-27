// Blog 03 — ADK for Go (November 2025)
// Example 3: Multi-Agent System with Agent2Agent (A2A) Protocol
//
// Source: https://developers.googleblog.com/announcing-the-agent-development-kit-for-go-build-powerful-ai-agents-with-your-favorite-languages/
//
// ADK for Go includes built-in support for the Agent2Agent (A2A) protocol,
// which allows a primary agent to securely delegate tasks to specialised
// sub-agents — whether running locally or as remote services.
//
// This example shows a coordinator agent orchestrating two specialised agents.
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

	model, err := google_llm.NewGemini("gemini-2.5-flash")
	if err != nil {
		log.Fatalf("model error: %v", err)
	}

	// ── Sub-Agent 1: Code Reviewer ───────────────────────────────────────────
	codeReviewer, _ := agents.NewLlmAgent(agents.LlmAgentConfig{
		Name:  "code_reviewer",
		Model: model,
		Description: "Specialised in reviewing Go code for correctness, " +
			"idiomatic patterns, performance, and security issues.",
		Instruction: "You are an expert Go code reviewer. When given code, " +
			"analyse it for bugs, performance issues, security vulnerabilities, " +
			"and non-idiomatic patterns. Provide specific, actionable feedback.",
	})

	// ── Sub-Agent 2: Documentation Writer ────────────────────────────────────
	docWriter, _ := agents.NewLlmAgent(agents.LlmAgentConfig{
		Name:  "doc_writer",
		Model: model,
		Description: "Specialised in writing clear, comprehensive Go documentation " +
			"including GoDoc comments and README content.",
		Instruction: "You are an expert technical writer for Go projects. " +
			"Write clear GoDoc comments, package documentation, and README content " +
			"following Go conventions and best practices.",
	})

	// ── Coordinator: routes to sub-agents via A2A ─────────────────────────────
	// Using sub-agents as AgentTools allows the coordinator to delegate
	// while maintaining the A2A protocol's security boundaries.
	codeReviewerTool, _ := tools.NewAgentTool(codeReviewer)
	docWriterTool, _ := tools.NewAgentTool(docWriter)

	coordinator, _ := agents.NewLlmAgent(agents.LlmAgentConfig{
		Name:  "engineering_coordinator",
		Model: model,
		Instruction: "You are an engineering assistant coordinator. " +
			"For code review requests, delegate to 'code_reviewer'. " +
			"For documentation requests, delegate to 'doc_writer'. " +
			"You may also combine both for comprehensive code improvement requests.",
		Tools: []tools.Tool{codeReviewerTool, docWriterTool},
	})

	// ── Runner setup ─────────────────────────────────────────────────────────
	sessionService := sessions.NewInMemorySessionService()
	session, _ := sessionService.CreateSession(ctx, "eng_app", "user_01", nil)
	runner, _ := runners.NewRunner(runners.RunnerConfig{
		Agent: coordinator, AppName: "eng_app", SessionService: sessionService,
	})

	// ── Demo queries ──────────────────────────────────────────────────────────
	goCode := `
func fetchData(url string) []byte {
    resp, _ := http.Get(url)
    data, _ := io.ReadAll(resp.Body)
    return data
}`

	queries := []string{
		"Please review this Go code and suggest improvements:\n" + goCode,
		"Write GoDoc comments and a brief README section for a function " +
			"that fetches HTTP data and handles errors properly.",
	}

	for _, q := range queries {
		fmt.Printf("User: %s\n\n", q)
		for event := range runner.RunAsync(ctx, "user_01", session.ID, q) {
			if event.IsFinalResponse() {
				fmt.Printf("Coordinator: %s\n\n", event.Content.Parts[0].Text)
				fmt.Println("─────────────────────────────────────────────────")
			}
		}
	}
}
