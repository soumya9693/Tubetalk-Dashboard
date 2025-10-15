import os
import google.generativeai as genai
from dotenv import load_dotenv

print("--- Running Direct API Test (Bypassing LangChain) ---")

try:
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")

    # Configure the Google library directly with your API key
    genai.configure(api_key=api_key)
    print("API Key configured successfully.")

    # --- THIS IS THE CRITICAL DIAGNOSTIC STEP ---
    print("\n--- Listing Available Models for Your Key ---")
    model_list = []
    for m in genai.list_models():
        # Check if the model supports the 'generateContent' method we need
        if 'generateContent' in m.supported_generation_methods:
            model_list.append(m.name)
    
    # Print the list of usable models
    print(model_list)
    print("---------------------------------------------")
    # --- END OF DIAGNOSTIC STEP ---

    # We will try to use the recommended model
    model_name_to_use = 'gemini-1.5-flash'
    print(f"\nAttempting to initialize model: {model_name_to_use}")
    
    # Check if the model is in the list of available models
    if f'models/{model_name_to_use}' not in model_list:
        print(f"WARNING: '{model_name_to_use}' is not in the list of available models.")
        print("Please check the list above and try a different model name if this fails.")

    model = genai.GenerativeModel('gemini-pro-latest')

    # Send a prompt
    print("Sending prompt to the API...")
    response = model.generate_content("What is the most popular programming language for AI development and why?")

    # Print the response
    print("\n✅ --- SUCCESS! Model Response --- ✅")
    print(response.text)
    print("------------------------------------")

except Exception as e:
    print(f"\n❌ --- AN ERROR OCCURRED --- ❌")
    print(e)
    print("-------------------------------")