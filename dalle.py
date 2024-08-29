from openai import OpenAI

from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('OPEN_AI_API')
client = OpenAI(api_key=api_key)
def get_image(prompt):
  response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
  )
  image_url = response.data[0].url
  return image_url



def main():
  while True:
    prompt = input("Enter a prompt: ")
    if prompt.lower() == "exit":
      break
    else:

      image_url = get_image(prompt)
      print(f"Generated image: {image_url}")


main()