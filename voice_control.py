import speech_recognition as sr
import pyttsx3
import time
import threading
import openai
import config  # Holds your OpenAI API key

import pvporcupine
import pyaudio
import struct

openai.api_key = config.OPENAI_API_KEY

###############################
#     GPT-4 Interpretation    #
###############################
def interpret_command(command):
    """Uses GPT-4 to analyze the command and return an action response."""
    prompt = f"""
    You are an AI assistant that converts user voice commands into actionable browser automation tasks.
    The user might ask you to open websites, search for information, or perform other browser-based tasks.

    Examples:
    - "Open Gmail" → "open https://mail.google.com"
    - "Search for Python tutorials" → "search Python tutorials"
    - "Check the weather" → "open https://weather.com"
    - "Play a song on Spotify" → "open https://open.spotify.com"
    - "Open cocomelon in YouTube" → "open https://www.youtube.com/results?search_query=cocomelon"   <== ADD THIS
    - "Click on second video" → "play_video 2"     <== NEW EXAMPLE
    - "Play the third video" → "play_video 3"
    - "Pause the video" → "pause_video"
    - "Search crossbody bags on Amazon" → "search_amazon crossbody bags"
    - "Search for Python tutorials" → "search Python tutorials"

    User Command: "{command}"
    AI Response:
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5  
    )

    result = response.choices[0].message.content.strip()
    print(f"🔍 GPT-4 Response: {result}")
    return result

###############################
#     Text-to-Speech (TTS)    #
###############################
engine = pyttsx3.init()
is_speaking = False




def speak(text):
    """Convert text to speech while preventing overlap."""
    global is_speaking
    if is_speaking:
        print("⚠️ Already speaking. Skipping duplicate speech request.")
        return

    is_speaking = True
    def _speak():
        global is_speaking
        engine.say(text)
        try:
            engine.runAndWait()
        except RuntimeError:
            print("⚠️ Speech engine error.")
        time.sleep(0.5)
        is_speaking = False

    threading.Thread(target=_speak, daemon=True).start()

###############################
#      Speech Recognition     #
###############################
def listen():
    """Use the microphone to listen for a command via SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"Recognized: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
            return None
        except sr.RequestError:
            print("Error: Could not request results. Check your internet connection.")
            return None
        except sr.WaitTimeoutError:
            print("Error: Listening timed out while waiting for phrase to start.")
            return None

###############################
#  Re-Initialize Porcupine    #
###############################
def create_porcupine():
    """Create a fresh Porcupine instance each time for repeated detection."""
    return pvporcupine.create(
        access_key=config.PORCUPINE_ACCESS_KEY,
        keywords=["computer"]
    )

def detect_wake_word():
    """
    Creates a fresh Porcupine + stream.
    Returns True after hearing the wake word 'computer' ONCE.
    Then cleans up the stream & Porcupine so we can do it again later.
    """
    print("🔹 Creating new Porcupine instance for wake word detection.")
    porcupine = create_porcupine()

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    stream.start_stream()

    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("👂 Wake Word Detected!")
            # Clean up for next cycle
            stream.stop_stream()
            stream.close()
            pa.terminate()
            porcupine.delete()
            return True

