import webbrowser
def send_email(email, subject, body):
    webbrowser.open(f"mailto:{email}?subject={subject}&body={body}")
    print(f"Sending email to {email} with subject: {subject} and body: {body}")
    return True
def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    print(f"Searching the web for: {query}")
    return True

def google_search(query: str):
    search_web(query)

def email(email: str, subject: str, body: str):
    send_email(email, subject, body)
def open_webpage(url):
    webbrowser.open(url)
    print("webpage opened")


def surf_web(url: str):

    open_webpage(url)