import re
from flask import Flask, request
import g4f
import os
import time

app = Flask(__name__)
CACHE_FILE = "working_provider_model.txt"
FAST_RESPONSE_THRESHOLD = 1  # seconds

MAX_TRIES = 1  

preferred_models = [
    "gpt_4",
    "gemini_pro",
    "gpt_4_mini",
    "gpt_3_5",
    "palm",
]

ignored_providers = ["ChatGLM", "Chatai", "Dog", "ImageLabs"]

# Function to check if the text contains a link
def contains_link(text):
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return re.search(url_pattern, text) is not None

def test_combo(model_name, provider_name, messages):
    try:
        model = getattr(g4f.models, model_name)
        provider = getattr(g4f.Provider, provider_name)

        responses = []
        for msg in messages:
            if contains_link(msg):
                print(f"Skipping message with link: {msg}")
                continue  # Skip messages containing links

            start_time = time.time()
            response = g4f.ChatCompletion.create(
                model=model,
                provider=provider,
                messages=[{"role": "user", "content": msg}],
                timeout=10
            )
            elapsed = time.time() - start_time

            # Skip if response is too slow
            if elapsed > 5:
                print(f"Skipping {provider_name} with {model_name} due to response timeout.")
                return None

            response_str = str(response).strip()

            if contains_link(response_str):
                print(f"Skipping {provider_name} with {model_name} due to response containing a link.")
                return None

            responses.append(response_str)

        print(f"Testing {provider_name} with {model_name}")
        print(f"Messages: {messages}")
        print(f"Responses: {responses}")

        # If all responses are the same, it's suspicious
        if all(responses[0] == r for r in responses):
            print(f"[SIMILAR RESPONSE] {provider_name} with {model_name} -> All responses are the same.")
            return None

        return responses[0]  # Return the first valid response

    except Exception as e:
        print(f"[ERROR] {provider_name} with {model_name} -> {str(e)}")
        return None

def find_working_combo(messages):
    for model_name in preferred_models:
        for provider_name in g4f.Provider.__all__:
            if provider_name in ignored_providers:
                continue
            print(f"Trying {model_name} with {provider_name}...")
            result = test_combo(model_name, provider_name, messages)
            if result:
                with open(CACHE_FILE, "w") as f:
                    f.write(f"{model_name}|{provider_name}")
                return result
    return "No active model/provider combination found."

def chat(message):
    messages = ["Hello", "How Are You", "Good Bye"]
    messages2 = [message]
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                model_name, provider_name = f.read().strip().split("|")
                print(f"Testing cached combo: {model_name} | {provider_name}")
                result = test_combo(model_name, provider_name, messages2)
                if result:
                    return result
                else:
                    os.remove(CACHE_FILE)
        except Exception as e:
            print(f"[ERROR] Failed to read cache: {str(e)}")
            pass
    return find_working_combo(messages)

@app.route('/chat', methods=['GET'])
def chat_endpoint():
    message = request.args.get("message")
    if not message:
        return "Missing 'message' parameter", 400
    result = chat(message)
    if isinstance(result, str) and result.startswith("No active model"):
        return result, 500
    return result

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
