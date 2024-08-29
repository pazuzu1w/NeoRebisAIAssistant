import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

# Set up your OpenAI API key
api_key = os.getenv('OPEN_AI_API')

# Ensure the API key is set
if not api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

# Initialize the OpenAI client with the API key
client = AsyncOpenAI(api_key=api_key)

history = [{"role": "system", "content": "You are a helpful assistant."}]

async def chat_loop():
    while True:
        message = input("Enter your message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break

        history.append({"role": "user", "content": message})

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            stream=True,
            temperature=1,
        )
        print("Assistant: ", end="", flush=True)
        full_response = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        print()  # Newline for the next message

        # Add assistant's response to history
        history.append({"role": "assistant", "content": full_response})

        # Limit history to last N messages to manage token count
        #history = history[-10:]  # Keep only the last 10 messages


asyncio.run(chat_loop())