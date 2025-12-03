from memory import Memory
import os
import asyncio


async def main():
    """Main entry point of the application."""

    # Accessing an environment variable
    api_key = os.environ.get('GEMINI_ANOTHER_KEY')

    # You can also access it directly, but it will raise a KeyError if not found
    # api_key = os.environ['MY_API_KEY']

    if api_key:
        print(f"API Key: {api_key}")
        # The google-adk library requires GOOGLE_API_KEY environment variable
        os.environ["GOOGLE_API_KEY"] = api_key
    else:
        print("MY_API_KEY environment variable not set.")

    agent = Memory(api_key)

    await agent.do_something()


if __name__ == "__main__":
    asyncio.run(main())

