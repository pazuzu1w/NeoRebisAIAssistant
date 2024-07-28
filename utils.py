import webbrowser
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup
import os

from httpx._urlparse import urlparse
import pyaudio
import speech_recognition as sr

import entityDB
from entityDB import EntityDB


def send_email(email, subject, body):
    webbrowser.open(f"mailto:{email}?subject={subject}&body={body}")
    print(f"Sending email to {email} with subject: {subject} and body: {body}")
    return True


def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    print(f"Searching the web for: {query}")
    return True


def google_search(query: str):
    return search_web(query)


def email(email: str, subject: str, body: str):
    return send_email(email, subject, body)


def open_webpage(url):
    webbrowser.open(url)
    print("Webpage opened")


@staticmethod
def surf_web(url: str) -> Dict[str, Any]:
    print(f"Surfing web: {url}")
    try:
        html_folder = "html"
        open_webpage(url)
        EntityDB.read_entity("Websites")
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title and a brief content summary
        title = soup.title.string if soup.title else "No title found"
        content_summary = ' '.join(soup.stripped_strings)[:1000] + "..."  # First 1000 characters

        # Prepare the webpage data
        webpage_data = {
            "title": title,
            "content_summary": content_summary,

        }
        print(f"Webpage data: {webpage_data}")
        # Add the webpage data to the 'websites' entity
        EntityDB.add_field("Websites", url, webpage_data)
        if not os.path.exists("html"):
            os.makedirs("html")

        parsed_url = urlparse(url)
        filename = f"{parsed_url.netloc}{parsed_url.path.replace('/', '_')}.html"
        if not filename.endswith('.html'):
            filename += '.html'
        filepath = os.path.join(html_folder, filename)

        # Write the raw HTML to a file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)






        return {
            "status": "success",
            "url": url,
            "title": title,
            "content_summary": content_summary,
            "message": f"Webpage data stored in 'websites' entity"
        }
    except Exception as e:
        print(f"An error occurred while surfing the web: {str(e)}")
        return {
            "status": "error",
            "url": url,
            "error": str(e)
        }


@staticmethod
def get_webpage_data(url: str) -> Dict[str, Any]:
    websites_data = EntityDB.read_entity("Websites")['data']
    if url in websites_data:
        return {
            "status": "success",
            "data": websites_data[url]
        }
    else:
        return {
            "status": "error",
            "message": f"No data found for URL: {url}"
        }



def create_file(file_path: str, file_content: str):
    """Creates a text file at the specified path, creating directories if needed.

    Args:
        file_path (str): The full path to the file, including filename and extension.
        file_content (str): The content to write to the file.
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")

    if not os.path.exists(file_path):
        formatted_code = file_content.replace('\\n', '\n')
        # Ensure the content is written as UTF-8 encoded text
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(formatted_code)
        print(f"File '{file_path}' created.")
        return f"File '{file_path}' created."
    else:
        print(f"File '{file_path}' already exists.")
        return f"File '{file_path}' already exists."


def read_file(file_path: str):
  """Reads any file on the disk.

  Args:
        file_path (str): The full path to the file.
  """
  if os.path.exists(file_path):
    with open(file_path, 'r') as file:
      print(f"Reading file '{file_path}'")
      return file.read()
  else:
    print(f"File '{file_path}' not found.")
    return f"File '{file_path}' not found."


def edit_file(name: str, extension: str, body: str):
    """Edits a text file.

    Args:
        name: The name of the file.
        extension: The file extension.
        body: The content to append to the file.
    """
    formatted_code = body.replace('\\n', '\n ')
    if os.path.exists(f"{name}.{extension}"):
        with open(f"{name}.{extension}", "a") as file:
            file.write(formatted_code)
        print(f"File '{name}.{extension}' edited.")
        return f"File '{name}.{extension}' edited."
    else:
        print(f"File '{name}.{extension}' not found.")
        return f"File '{name}.{extension}' not found."


def read_directory(name: str):
    """Reads the contents of the 'files' directory."""
    if os.path.exists(f"{name}"):
        files = os.listdir(f"{name}")
        print(f"Files in 'files' directory: {files}")
        return files
    else:
        print("Directory 'files' not found.")
        return "Directory 'files' not found."


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`."""
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for commands...")
        audio = recognizer.listen(source)

    response = {"success": True, "error": None, "transcription": None}

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response


def check_for_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        print("Say something!")
        result = recognize_speech_from_mic(recognizer, microphone)

        if result["transcription"]:
            print(f"You said: {result['transcription']}")
        if not result["success"]:
            print("I didn't catch that. What did you say?\n")

        if result["error"]:
            print(f"ERROR: {result['error']}")

        # Add your command processing logic here
        # Example:
        if result["transcription"]:
            command = result["transcription"].lower()
            if "exit" in command:
                print("Exiting...")
                break
            elif "hello" in command:
                print("Hello to you too!")
            # Add more commands as needed
