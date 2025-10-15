import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file")
    exit()

genai.configure(api_key=api_key)

# List available models
print("🔍 Checking available models...")
try:
    models = genai.list_models()
    for model in models:
        print(f"Model: {model.name}")
        print(f"Supported methods: {model.supported_generation_methods}")
        print("---")
except Exception as e:
    print(f"❌ Error listing models: {e}")

# Test a specific model
print("\n🧪 Testing model...")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello World' in a creative way")
    print(f"✅ Success! Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")