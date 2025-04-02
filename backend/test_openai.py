import openai
import os
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR:  OPENAI_API_KEY not found in .env file.")
    exit(1)
else:
    print("API Key:", api_key)

# Initialize OpenAI Client (New format for openai v1.0.0+)
client = openai.OpenAI(api_key=api_key)

# Fetch available models
# try:
#     models = client.models.list()
#     print("\n Available OpenAI Models:")
#     for model in models:
#         print("-", model.id)

# Test OpenAI API connection
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello, how are you?"}]
    )

    print("\n OpenAI API connection successful.")
    print("Response: ", response["choices"][0]["message"]["content"])

except Exception as e:
    print("\n OpenAI API connection failed.")
    print("Error: ", str(e))