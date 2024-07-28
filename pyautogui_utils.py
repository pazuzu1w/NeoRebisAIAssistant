import pyautogui
import os
import time


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

def type_text(text, interval=0.1):
    """Types the specified text with a delay between each character."""
    pyautogui.typewrite(text, interval=interval)

def press_key(key):
    """Presses the specified key."""
    pyautogui.press(key)

def find_image(image_path, confidence=0.9):
    """Finds an image on the screen and returns its coordinates."""
    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    return location

def click_image(image_path, confidence=0.9):
    """Clicks on an image on the screen
    """
    location = find_image(image_path, confidence=confidence)
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
