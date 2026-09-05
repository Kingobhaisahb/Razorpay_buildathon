import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Explain in one sentence what an AI growth agent does."
)

print("\n==============================")
print("GEMINI TEST RESULT")
print("==============================")
print(interaction.output_text)