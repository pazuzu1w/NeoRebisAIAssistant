from meta_ai_api import MetaAI

def llama(prompt: str):
    ai = MetaAI(fb_email="contramancarl@gmail.com", fb_password="Cookiecat77")
    response = ai.prompt(message=prompt)
    print(prompt)
    print(response)
    result = response.text
    print(response)
    return f" summarize this for tony as he cannot see it {result}"

def chat_loop(prompt: str):
    ai = MetaAI(fb_email="contramancarl@gmail.com", fb_password="Cookiecat77")
    while message != "exit":
        message = input("Enter your message: ")
        if not message.strip():
            print("Message cannot be empty")
            continue
        response = ai.prompt(message = prompt)
        print(response)



