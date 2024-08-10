from meta_ai_api import MetaAI

def llama(prompt: str):

    running = True

    while running:

        if prompt == "quit":
            running = False
            break
        else:
            ai = MetaAI(fb_email="contramancarl@gmail.com", fb_password="Cookiecat77")
            response = ai.prompt(message=prompt)
            print(prompt)
            print (response)
            result = response.text
            print(response)
            return f" summarize this for tony and list any links it may contain {result}"