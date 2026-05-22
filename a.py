import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("GEMINI_MODEL"))
print(os.getenv("GEMINI_API_KEY")[:15])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    os.getenv("GEMINI_MODEL")
)

response = model.generate_content("Say hello")

print(response.text)