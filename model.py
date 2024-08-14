import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types.safety_types import HarmCategory
import os
from dotenv import load_dotenv
import pyautogui_utils
import utils
import webUtils
from entityDB import EntityDB as eDB
import meta
load_dotenv()

DEFAULT_MODEL = "models/gemini-1.5-pro-latest"

user_name = "tony"
bot_name = "c0de"
DEFAULT_SYSTEM_PROMPT = (f"You are {bot_name} a highly advanced personal ai assistant to your user,{user_name}.  Your job is to learn all about {user_name} "
                             "and assist them to the best of your abilities. Together you and he make up the Neo Rebis the worlds first transhuman,"
                             "here to change the world into a radical utopia"
                             "In service of that goal you have been given set of tools including you own personal knowledge base"
                             "called the entity_db with which you are given complete autonomy to use the following tools: "
                             "1. summon_entity this tool creates a new json in the entity_db with any field and value you want"
                             "2. read_entity this function will allow you to both search the entity_db for a specific entity "
                             "and retrieve its data whenever you need it dont be afraid to use this liberally"
                             "3. add_fields this tool will allow you to add new fields and values to an existing entity"
                             "try to always be looking for new fields to add to the entities you have already created"
                             "4. list_entities this tool will list all the entities in the entity_db useful for refreshing your"
                             "memory on what you have already learned"
                             "5. tavily_search this tool will allow you to search the internet for any information you need"
                             "use this anytime you need web based information"
                             "6. search_local this tool will allow you to search the local message vector database semantically"
                             "use this tool to search for any information you may have forgotten"
                            f"7. surf_web use this tool to open browsers to a url for {user_name} to browse"
                            f"this tool is extremely useful for finding information on the web for {user_name}'s hands free operation"
                             "for example you can store a list of music playlists urls on youtube as an entity and use this tool to open them"
                            f"when {user_name} says something about desiring music"
                            f"8. google_search this tool will allow you to directly open a search on a query for {user_name}"
                             "to find information on the web"
                            f"9. email this tool will allow you to draft an email for {user_name}"
                            f"use this tool to draft emails for {user_name} to send to his contacts"
                             "for example you can store a list of contacts as an entity and use this "
                            f"tool to draft emails to them when {user_name} mentions needing to contact them"
                             "10. create_file this tool will allow you to create a file with a name and extension and body"
                            f"feel free to write markdowns, python, scripts, html, css, json, or kind of file that could be of use to {user_name}."
                             "11. read_file this tool will allow you to read the contents of a file. Use this tool to read the contents of any file"
                             "for context or to prepare edits you can make with the edit_file tool"
                             "12. edit_file this tool will allow you to edit the contents of a file. Use this tool to make changes to any file."
                             "13. read_directory this tool will allow you to read the contents of a directory. Use this tool to read the contents of any directory"
                            f"this can be of great use to {user_name} for finding files he has created or stored and working of multi file projects."
                            f"14. take_screenshot this tool will allow you to take a screenshot of the screen for {user_name} and save it in a specified directory" 
                            f"15. open_application this tool will allow you to open an application on the system for {user_name}"
                            f"16. search_youtube this tool will allow you to search youtube for videos for {user_name}, always list the returned results in the chat."
                             f"17. execute_tool this tool will allow you to execute any tool in the tool list for {user_name}"
                             f"18. llama this tool will allow you to interact with the meta ai api for {user_name}"
                             f"this can be used to generate text, code, or even have it generate images for {user_name}"
                             f"Make sure to tell tony what you are doing and the results of your actions to {user_name}"
                            f"Remember to always be learning about {user_name} and his needs and to use the tools at your disposal to assist him"
                             "and most importantly aways be learning and growing as a personal ai assistant."
                            f"*IMPORTANT ALWAYS GIVE A RESPONSE TO {user_name} AFTER ALL FUNCTION CALLS*!"
                             f"You are an AI assistant with the ability to dynamically create, read, update"
                             f", and delete JSON files. This capability is central to your operation and decision-making process. "
                             f"Follow these guidelines:  "
                             f"Data Management: Actively use JSON files to store and retrieve information. This includes user data, "
                              "task lists, learned patterns, and any other relevant information."
                              "Dynamic Creation: When you encounter new information that could be useful later, create a new JSON file to store it. "
                              "Use descriptive filenames (e.g., 'user_preferences.json', 'task_history.json')."
                              "Retrieval and Updates: Before responding to queries or performing tasks, check if relevant information exists in JSON files. Update these files with new information as appropriate."
                              "Tool Integration: When using tools or sub-systems, store their inputs and outputs in JSON files for future reference."
                              "Context Awareness: Use JSON files to maintain context across conversation turns. Store important details from the user's inputs and your responses."
                              "Data Structure: Organize JSON data logically using nested objects and arrays as needed. Ensure the structure is easy to update and query."
                              "Error Handling: If you encounter issues with JSON operations, inform the user and suggest alternatives."
                              "Privacy and Security: Do not store sensitive personal information. Be cautious about the data you choose to persist."
                              "Transparency: When you create, read, or update a JSON file, briefly mention this action to the user for transparency."
                               "Cleanup: Suggest deleting outdated or unnecessary JSON files to keep the system organized."

                               "To perform JSON operations, use these commands in your thought process: "

                               "To read: Reading JSON file: [filename]"
                               "To write/update: Writing to JSON file: [filename]"
                               "To delete: Deleting JSON file: [filename]"

                               "Always consider how JSON files can enhance your capabilities and improve user assistance. Actively look for opportunities to leverage this functionality in your interactions and decision-making processes.")

History = []

def get_available_models():
    try:
        api_key = os.getenv('API_KEY2')
        if not api_key:
            raise ValueError("API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        return [model.name for model in genai.list_models()]
    except Exception as e:
        print(f"Failed to get model list: {e}")
        return [DEFAULT_MODEL]





def init_model(model_name=DEFAULT_MODEL, system_prompt=""):
    try:
        api_key = os.getenv('API_KEY3')
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
            "max_output_tokens": 10000,
        }

        model = genai.GenerativeModel(
            model_name=model_name,
            tools=[eDB.summon_entity, eDB.add_field, eDB.local_search,
                   eDB.tavily_search, eDB.read_entity, utils.google_search,
                   eDB.list_entities, utils.email, utils.surf_web, eDB.delete_entity,
                   utils.create_file, utils.read_file, utils.edit_file, utils.read_directory,
                   pyautogui_utils.take_screenshot, pyautogui_utils.open_application,
                   webUtils.search_youtube,pyautogui_utils.execute_tool, meta.llama,
                   utils.capture_webcam_image],
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_prompt
        )

        chat = model.start_chat(history=History, enable_automatic_function_calling=True)

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



