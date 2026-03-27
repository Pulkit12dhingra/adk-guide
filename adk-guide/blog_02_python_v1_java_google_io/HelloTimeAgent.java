/**
 * Blog 02 — ADK Python v1.0 & Java ADK (Google I/O, May 2025)
 * Java ADK v0.1.0 — Hello Time Agent
 *
 * Source: https://developers.googleblog.com/agents-adk-agent-engine-a2a-enhancements-google-io/
 *
 * The Java ADK was announced at Google I/O 2025. This example shows how to
 * build a basic agent in Java that tells the current time in a specified city.
 *
 * Maven dependency (pom.xml):
 * <dependency>
 *   <groupId>com.google.adk</groupId>
 *   <artifactId>google-adk</artifactId>
 *   <version>0.1.0</version>
 * </dependency>
 *
 * Environment variable:
 *   GOOGLE_API_KEY=your-gemini-api-key
 */

import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.adk.events.Event;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

public class HelloTimeAgent {

    // ── Custom tool: get current time in a city ──────────────────────────────
    /**
     * Returns the current time in the specified city's timezone.
     *
     * @param city The city name (e.g., "London", "Tokyo", "New York")
     * @return A map with "city", "current_time", and "timezone" keys
     */
    @Schema(description = "Gets the current time in a specified city.")
    public static Map<String, String> getCurrentTime(
            @Schema(description = "The name of the city to get the current time for.")
            String city) {

        Map<String, String> cityTimezones = Map.of(
            "london",   "Europe/London",
            "tokyo",    "Asia/Tokyo",
            "new york", "America/New_York",
            "sydney",   "Australia/Sydney",
            "paris",    "Europe/Paris",
            "berlin",   "Europe/Berlin",
            "mumbai",   "Asia/Kolkata"
        );

        String timezone = cityTimezones.getOrDefault(
            city.toLowerCase(), "UTC"
        );

        ZonedDateTime now = ZonedDateTime.now(ZoneId.of(timezone));
        String formattedTime = now.format(
            DateTimeFormatter.ofPattern("HH:mm:ss z, EEEE d MMMM yyyy")
        );

        return Map.of(
            "city",         city,
            "current_time", formattedTime,
            "timezone",     timezone
        );
    }

    // ── Main ─────────────────────────────────────────────────────────────────
    public static void main(String[] args) throws Exception {

        // Create the tool from the static method
        FunctionTool timeTool = FunctionTool.create(
            HelloTimeAgent.class.getMethod("getCurrentTime", String.class)
        );

        // Build the agent
        LlmAgent agent = LlmAgent.builder()
            .name("hello-time-agent")
            .model("gemini-2.5-flash")
            .description("An agent that tells the current time in any city.")
            .instruction(
                "You are a helpful time assistant. When asked about the time in "
                "a city, use the getCurrentTime tool to fetch the accurate time. "
                "Always be friendly and include the timezone in your response."
            )
            .tools(timeTool)
            .build();

        // Create a runner and session
        InMemoryRunner runner = new InMemoryRunner(agent, "time-app");
        Session session = runner.sessionService()
            .createSession("time-app", "user_01")
            .blockingGet();

        // Run a conversation
        String[] queries = {
            "What time is it in Tokyo right now?",
            "And what about in London?",
            "What's the time difference between Tokyo and London?"
        };

        for (String query : queries) {
            System.out.println("User: " + query);

            Content userMessage = Content.newBuilder()
                .setRole("user")
                .addParts(Part.fromText(query))
                .build();

            Flowable<Event> events = runner.runAsync("user_01", session.id(), userMessage);

            events.blockingForEach(event -> {
                if (event.finalResponse()) {
                    event.content().ifPresent(content ->
                        content.parts().ifPresent(parts ->
                            parts.stream()
                                .filter(p -> p.text().isPresent())
                                .forEach(p -> System.out.println("Agent: " + p.text().get()))
                        )
                    );
                }
            });
            System.out.println();
        }
    }
}
