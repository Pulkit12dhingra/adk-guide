"""
Blog 01 — Google ADK Initial Launch (April 2025)
Example 2: Agent with a Custom Python Tool

Source: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/

ADK treats any Python function as a tool. The docstring is used by the LLM
to understand when and how to call the function.
"""

import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Custom tool: weather lookup (mocked) ─────────────────────────────────────
def get_weather(city: str) -> dict:
    """
    Retrieves the current weather for a given city.

    Args:
        city: The name of the city to get weather for (e.g., "London", "Tokyo").

    Returns:
        A dictionary containing 'temperature', 'condition', and 'humidity'.
    """
    # In production, call a real weather API here.
    mock_data = {
        "london":  {"temperature": "15°C", "condition": "Cloudy",  "humidity": "78%"},
        "tokyo":   {"temperature": "22°C", "condition": "Sunny",   "humidity": "55%"},
        "new york":{"temperature": "18°C", "condition": "Partly Cloudy", "humidity": "62%"},
        "sydney":  {"temperature": "25°C", "condition": "Clear",   "humidity": "45%"},
    }
    return mock_data.get(city.lower(), {
        "temperature": "N/A",
        "condition":   "Unknown",
        "humidity":    "N/A",
    })


# ── Custom tool: unit conversion ──────────────────────────────────────────────
def convert_temperature(value: float, from_unit: str, to_unit: str) -> dict:
    """
    Converts a temperature value between Celsius, Fahrenheit, and Kelvin.

    Args:
        value: The numeric temperature value to convert.
        from_unit: The source unit — 'celsius', 'fahrenheit', or 'kelvin'.
        to_unit: The target unit — 'celsius', 'fahrenheit', or 'kelvin'.

    Returns:
        A dictionary with 'result' (float) and 'unit' (str).
    """
    # Normalise to Celsius first
    celsius_map = {
        "celsius":    lambda v: v,
        "fahrenheit": lambda v: (v - 32) * 5 / 9,
        "kelvin":     lambda v: v - 273.15,
    }
    to_map = {
        "celsius":    lambda c: c,
        "fahrenheit": lambda c: c * 9 / 5 + 32,
        "kelvin":     lambda c: c + 273.15,
    }
    celsius = celsius_map[from_unit.lower()](value)
    result  = to_map[to_unit.lower()](celsius)
    return {"result": round(result, 2), "unit": to_unit}


# ── Define the agent ──────────────────────────────────────────────────────────
weather_agent = Agent(
    name="weather_assistant",
    model="gemini-2.5-flash",
    instruction=(
        "You are a weather assistant. Use the get_weather tool to fetch current "
        "conditions for any city. If asked about temperatures in different units, "
        "use the convert_temperature tool."
    ),
    description="An agent that provides weather information and temperature conversions.",
    tools=[get_weather, convert_temperature],
)


# ── Run the agent ─────────────────────────────────────────────────────────────
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="weather_app", user_id="user_01"
    )
    runner = Runner(
        agent=weather_agent,
        app_name="weather_app",
        session_service=session_service,
    )

    queries = [
        "What is the weather like in Tokyo right now?",
        "Convert 22 degrees Celsius to Fahrenheit.",
    ]

    for query in queries:
        print(f"User: {query}")
        async for event in runner.run_async(
            user_id="user_01",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=query)]
            ),
        ):
            if event.is_final_response():
                print(f"Agent: {event.content.parts[0].text}\n")


if __name__ == "__main__":
    asyncio.run(main())
