import webbrowser
import requests
from bs4 import BeautifulSoup


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


def surf_web(url: str):
    try:
        # Open the webpage
        open_webpage(url)

        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Get the raw HTML
        raw_html = response.text

        # Parse the HTML content
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Extract the title and a brief content summary
        title = soup.title.string if soup.title else "No title found"
        content_summary = ' '.join(soup.stripped_strings)[:500] + "..."  # First 500 characters

        return {
            "success": True,
            "url": url,
            "title": title,
            "content_summary": content_summary,
            "raw_html": raw_html
        }
    except Exception as e:
        print(f"An error occurred while surfing the web: {str(e)}")
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }