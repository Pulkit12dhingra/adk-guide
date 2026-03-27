// Blog 03 — ADK for Go (November 2025)
// Example 2: Agent with a Custom Go Tool
//
// Source: https://developers.googleblog.com/announcing-the-agent-development-kit-for-go-build-powerful-ai-agents-with-your-favorite-languages/
//
// Custom Go functions can be registered as agent tools. ADK uses struct
// tags and type reflection to generate the JSON schema the LLM needs
// to understand when and how to call each function.
//
// Run:
//   export GOOGLE_API_KEY="your-api-key"
//   go run main.go

package main

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"google.golang.org/adk/agents"
	"google.golang.org/adk/models/google_llm"
	"google.golang.org/adk/runners"
	"google.golang.org/adk/sessions"
	"google.golang.org/adk/tools"
)

// ── Tool 1: Get current time ─────────────────────────────────────────────────

// GetTimeInput represents the input parameters for GetCurrentTime.
type GetTimeInput struct {
	City string `json:"city" description:"The city name to get the current time for (e.g., 'Tokyo', 'London')."`
}

// GetTimeOutput represents the output of GetCurrentTime.
type GetTimeOutput struct {
	City        string `json:"city"`
	CurrentTime string `json:"current_time"`
	Timezone    string `json:"timezone"`
}

// GetCurrentTime returns the current time for a given city.
func GetCurrentTime(ctx context.Context, input GetTimeInput) (*GetTimeOutput, error) {
	timezones := map[string]string{
		"london":   "Europe/London",
		"tokyo":    "Asia/Tokyo",
		"new york": "America/New_York",
		"sydney":   "Australia/Sydney",
		"berlin":   "Europe/Berlin",
	}

	tz, ok := timezones[strings.ToLower(input.City)]
	if !ok {
		tz = "UTC"
	}

	loc, err := time.LoadLocation(tz)
	if err != nil {
		return nil, fmt.Errorf("unknown timezone %q: %w", tz, err)
	}

	now := time.Now().In(loc)
	return &GetTimeOutput{
		City:        input.City,
		CurrentTime: now.Format("15:04:05 MST, Monday 2 January 2006"),
		Timezone:    tz,
	}, nil
}

// ── Tool 2: Calculate time difference ────────────────────────────────────────

// TimeDiffInput holds two city names for time zone comparison.
type TimeDiffInput struct {
	CityA string `json:"city_a" description:"The first city name."`
	CityB string `json:"city_b" description:"The second city name."`
}

// TimeDiffOutput holds the computed time difference.
type TimeDiffOutput struct {
	CityA       string `json:"city_a"`
	CityB       string `json:"city_b"`
	DiffHours   int    `json:"difference_hours"`
	Description string `json:"description"`
}

// GetTimeDifference calculates the hour difference between two cities.
func GetTimeDifference(ctx context.Context, input TimeDiffInput) (*TimeDiffOutput, error) {
	tzMap := map[string]string{
		"london":   "Europe/London",
		"tokyo":    "Asia/Tokyo",
		"new york": "America/New_York",
		"sydney":   "Australia/Sydney",
		"berlin":   "Europe/Berlin",
	}

	tzA := tzMap[strings.ToLower(input.CityA)]
	tzB := tzMap[strings.ToLower(input.CityB)]
	if tzA == "" { tzA = "UTC" }
	if tzB == "" { tzB = "UTC" }

	locA, _ := time.LoadLocation(tzA)
	locB, _ := time.LoadLocation(tzB)

	now := time.Now()
	offsetA := now.In(locA).UTC().Sub(now.UTC())
	offsetB := now.In(locB).UTC().Sub(now.UTC())
	diff := int((offsetB - offsetA).Hours())

	description := fmt.Sprintf(
		"%s is %d hours ahead of %s", input.CityB, diff, input.CityA,
	)
	if diff < 0 {
		description = fmt.Sprintf(
			"%s is %d hours behind %s", input.CityB, -diff, input.CityA,
		)
	}

	return &TimeDiffOutput{
		CityA: input.CityA, CityB: input.CityB,
		DiffHours: diff, Description: description,
	}, nil
}

// ── Main ──────────────────────────────────────────────────────────────────────

func main() {
	ctx := context.Background()

	model, _ := google_llm.NewGemini("gemini-2.5-flash")

	// Register custom Go functions as tools
	timeTool, err := tools.NewFunctionTool(
		"get_current_time",
		"Returns the current time in a specified city.",
		GetCurrentTime,
	)
	if err != nil {
		log.Fatalf("tool error: %v", err)
	}

	diffTool, _ := tools.NewFunctionTool(
		"get_time_difference",
		"Calculates the time difference in hours between two cities.",
		GetTimeDifference,
	)

	rootAgent, _ := agents.NewLlmAgent(agents.LlmAgentConfig{
		Name:  "time_assistant",
		Model: model,
		Instruction: "You are a world clock assistant. Use your tools to answer " +
			"questions about time in different cities.",
		Tools: []tools.Tool{timeTool, diffTool},
	})

	sessionService := sessions.NewInMemorySessionService()
	session, _ := sessionService.CreateSession(ctx, "time_app", "user_01", nil)
	runner, _ := runners.NewRunner(runners.RunnerConfig{
		Agent: rootAgent, AppName: "time_app", SessionService: sessionService,
	})

	queries := []string{
		"What time is it in Tokyo right now?",
		"What's the time difference between London and Sydney?",
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
