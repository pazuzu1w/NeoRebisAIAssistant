import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

import time
import os

def search_youtube(query: str, num_results: int = 5):
    # Set up the Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--detach")  # Ensure the browser doesn't close after the function ends
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation control

    # Initialize the Chrome webdriver
    driver = webdriver.Chrome(options=chrome_options)

    results = []

    try:
        # Open YouTube
        driver.get("https://www.youtube.com")

        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search_query")))

        # Type the query into the search bar
        search_bar.send_keys(query)

        # Press Enter to search
        search_bar.send_keys(Keys.RETURN)

        # Wait for the search results to load
        time.sleep(5)
        search_bar.submit()

        # Find the first video link
        video_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, "video-title")))

        for video in video_elements[:num_results]:
            title = video.get_attribute('title')
            url = video.get_attribute('href')
            results.append({'title': title, 'url': url})

    finally:
        print(results)
        # Close the browser
        driver.quit()

    return f"here are the results the user requested: {results}, now print them out in the chat", results


