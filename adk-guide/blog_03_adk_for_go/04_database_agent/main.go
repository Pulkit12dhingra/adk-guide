// Blog 03 — ADK for Go (November 2025)
// Example 4: Agent with MCP Toolbox for Databases
//
// Source: https://developers.googleblog.com/announcing-the-agent-development-kit-for-go-build-powerful-ai-agents-with-your-favorite-languages/
//
// ADK for Go has out-of-the-box support for 30+ databases through the
// MCP Toolbox for Databases. This lets agents query, analyse, and manage
// data in PostgreSQL, BigQuery, AlloyDB, Spanner, and more.
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
	"google.golang.org/adk/tools/mcp"
)

func main() {
	ctx := context.Background()

	// ── Connect to MCP Toolbox for Databases ─────────────────────────────────
	// The MCP Toolbox server exposes database operations as MCP tools.
	// Start the toolbox server locally:
	//   docker run -p 5000:5000 gcr.io/cloud-toolbox/mcp-toolbox:latest
	//   (configure with your database connection in toolbox.yaml)
	mcpClient, err := mcp.NewSSEClient(mcp.SSEConfig{
		URL: "http://localhost:5000/sse", // MCP Toolbox server endpoint
	})
	if err != nil {
		log.Fatalf("failed to connect to MCP Toolbox: %v", err)
	}
	defer mcpClient.Close()

	// Discover all tools exposed by the toolbox server
	dbTools, err := mcpClient.ListTools(ctx)
	if err != nil {
		log.Fatalf("failed to list tools: %v", err)
	}

	fmt.Printf("Connected to MCP Toolbox — %d tools available:\n", len(dbTools))
	for _, t := range dbTools {
		fmt.Printf("  • %s: %s\n", t.Name(), t.Description())
	}
	fmt.Println()

	// ── Build the database agent ──────────────────────────────────────────────
	model, _ := google_llm.NewGemini("gemini-2.5-flash")

	dbAgent, _ := agents.NewLlmAgent(agents.LlmAgentConfig{
		Name:  "database_analyst",
		Model: model,
		Instruction: "You are a database analyst assistant. Use the available " +
			"database tools to query, analyse, and summarise data. " +
			"Always explain what queries you're running and why. " +
			"Format results in a human-readable way.",
		Tools: dbTools, // inject all discovered MCP tools
	})

	// ── Session and runner ────────────────────────────────────────────────────
	sessionService := sessions.NewInMemorySessionService()
	session, _ := sessionService.CreateSession(ctx, "db_app", "user_01", nil)
	runner, _ := runners.NewRunner(runners.RunnerConfig{
		Agent: dbAgent, AppName: "db_app", SessionService: sessionService,
	})

	// ── Demo queries (adjust to match your database schema) ──────────────────
	queries := []string{
		"List all tables available in the database.",
		"How many records are in the users table?",
		"Show me the top 5 most recently created records.",
	}

	for _, q := range queries {
		fmt.Printf("User: %s\n", q)
		for event := range runner.RunAsync(ctx, "user_01", session.ID, q) {
			if event.IsFinalResponse() {
				fmt.Printf("Agent: %s\n\n", event.Content.Parts[0].Text)
			}
		}
	}
}
