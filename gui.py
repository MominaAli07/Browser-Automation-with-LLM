import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from urllib.parse import urlparse
import re
from browser_control import get_driver
# Import the re-initialized approach
from voice_control import detect_wake_word, listen, interpret_command

from browser_control import search_amazon, search_amazon_price_filter

########################
#  Global Variables
########################
driver = None  
listening_active = True  # Controls the main loop

########################
#  Tkinter GUI Setup
########################
root = tk.Tk()
root.title("Voice-Controlled Browser")
root.geometry("500x350")

log_display = scrolledtext.ScrolledText(root, width=50, height=10)
log_display.pack(pady=10)

def update_log(message):
    """Append messages to the log display."""
    log_display.insert(tk.END, message + "\n")
    log_display.yview(tk.END)  # auto-scroll



def parse_price_filter(command):
    """
    Looks for patterns like 'below $50' or 'under $30'
    Returns an integer price (e.g., 50) if found, otherwise None.
    """
    pattern = r"(?:below|under)\s*\$?(\d+)"
    match = re.search(pattern, command)
    if match:
        return int(match.group(1))  # e.g. "50" -> 50
    return None



###############################
#   Wake Word + Listen Loop
###############################
def listen_thread():
    global driver, listening_active
    while listening_active:
        update_log("🟢 Waiting for wake word... (Say 'Computer')")
        
        # 1) Create a fresh Porcupine, detect 'computer' once
        if detect_wake_word():
            update_log("✅ Wake word detected! Now speak your command...")

            # 2) Listen for the actual command
            command = listen()
            if command is None:
                update_log("❌ No command detected. Please try again.")
            else:
                update_log(f"🎤 Recognized Command: {command}")

                # 3) GPT-4 interpretation
                action = interpret_command(command).strip('"').strip()
                update_log(f"🔍 AI Interpretation: {action}")

                # 4) Browser if needed
                if driver is None:
                    update_log("🌐 Opening browser...")
                    driver = get_driver()

                # 5) Perform the interpreted action
                if action.startswith("open "):
                    url = action.replace("open ", "").strip()
                    if not url.startswith("http"):
                        url = "https://" + url
                    update_log(f"🌍 Opening {url}...")
                    driver.get(url)
                # elif action.startswith("search "):
                #     query = action.replace("search ", "").strip()
                #     search_url = f"https://www.google.com/search?q={query}"
                #     update_log(f"🔎 Searching Google for: {query}")
                #     driver.get(search_url)
                    
                # elif action.startswith("search "):
                #     query = action.replace("search ", "").strip()
                #     domain = urlparse(driver.current_url).netloc.lower()
                #     if "amazon" in domain:
                #         update_log(f"🔎 Searching Amazon for: {query}")
                #         search_amazon(driver, query)
                #     else:
                #         update_log(f"🔎 Searching Google for: {query}")
                #         driver.get(f"https://www.google.com/search?q={query}")

                # elif action.startswith("search_amazon "):
                #     query = action.replace("search_amazon ", "").strip()
                #     update_log(f"🔎 Searching Amazon for: {query}")
                #     search_amazon(driver, query)
                    

                elif action.startswith("search "):
                    query = action.replace("search ", "").strip()
                    domain = urlparse(driver.current_url).netloc.lower()

                    # 1) Check if the user said "below $X" or "under $X"
                    max_price = parse_price_filter(command)  # e.g. 50
                    if max_price and "amazon" in domain:
                        # The user is on Amazon, and we found a "below $X" phrase
                        item_only = re.sub(r"(?:below|under)\s*\$\d+", "", query, flags=re.IGNORECASE).strip()
                        # e.g. "crossbody bags below $50" -> "crossbody bags"
                        update_log(f"🔎 Searching Amazon for: {item_only} under ${max_price}")
                        search_amazon_price_filter(driver, item_only, max_price)

                    elif "amazon" in domain:
                        # Normal Amazon search (no price filter)
                        update_log(f"🔎 Searching Amazon for: {query}")
                        search_amazon(driver, query)
                    else:
                        # Fallback to Google
                        update_log(f"🔎 Searching Google for: {query}")
                        driver.get(f"https://www.google.com/search?q={query}")

                elif action.startswith("search_amazon "):
                    query = action.replace("search_amazon ", "").strip()

                    # 2) If GPT-4 specifically said "search_amazon"
                    max_price = parse_price_filter(query)
                    if max_price:
                        # We found 'below $X' in the user query
                        item_only = re.sub(r"(?:below|under)\s*\$\d+", "", query, flags=re.IGNORECASE).strip()
                        update_log(f"🔎 Searching Amazon for: {item_only} under ${max_price}")
                        search_amazon_price_filter(driver, item_only, max_price)
                    else:
                        # Normal Amazon search
                        update_log(f"🔎 Searching Amazon for: {query}")
                        search_amazon(driver, query)



                elif action.startswith("play_video "):
                    index_str = action.replace("play_video", "").strip()  # e.g. "3"
                    try:
                        video_index = int(index_str)
                    except ValueError:
                        video_index = 1
                    update_log(f"🎬 Playing video at index: {video_index}")

                    # call the `handle_play_video` from browser_control.py
                    from browser_control import handle_play_video
                    handle_play_video({"video_index": video_index}, driver)   
                elif action.startswith("pause_video"):
                    from browser_control import handle_pause_video
                    # If needed, you can pass parameters, but we likely have none
                    update_log("⏸ Pausing the current video...")
                    handle_pause_video({}, driver)
                else:
                    fallback_query = action
                    update_log(f"⚠ Unknown action. Using fallback Google search for: {fallback_query}")
                    driver.get(f"https://www.google.com/search?q={fallback_query}")

        # 6) Short pause before next loop
        time.sleep(1)  
        # Then the loop continues, calling `detect_wake_word()` again

def start_wake_word_detection():
    """Start the wake word detection in a separate thread."""
    update_log("Starting wake word detection...")
    detection_thread = threading.Thread(target=listen_thread, daemon=True)
    detection_thread.start()

start_wake_word_detection()

##############################
#   Run the GUI Main Loop
##############################
root.mainloop()
