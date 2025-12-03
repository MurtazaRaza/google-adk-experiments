from typing import Any, Dict

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.genai import types

class Memory:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        # Define constants used throughout the notebook
        self.APP_NAME = "MemoryDemoApp"
        self.USER_ID = "demo_user"

        self.retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

    async def do_something(self):
        print("Doing day 4 assignment 2")
        # Create agent
        user_agent = LlmAgent(
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=self.retry_config),
            name="MemoryDemoAgent",
            instruction="Answer user questions in simple words.")

        # Create runner with BOTH services
        runner = Runner(
            agent=user_agent,
            app_name="MemoryDemoApp",
            session_service=self.session_service,
            memory_service=self.memory_service,  # Memory service is now available!
        )

        # User tells agent about their favorite color
        await self.run_session(
            runner,
            "My favorite color is blue-green. Can you write a Haiku about it?",
            "conversation-01",  # Session ID
        )

        session = await self.session_service.get_session(
        app_name=self.APP_NAME, user_id=self.USER_ID, session_id="conversation-01")

        # Let's see what's in the session
        print("📝 Session contains:")
        for event in session.events:
            text = (
                event.content.parts[0].text[:60]
                if event.content and event.content.parts
                else "(empty)"
            )
            print(f"  {event.content.role}: {text}...")

        await self.memory_service.add_session_to_memory(session)

        print("✅ Session added to memory!")

    async def do_retrieval_and_something(self):
        
        print("Doing day 4 assignment 2 part 2")
        user_agent = LlmAgent(
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=self.retry_config),
            name="MemoryDemoAgent",
            instruction="Answer user questions in simple words. Use load_memory tool if you need to recall past conversations.",
            tools=[
                load_memory
            ],  # Agent now has access to Memory and can search it whenever it decides to!)
        )

        print("✅ Agent with load_memory tool created.")



    async def run_session(self, runner_instance: Runner, user_queries: list[str] | str, session_id: str = "default"):
        """Helper function to run queries in a session and display responses."""
        print(f"\n### Session: {session_id}")

        # Create or retrieve session
        try:
            session = await self.session_service.create_session(
                app_name=self.APP_NAME, user_id=self.USER_ID, session_id=session_id
            )
        except:
            session = await self.session_service.get_session(
                app_name=self.APP_NAME, user_id=self.USER_ID, session_id=session_id
            )

        # Convert single query to list
        if isinstance(user_queries, str):
            user_queries = [user_queries]

        # Process each query
        for query in user_queries:
            print(f"\nUser > {query}")
            query_content = types.Content(role="user", parts=[types.Part(text=query)])

            # Stream agent response
            async for event in runner_instance.run_async(
                user_id=self.USER_ID, session_id=session.id, new_message=query_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    text = event.content.parts[0].text
                    if text and text != "None":
                        print(f"Model: > {text}")


        print("✅ Memory functions defined.")

