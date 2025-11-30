import uuid
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StdioServerParameters,
)
from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.events.event import Event
from IPython.display import display, Image as IPImage
import base64

class McpAndMultiAgent:
    """A class to hold day 3 assignment implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def do_something(self):
        print("Doing day 3 assignment")
        self.GOOGLE_API_KEY = self.api_key

        retry_config = self._create_retry_config()

        # MCP integration with Everything Server
        mcp_image_server = self._create_mcp_toolset()

        image_agent = self._create_image_agent(mcp_image_server, retry_config)

        runner = InMemoryRunner(agent=image_agent)
        response = await runner.run_debug("Provide a sample tiny image", verbose=True)

        self.display_image(response)

    def _create_retry_config(self) -> types.HttpRetryOptions:
        return types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

    def _create_mcp_toolset(self) -> McpToolset:
        """Creates and returns an McpToolset for the Everything Server."""
        mcp_image_server = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",  # Run MCP server via npx
                    args=[
                        "-y",  # Argument for npx to auto-confirm install
                        "@modelcontextprotocol/server-everything",
                    ],
                    tool_filter=["getTinyImage"],
                ),
                timeout=30,
            )
        )

        print("✅ MCP Tool created")
        return mcp_image_server

    def _create_image_agent(self, mcp_image_server: McpToolset, retry_config: types.HttpRetryOptions) -> LlmAgent:
        """Creates and returns an image agent."""
        return LlmAgent(
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            name="image_agent",
            instruction="Use the MCP Tool to generate images for user queries",
            tools=[mcp_image_server],
        )

    def display_image(self, events: list[Event]):
        """Displays an image from a base64-encoded string."""
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "function_response") and part.function_response:
                        for item in part.function_response.response.get("content", []):
                            if item.get("type") == "image":
                                display(IPImage(data=base64.b64decode(item["data"])))