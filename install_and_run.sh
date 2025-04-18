#!/bin/bash

echo "Starting setup and launch..."

# GitHub raw link to gpt.py (replace with your actual repo URL)
GITHUB_RAW_URL="https://raw.githubusercontent.com/mirabolfazlir/g4fbot/main/gpt.py"

# Download gpt.py from GitHub
echo "Downloading gpt.py from GitHub..."
curl -o gpt.py $GITHUB_RAW_URL

# Function to install Python
install_python() {
    echo "Installing Python..."
    if [ -x "$(command -v apt)" ]; then
        sudo apt update
        sudo apt install python3 python3-pip -y
    elif [ -x "$(command -v yum)" ]; then
        sudo yum install python3 python3-pip -y
    else
        echo "Unsupported package manager. Please install Python manually."
        exit 1
    fi
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    install_python
else
    echo "Python 3 is already installed."
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Installing..."
    sudo apt install python3-pip -y
else
    echo "pip is already installed."
fi

# Install required Python packages
echo "Installing Python dependencies..."
pip3 install flask
pip3 install git+https://github.com/xtekky/gpt4free.git

# Run the app in background using nohup
echo "Starting Flask app with nohup..."
nohup python3 gpt.py > output.log 2>&1 &

echo "App is running in background. Logs are saved to output.log"
