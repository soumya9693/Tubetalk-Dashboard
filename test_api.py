import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Check if the API key is loaded correctly
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Google API Key not found. Please set it in the .env file.")

# Initialize the Gemini model
# We are using the "gemini-pro" model

llm = ChatGoogleGenerativeAI(model="gemini-pro-latest")
print("Successfully initialized the Gemini model!")
print("---")
print("Sending a test prompt...")

# Send a simple prompt to the model
result = llm.invoke("What is the most popular programming language for AI development and why?")

# Print the model's response
print("---")
print("Model Response:")
print(result.content)