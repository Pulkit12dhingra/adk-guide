"""
Blog 01 — Google ADK Initial Launch (April 2025)
Example 5: Agent Using Model Context Protocol (MCP) Tools

Source: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/

ADK natively supports MCP tools, allowing agents to connect to any MCP server
(local subprocess or remote SSE endpoint). This unlocks a huge ecosystem of
pre-built integrations (file systems, databases, APIs, etc.).
"""

import asyncio
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# ── Example A: Connect to a local filesystem MCP server ──────────────────────
async def build_filesystem_agent():
    """
    Uses the official @modelcontextprotocol/server-filesystem MCP server
    to give the agent read/write access to a local directory.

    Prerequisites:
        npm install -g @modelcontextprotocol/server-filesystem
    """
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "/tmp/agent-workspace",   # directory the agent can access
            ],
        )
    )

    agent = Agent(
        name="filesystem_agent",
        model="gemini-2.5-flash",
        instruction=(
            "You are a file management assistant. Use the available MCP tools "
            "to read, list, and manage files in the workspace directory."
        ),
        description="Agent with local filesystem access via MCP.",
        tools=tools,
    )
    return agent, exit_stack


# ── Example B: Connect to a remote MCP server via SSE ────────────────────────
async def build_remote_mcp_agent():
    """
    Connects to a remote MCP server (e.g., a company's internal tool server)
    via Server-Sent Events (SSE).
    """
    from google.adk.tools.mcp_tool.mcp_toolset import SseServerParams

    tools, exit_stack = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="http://localhost:8080/sse",   # replace with your MCP server URL
        )
    )

    agent = Agent(
        name="remote_tools_agent",
        model="gemini-2.5-flash",
        instruction=(
            "You are an assistant with access to remote tools via MCP. "
            "Use the available tools to complete user requests."
        ),
        description="Agent connected to a remote MCP tool server.",
        tools=tools,
    )
    return agent, exit_stack


# ── Run the filesystem agent ──────────────────────────────────────────────────
async def main():
    agent, exit_stack = await build_filesystem_agent()

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="mcp_app", user_id="user_01"
    )
    runner = Runner(
        agent=agent,
        app_name="mcp_app",
        session_service=session_service,
    )

    try:
        query = "List all files in the workspace directory."
        print(f"User: {query}")
        async for event in runner.run_async(
            user_id="user_01",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=query)]
            ),
        ):
            if event.is_final_response():
                print(f"Agent: {event.content.parts[0].text}")
    finally:
        await exit_stack.aclose()   # always clean up MCP connections


if __name__ == "__main__":
    asyncio.run(main())
