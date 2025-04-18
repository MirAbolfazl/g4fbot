

---

README.md

# GPT4Free Auto-Tester API

This project is a simple Flask-based API that automatically tests multiple GPT models and providers using [gpt4free](https://github.com/xtekky/gpt4free), and selects the fastest working combination.

## Features

- Automatically finds and caches the first working provider/model.
- Skips unsupported or blocked providers like `ChatGLM` and `Chatai`.
- Caches working combo to speed up future requests.
- Easy deployment with auto-install script and `nohup` support.

## API Endpoint

### `GET /chat?message=YOUR_MESSAGE`

**Query Parameter:**

- `message`: (string) The message to send to the chatbot.

**Response:**

- The chatbot's reply as plain text.

## Setup & Run (Automatic)

Use the provided install script to install everything and start the server:

```bash
curl -O https://raw.githubusercontent.com/mirabolfazlir/gp4fbot/main/install_and_run.sh
chmod +x install_and_run.sh
./install_and_run.sh

> This script will:

Download gpt.py from GitHub

Install Python if missing

Install Flask and gpt4free

Launch the Flask app in background via nohup




Manual Installation

# Clone repo
git clone https://github.com/mirabolfazlir/gp4fbot.git
cd gp4fbot

# Install dependencies
pip install flask
pip install git+https://github.com/xtekky/gpt4free.git

# Run the app
python3 gpt.py

File Structure

gpt.py                 # Main Flask app
install_and_run.sh     # Auto-install and background-run script
README.md              # Documentation

License

MIT © Abolfazl Ebrahimi

---
