# Voice-Controlled Browser Automation

A simple Python app that uses voice commands to control a web browser using GPT-4, Selenium, and Porcupine wake word detection.

## Features
- 🔊 Wake word activation ("Computer")
- 🗣️ Speech recognition with OpenAI's GPT-4
- 🌐 Automate browser actions (search, open websites, play/pause videos)
- 🖥️ Real-time GUI feedback

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/MominaAli07/Browser-Automation-with-LLM.git
cd Browser-Automation-with-LLM
```

### 2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API keys
Create a file named `config.py` in your project folder and add:
```python
OPENAI_API_KEY = "your-openai-api-key"
PORCUPINE_ACCESS_KEY = "your-porcupine-access-key"
```

### How to get your PORCUPINE_ACCESS_KEY:
- Sign up at [Picovoice Console](https://console.picovoice.ai/)
- Once signed in, your access key is available under your account dashboard.

### 5. Run the app
```bash
python main.py
```

## Usage
- Say **"Computer"**, then give a command:
  - **"Open YouTube"**
  - **"Search crossbody bags below $50 on Amazon"**
  - **"Play video two"** *(on YouTube search results)*  
  - **"Pause video"**

## Project Structure
- `config.py`: Stores API keys.
- `voice_control.py`: Handles wake word detection and voice recognition.
- `browser_control.py`: Automates browser tasks via Selenium.
- `gui.py`: GUI built using Tkinter, showing logs and statuses.
- `main.py`: Starts the application by loading GUI.

## Future Enhancements
- Improved context-awareness and memory.
- Dynamic web page analysis.
- Better error handling and user feedback.

