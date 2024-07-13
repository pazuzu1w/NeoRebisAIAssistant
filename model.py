import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types.safety_types import HarmCategory
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "models/gemini-1.5-pro-latest"

def get_available_models():
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            raise ValueError("API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        return [model.name for model in genai.list_models()]
    except Exception as e:
        print(f"Failed to get model list: {e}")
        return [DEFAULT_MODEL]


def init_model(model_name=DEFAULT_MODEL, system_prompt=None):
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            raise ValueError("API_KEY not found in environment variables")

        genai.configure(api_key=api_key)

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE
        }

        model = genai.GenerativeModel(
            model_name=model_name,
            safety_settings=safety_settings,
        )

        chat = model.start_chat(history=[])
        if system_prompt:
            chat.send_message(system_prompt)

        print(f"Model '{model_name}' initialized successfully! 🔥")
        return chat

    except Exception as e:
        print(f"Model initialization failed: {e}")
        return None


def send_message_async(chat, message):
    try:
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        print(f"Failed to send message: {e}")
        return None