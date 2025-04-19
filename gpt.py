from flask import Flask, request
import g4f
import os
import time

app = Flask(__name__)
CACHE_FILE = "working_provider_model.txt"
FAST_RESPONSE_THRESHOLD = 1  # seconds
MAX_TRIES = 3  # Number of times to test each combo

# Preferred models to test (in order)
preferred_models = [
    "gpt_4_mini",
    "gpt_4",
    "gpt_3_5",
    "deepseek_chat",
    "palm",
    "gemini_pro"
]

# Providers to ignore completely
ignored_providers = ["ChatGLM", "Chatai"]

# Test a given model and provider combination
def test_combo(model_name, provider_name, message):
    responses = []
    fast_responses = 0

    for _ in range(MAX_TRIES):
        try:
            model = getattr(g4f.models, model_name)
            provider = getattr(g4f.Provider, provider_name)

            start_time = time.time()
            response = g4f.ChatCompletion.create(
                model=model,
                provider=provider,
                messages=[{"role": "user", "content": message}],
                timeout=10
            )
            elapsed = time.time() - start_time

            response_str = str(response).strip()
            responses.append(response_str)

            # Count if the response is too fast (possibly fake)
            if elapsed < FAST_RESPONSE_THRESHOLD:
                fast_responses += 1
            else:
                # If at least one legit response, accept it
                return response_str

        except Exception:
            continue

    # All responses were fast AND identical → likely blocked or fake
    if fast_responses == MAX_TRIES and all(r == responses[0] for r in responses):
        print(f"[BLOCKED] {provider_name} with {model_name} -> {responses[0]}")
        return None

    # All responses were identical even if slow → likely fake or error
    if all(r == responses[0] for r in responses):
        print(f"[FAKE?] {provider_name} with {model_name} -> Same response every time.")
        return None

    return None

# Try all model/provider combinations until one works
def find_working_combo(message):
    for model_name in preferred_models:
        for provider_name in g4f.Provider.__all__:
            if provider_name in ignored_providers:
                continue
            print(f"Trying {model_name} with {provider_name}...")
            result = test_combo(model_name, provider_name, message)
            if result:
                # Save the working combo to cache
                with open(CACHE_FILE, "w") as f:
                    f.write(f"{model_name}|{provider_name}")
                return result
    return "No active model/provider combination found."

# Main chat handler
def chat(message):
    # Try cached model/provider first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                model_name, provider_name = f.read().strip().split("|")
                print(f"Testing cached combo: {model_name} | {provider_name}")
                result = test_combo(model_name, provider_name, message)
                if result:
                    return result
                else:
                    # If failed, remove the cache and re-test all
                    os.remove(CACHE_FILE)
        except:
            pass
    # Find a new working combo if cache failed
    return find_working_combo(message)

# Flask API endpoint
@app.route('/chat', methods=['GET'])
def chat_endpoint():
    message = request.args.get("message")
    if not message:
        return "Missing 'message' parameter", 400
    return chat(message)

# Start the server
if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
