import tkinter as tk
from tkinter import scrolledtext, messagebox as msg, simpledialog
import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types.safety_types import HarmCategory
import os
import datetime
import time
import queue
import threading
import pyttsx3
from dotenv import load_dotenv








def check_search_results():
    global root
    """Checks for search results and displays them."""
    try:
        results = search_results_queue.get_nowait()
        display_message(f"Search results:\n\n{results}", "system")

        # Send the search results back to the AI as a message
        response = chat.send_message(f"RETRIEVE_MEMORY: {results}")
        display_message(response.text, "bot")

    except queue.Empty:
        pass
        # Schedule the check to run again after a short delay
    root.after(500, check_search_results)


def handle_bot_search_command(bot_response):
    # Split the response by spaces and find the part starting with "!search"
    parts = bot_response.split()
    search_index = next((i for i, part in enumerate(parts) if part.lower() == "!search"), None)

    if search_index is not None and search_index + 1 < len(parts):
        keyword = " ".join(parts[search_index + 1:])
        if keyword:
            threading.Thread(target=perform_search, args=(keyword,)).start()

    else:
        display_message("Invalid search command format.", "system")




# --- GET SYSTEM PROMPT ---
def get_sys_prompt():
    new_prompt = simpledialog.askstring("!sysprompt", "Enter new system instruction:")
    if new_prompt:
        # TODO: Send new_prompt to gemini_api module to update model's system instructions
        print("New System Prompt:", new_prompt)
        pass  # Placeholder for now




def handle_search_command(input_text):
    keyword = input_text[8:].strip()
    if keyword:
        results = search_logs(keyword)
        formatted_results = process_search_results(results)

        # Display the search results
        display_message(f"Search results for '{keyword}':\n\n{formatted_results}", "system")

        # Send the search results to the AI for commentary
        response = chat.send_message(
            f"I've searched the logs for '{keyword}'. Here are the results:\n\n{formatted_results}\nCan you provide any insights or analysis based on these results?")
        display_message(response.text, "bot")
    else:
        display_message("No search keyword provided.", "system")
