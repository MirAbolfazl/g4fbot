from flask import Flask, request
import g4f
import os
import socket

app = Flask(__name__)
CACHE_FILE = "working_provider_model.txt"

# Models to try in order of preference
preferred_models = [
    "gpt_4_mini",
    "gpt_4",
    "gpt_3_5",
    "deepseek_chat",
    "palm",
    "gemini_pro"
]

# Providers to ignore
ignored_providers = ["ChatGLM", "Chatai"]

# Test a specific model/provider combo
def test_combo(model_name, provider_name, message):
    try:
        model = getattr(g4f.models, model_name)
        provider = getattr(g4f.Provider, provider_name)
        print(f"Testing {model_name} with {provider_name}...")  # Log model and provider
        
        # Check if the provider is DDG (DuckDuckGo) and handle accordingly
        if provider_name == "DDG":
            print("Warning: Using DDG provider, may experience delays.")

        # Test the connection with the server
        socket.gethostbyname("www.google.com")  # Just a basic test to ensure network connectivity

        response = g4f.ChatCompletion.create(
            model=model,
            provider=provider,
            messages=[{"role": "user", "content": message}],
            timeout=30  # Increased timeout to avoid hanging
        )
        
        print(f"Response received: {response}")  # Log response
        return str(response)
    except socket.gaierror as e:
        print(f"Network error: {e}")  # Log network errors
        return "Network error. Please check your internet connection."
    except Exception as e:
        print(f"Error occurred: {e}")  # Log other errors
        return None

# Try all combinations and find the first working one
def find_working_combo(message):
    for model_name in preferred_models:
        for provider_name in g4f.Provider.__all__:
            if provider_name in ignored_providers:
                continue
            print(f"Testing {model_name} with {provider_name}...")
            result = test_combo(model_name, provider_name, message)
            if result:
                with open(CACHE_FILE, "w") as f:
                    f.write(f"{model_name}|{provider_name}")
                return result
    return "No active model/provider combination found."

# Main chat function
def chat(message):
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                model_name, provider_name = f.read().strip().split("|")
                result = test_combo(model_name, provider_name, message)
                if result:
                    return result
        except Exception as e:
            print(f"Error reading cache: {e}")
            pass
    return find_working_combo(message)

# Flask endpoint
@app.route('/chat', methods=['GET'])
def chat_endpoint():
    message = request.args.get("message")
    if not message:
        return "Missing 'message' parameter", 400
    return chat(message)

# Run the app
if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
