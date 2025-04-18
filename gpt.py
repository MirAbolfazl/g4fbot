from flask import Flask, request
import g4f
import os

app = Flask(__name__)
CACHE_FILE = "working_provider_model.txt"

preferred_models = [
    "gpt_4_mini",
    "gpt_4",
    "gpt_3_5",
    "deepseek_chat",
    "palm",
    "gemini_pro"
]

def test_combo(model_name, provider_name, message):
    try:
        model = getattr(g4f.models, model_name)
        provider = getattr(g4f.Provider, provider_name)
        response = g4f.ChatCompletion.create(
            model=model,
            provider=provider,
            messages=[{"role": "user", "content": message}],
            timeout=10
        )
        return str(response)
    except Exception:
        return None

def find_working_combo(message):
    for model_name in preferred_models:
        for provider_name in g4f.Provider.__all__:
            if any(x in provider_name.lower() for x in ["chatglm", "chatai"]):
                continue
            print(f"در حال تست {model_name} با {provider_name}")
            result = test_combo(model_name, provider_name, message)
            if result:
                with open(CACHE_FILE, "w") as f:
                    f.write(f"{model_name}|{provider_name}")
                return result
    return "هیچ مدل و provider فعالی پیدا نشد."

def chat(message):
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                model_name, provider_name = f.read().strip().split("|")
                result = test_combo(model_name, provider_name, message)
                if result:
                    return result
        except:
            pass
    return find_working_combo(message)

@app.route('/chat', methods=['GET'])
def chat_endpoint():
    message = request.args.get("message")
    if not message:
        return "پارامتر message رو وارد کن", 400
    return chat(message)

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
