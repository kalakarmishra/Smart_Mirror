# Speak_out_Assistant_with_UI.py
# Integrated Smart Mirror: frontend (Tkinter) + assistant (voice, Gemini, music, weather, jokes, and FET Building Navigator)

import os
import threading
import time
import queue
from datetime import datetime
from urllib.parse import quote

import pyttsx3
import speech_recognition as sr
import requests
import pygame
import vlc
import yt_dlp
import google.generativeai as genai
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox

# ✅ Import FET Building Data
from building_data import building_info

# ---------------- CONFIG ----------------
WEATHER_API_KEY = "eeddbf651f3dc07b4bea92e116270823"
CITY = "Delhi"
GEMINI_API_KEY = "AIzaSyDsWMZWlGjkXhBY4_OLh1WDW_w7soTYKoA"

# ---------------- VLC PATH FIX (Windows) ----------------
try:
    os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
except Exception:
    pass

# ---------------- TTS ----------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
female_voice = next((v for v in voices if "female" in v.name.lower()), None)
if female_voice:
    engine.setProperty('voice', female_voice.id)
else:
    engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)
_engine_lock = threading.Lock()
current_voice = "female"

def speak_async(text):
    """Run TTS in background to avoid blocking UI."""
    def _run(txt):
        try:
            with _engine_lock:
                engine.say(txt)
                engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)
    threading.Thread(target=_run, args=(text,), daemon=True).start()

# ---------------- Google Gemini ----------------
genai.configure(api_key=GEMINI_API_KEY)

def ask_google_gemini(query):
    """Ask Gemini. Fallback tries multiple models. Returns string or raises."""
    try:
        preferred_models = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for model_name in preferred_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(query)
                if response and hasattr(response, "text") and response.text.strip():
                    return response.text.strip()
            except Exception as e:
                print(f">> Model {model_name} failed: {e}")
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                model = genai.GenerativeModel(m.name)
                response = model.generate_content(query)
                if response and hasattr(response, "text") and response.text.strip():
                    return response.text.strip()
        raise RuntimeError("No usable Gemini model returned text.")
    except Exception as e:
        raise e

# ---------------- Music ----------------
pygame.mixer.init()
vlc_instance = vlc.Instance()
vlc_player = None

def play_youtube_music(song_name):
    global vlc_player
    try:
        ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song_name}", download=False)
            if "entries" in info:
                info = info["entries"][0]
            audio_url = info['url']
            title = info.get("title", song_name)
        vlc_player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(audio_url)
        vlc_player.set_media(media)
        vlc_player.audio_set_volume(50)
        vlc_player.play()
        return f"Playing {title}"
    except Exception as e:
        raise e

def pause_youtube_music():
    if vlc_player:
        vlc_player.pause()

def resume_youtube_music():
    if vlc_player:
        vlc_player.play()

def stop_youtube_music():
    global vlc_player
    if vlc_player:
        vlc_player.stop()
        vlc_player = None

def change_voice(gender):
    global current_voice
    voices = engine.getProperty('voices')
    target = next((v for v in voices if gender.lower() in v.name.lower()), None)
    if target:
        engine.setProperty('voice', target.id)
        current_voice = gender.lower()
        return True
    return False

# ---------------- Weather & Jokes ----------------
def fetch_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={quote(city)}&appid={WEATHER_API_KEY}&units=metric"
        j = requests.get(url, timeout=6).json()
        if j.get("main"):
            t = j['main']['temp']
            desc = j['weather'][0]['description'].title()
            return f"{city.title()}: {t}°C, {desc}"
        return "Weather not available"
    except Exception:
        return "Weather error"

def fetch_joke():
    try:
        r = requests.get("https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit", timeout=6).json()
        if r.get('type') == 'single':
            return r.get('joke')
        return f"{r.get('setup')} ... {r.get('delivery')}"
    except Exception:
        return "Couldn't fetch a joke."

# ---------------- NEW FEATURE: FET Building Navigator ----------------
def get_location_info(query):
    """Search FET building data for a matching place name."""
    query = query.lower()
    for name, info in building_info.items():
        if name in query:
            floor = info.get("floor", "unknown")
            room = info.get("room", "unknown")
            if room:
                return f"{name.title()} is located at {floor}, room number {room}."
            else:
                return f"{name.title()} is located at {floor}."
    return "Sorry, I couldn’t find that location in the FET building."

# ---------------- GUI (Tkinter) ----------------
FONT_COLOR = "#ffffff"
BG_COLOR = "#0b0c10"
ACCENT_COLOR = "#1f2833"

root = tk.Tk()
root.title("Smart Mirror — Lush")
root.geometry("1280x720")
root.config(bg=BG_COLOR)
root.attributes("-fullscreen", False)

# --- UI Layout (Time, Weather, Chat, Input) ---
top_frame = tk.Frame(root, bg=BG_COLOR)
top_frame.pack(pady=12)
time_label = tk.Label(top_frame, text="", font=("Segoe UI", 52, "bold"), fg=FONT_COLOR, bg=BG_COLOR)
time_label.pack()
date_label = tk.Label(top_frame, text="", font=("Segoe UI", 18), fg="lightgray", bg=BG_COLOR)
date_label.pack()

weather_frame = tk.Frame(root, bg=ACCENT_COLOR)
weather_frame.pack(padx=30, pady=8, fill="x")
weather_label = tk.Label(weather_frame, text="Loading weather...", font=("Segoe UI", 16), fg=FONT_COLOR, bg=ACCENT_COLOR)
weather_label.pack(padx=10, pady=8)

assistant_frame = tk.Frame(root, bg="#121317", bd=1, relief="ridge")
assistant_frame.pack(padx=30, pady=10, fill="both", expand=True)
assistant_title = tk.Label(assistant_frame, text="💬 Smart Assistant", font=("Segoe UI", 18, "bold"), bg="#121317", fg="#66fcf1")
assistant_title.pack(anchor="w", padx=12, pady=(8,0))

chat_canvas = tk.Canvas(assistant_frame, bg="#0b0c10", highlightthickness=0)
chat_scroll = ttk.Scrollbar(assistant_frame, orient="vertical", command=chat_canvas.yview)
chat_inner = tk.Frame(chat_canvas, bg="#0b0c10")
chat_inner.bind("<Configure>", lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all")))
chat_canvas.create_window((0,0), window=chat_inner, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scroll.set)
chat_canvas.pack(side="left", fill="both", expand=True, padx=(12,0), pady=12)
chat_scroll.pack(side="right", fill="y", padx=(0,12), pady=12)

# --- Input area ---
input_frame = tk.Frame(root, bg="#1b1e22")
input_frame.pack(fill="x", padx=30, pady=(0,16))
user_entry = ttk.Entry(input_frame, font=("Segoe UI", 14))
user_entry.pack(side="left", fill="x", expand=True, padx=(8,8), pady=8)
send_btn = ttk.Button(input_frame, text="Send", width=10)
send_btn.pack(side="right", padx=(0,8))
mic_btn = ttk.Button(input_frame, text="🎤 Speak", width=10)
mic_btn.pack(side="right", padx=6)

_ui_queue = queue.Queue()

def ui_append_message(text, sender="assistant"):
    _ui_queue.put((text, sender))

def _process_ui_queue():
    while not _ui_queue.empty():
        text, sender = _ui_queue.get_nowait()
        ts = datetime.now().strftime("%H:%M:%S")
        display = f"[{ts}] {text}"
        lbl = tk.Label(chat_inner, text=display, anchor="w" if sender=="assistant" else "e",
                       justify="left" if sender=="assistant" else "right",
                       bg="#0b0c10" if sender=="assistant" else "#202020",
                       fg="#00ffcc" if sender=="assistant" else "white",
                       font=("Segoe UI", 12), wraplength=900, padx=8, pady=6)
        lbl.pack(anchor="w" if sender=="assistant" else "e", pady=6, padx=8, fill="x")
        chat_canvas.update_idletasks()
        chat_canvas.yview_moveto(1.0)
    root.after(150, _process_ui_queue)

# ---------------- Time & Weather ----------------
def update_time():
    now = datetime.now()
    time_label.config(text=now.strftime("%I:%M:%S %p"))
    date_label.config(text=now.strftime("%A, %d %B %Y"))
    root.after(1000, update_time)

def update_weather_background():
    def _fetch():
        txt = fetch_weather(CITY)
        weather_label.config(text=txt)
    threading.Thread(target=_fetch, daemon=True).start()
    root.after(600000, update_weather_background)

# ---------------- Voice (click-to-speak) ----------------
_listening_flag = threading.Event()

def listen_and_process():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            _listening_flag.set()
            mic_btn.config(text="🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1.2)
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        cmd = recognizer.recognize_google(audio).lower()
    except Exception:
        cmd = ""
    finally:
        _listening_flag.clear()
        mic_btn.config(text="🎤 Speak")
    if not cmd:
        ui_append_message("I didn't catch that.", "assistant")
        speak_async("I didn't catch that. Please try again.")
        return
    ui_append_message(cmd, "user")
    threading.Thread(target=process_command, args=(cmd,), daemon=True).start()

mic_btn.config(command=lambda: threading.Thread(target=listen_and_process, daemon=True).start())

def on_send_click():
    txt = user_entry.get().strip()
    if not txt:
        return
    user_entry.delete(0, tk.END)
    ui_append_message(txt, "user")
    threading.Thread(target=process_command, args=(txt,), daemon=True).start()

send_btn.config(command=on_send_click)

# ---------------- Command Processor ----------------
def process_command(command):
    command = command.lower()
    try:
        if "where" in command or "location" in command:
            # ✅ NEW FEATURE: FET Building Navigator
            response = get_location_info(command)
            ui_append_message(response, "assistant")
            speak_async(response)

        elif "time" in command or "date" in command:
            now = datetime.now()
            msg = f"Today is {now.strftime('%A, %d %B %Y')} and the time is {now.strftime('%I:%M:%S %p')}"
            ui_append_message(msg, "assistant")
            speak_async(msg)

        elif "weather" in command:
            city = CITY
            if "in " in command:
                try:
                    city = command.split("in ",1)[1].strip()
                except:
                    city = CITY
            w = fetch_weather(city)
            ui_append_message(w, "assistant")
            speak_async(w)

        elif "joke" in command:
            j = fetch_joke()
            ui_append_message(j, "assistant")
            speak_async(j)

        elif "play youtube" in command and "music" in command or ("play" in command and "youtube" in command):
            song = command.replace("play youtube", "").replace("music", "").replace("play", "").strip()
            if song:
                ui_append_message(f"Searching YouTube for {song}...", "assistant")
                try:
                    res = play_youtube_music(song)
                    ui_append_message(res or "Playing from YouTube.", "assistant")
                    speak_async(res or "Playing from YouTube.")
                except Exception as e:
                    ui_append_message(f"Could not play YouTube music: {e}", "assistant")
                    speak_async("Could not play the requested YouTube track.")
            else:
                ui_append_message("Please say the name of the song after play youtube music.", "assistant")
                speak_async("Please say the name of the song after play youtube music.")

        elif "pause music" in command:
            pause_youtube_music()
            ui_append_message("Music paused.", "assistant")
            speak_async("Music paused.")

        elif "resume music" in command:
            resume_youtube_music()
            ui_append_message("Music resumed.", "assistant")
            speak_async("Music resumed.")

        elif "stop music" in command or "stop the music" in command:
            stop_youtube_music()
            ui_append_message("Music stopped.", "assistant")
            speak_async("Music stopped.")

        elif "change voice to female" in command or "female voice" in command:
            ok = change_voice("female")
            msg = "Voice changed to female." if ok else "Female voice not found."
            ui_append_message(msg, "assistant")
            speak_async(msg)

        elif "change voice to male" in command or "male voice" in command:
            ok = change_voice("male")
            msg = "Voice changed to male." if ok else "Male voice not found."
            ui_append_message(msg, "assistant")
            speak_async(msg)

        elif "google" in command or "ask google" in command:
            q = command.replace("ask google", "").replace("google", "").strip()
            if not q:
                msg = "What do you want me to ask Google?"
                ui_append_message(msg, "assistant")
                speak_async(msg)
            else:
                ui_append_message("Asking Google...", "assistant")
                try:
                    ans = ask_google_gemini(q)
                    ui_append_message(ans, "assistant")
                    speak_async(ans)
                except Exception:
                    msg = "Sorry, there was an issue connecting to Google."
                    ui_append_message(msg, "assistant")
                    speak_async(msg)

        elif "stop" in command or "exit" in command or "goodbye" in command:
            ui_append_message("Goodbye! Have a nice day.", "assistant")
            speak_async("Goodbye! Have a nice day.")
            time.sleep(1.2)
            root.quit()

        else:
            ui_append_message("I can help you with time, weather, music, jokes, or ask about FET building locations.", "assistant")
            speak_async("I can help you with time, weather, music, jokes, or ask about FET building locations.")

    except Exception as e:
        print("Processing error:", e)
        ui_append_message("Sorry, I had a problem processing that.", "assistant")
        speak_async("Sorry, I had a problem processing that command.")

# ---------------- Startup ----------------
def startup_greeting():
    msg = "Good evening Aman! My name is Lush. Click the microphone to speak or type below."
    ui_append_message(msg, "assistant")
    speak_async(msg)

root.after(200, _process_ui_queue)
root.after(500, update_time)
root.after(800, update_weather_background)
startup_greeting()
root.mainloop()
