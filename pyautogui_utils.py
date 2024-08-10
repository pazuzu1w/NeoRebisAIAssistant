import pyautogui
import os
import time
import json
import cv2

def take_screenshot(filename: str, directory: str):
    """Takes a screenshot of the entire screen and saves it to a file."""
    screenshot = pyautogui.screenshot()
    filepath = os.path.join(directory, f"{filename}.png")
    screenshot.save(filepath)

def move_mouse(x, y, duration=1):
    """Moves the mouse cursor to the specified coordinates."""
    pyautogui.moveTo(x, y, duration=duration)

def click_mouse(x, y, button='left'):
    """Clicks the mouse at the specified coordinates with the specified button."""
    pyautogui.click(x, y, button=button)

def press_key(key):
    """Presses the specified key."""
    pyautogui.press(key)

def locate_image(image_path, confidence=0.9):
    """Locates an image on the screen with a specified confidence level."""
    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    if location is not None:
        return pyautogui.center(location)
    else:
        print(f"{image_path} not found on the screen.")
        return None

def click_button(image_path):
    position = locate_image(image_path)
    if position is not None:
        pyautogui.click(position)

def double_click_button(image_path):
    position = locate_image(image_path)
    if position is not None:
        pyautogui.doubleClick(position)

def type_text(image_path, text):
    position = locate_image(image_path)
    if position is not None:
        pyautogui.click(position)
        pyautogui.typewrite(text)

def click_image(image_path, confidence=0.9):
    """Clicks on an image on the screen."""
    location = locate_image(image_path, confidence=confidence)
    if location:
        x, y = pyautogui.center(location)
        pyautogui.click(x, y)
    else:
        print(f"Image '{image_path}' not found on the screen.")

def open_application(program_name: str):
    """Opens an application on the system."""
    try:
        # Press the Windows key
        pyautogui.press('win')
        time.sleep(1)  # Wait for the Start menu to open

        # Type the program name
        pyautogui.write(program_name)
        time.sleep(1)  # Wait for search results

        # Press Enter to open the top result
        pyautogui.press('enter')
        time.sleep(2)  # Wait for the program to start

        return f"Attempted to open {program_name}. Please check if it's running."
    except Exception as e:
        return f"An error occurred while trying to open {program_name}: {str(e)}"

def main_tool_dispatcher(params):
    subtool_name = params.get("subtool")
    subtool_params = params.get("subtool_params", {})

    subtools = {
        "click_button": click_button,
        "double_click_button": double_click_button,
        "type_text": type_text,
        "click_image": click_image,  # Added missing subtool
        "move_mouse": move_mouse,  # Added missing subtool
        "click_mouse": click_mouse,  # Added missing subtool
        "press_key": press_key,  # Added missing subtool
        "open_application": open_application  # Added missing subtool
    }

    subtool = subtools.get(subtool_name)
    if subtool:
        try:
            return subtool(**subtool_params)
        except TypeError as e:
            return {"status": "error", "message": f"Invalid parameters for {subtool_name}: {str(e)}"}
    else:
        return {"status": "error", "message": f"Subtool {subtool_name} not found."}

tools = {
    "main_tool": main_tool_dispatcher,
}

def execute_tool(command_json: str):
    try:
        command = json.loads(command_json)
        tool_name = command.get('tool')
        params = command.get('params', {})

        tool = tools.get(tool_name)
        if tool:
            return tool(params)
        else:
            return {"status": "error", "message": f"Tool {tool_name} not found."}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
