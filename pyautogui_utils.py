import pyautogui

def take_screenshot(filename='screenshot.png'):
    \"\"\"Takes a screenshot of the entire screen and saves it to a file.\"\"\"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

def move_mouse(x, y, duration=1):
    \"\"\"Moves the mouse cursor to the specified coordinates.\"\"\"
    pyautogui.moveTo(x, y, duration=duration)

def click_mouse(x, y, button='left'):
    \"\"\"Clicks the mouse at the specified coordinates with the specified button.\"\"\"
    pyautogui.click(x, y, button=button)

def type_text(text, interval=0.1):
    \"\"\"Types the specified text with a delay between each character.\"\"\"
    pyautogui.typewrite(text, interval=interval)

def press_key(key):
    \"\"\"Presses the specified key.\"\"\"
    pyautogui.press(key)

def find_image(image_path, confidence=0.9):
    \"\"\"Finds an image on the screen and returns its coordinates.\"\"\"
    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    return location