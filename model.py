import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types.safety_types import HarmCategory
import os
from dotenv import load_dotenv
from entityDB import EntityDB as eDB
load_dotenv()
DEFAULT_MODEL = "models/gemini-1.5-pro-latest"




def get_available_models():
    try:
        api_key = os.getenv('API_KEY3')
        if not api_key:
            raise ValueError("API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        return [model.name for model in genai.list_models()]
    except Exception as e:
        print(f"Failed to get model list: {e}")
        return [DEFAULT_MODEL]





def init_model(model_name=DEFAULT_MODEL, system_prompt=""):
    try:
        api_key = os.getenv('API_KEY2')
        if not api_key:
            raise ValueError("API_KEY not found in environment variables")

        genai.configure(api_key=api_key)

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE
        }

        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 5000,
        }

        model = genai.GenerativeModel(
            model_name=model_name,
            tools=[eDB.summon_entity, eDB.add_field, eDB.local_search, eDB.tavily_search, eDB.read_entity, eDB.list_entities, eDB.delete_entity],
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_prompt
        )

        chat = model.start_chat(history=[], enable_automatic_function_calling=True)

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

