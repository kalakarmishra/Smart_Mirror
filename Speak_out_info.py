import pyttsx3
import speech_recognition as sr
from datetime import datetime
import requests
from fer import FER
import cv2
from urllib.parse import quote
import time
import random
import threading
import pygame
import os
import vlc
import yt_dlp
import google.generativeai as genai
from building_data import building_info   # ✅ NEW IMPORT for FET location data

# ---------------------- VLC Path Fix ----------------------
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")

# ---------------------- Initialize TTS Engine ----------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Try to set default voice to female
female_voice = next((v for v in voices if "female" in v.name.lower()), None)
if female_voice:
    engine.setProperty('voice', female_voice.id)
else:
    engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

current_voice = "female"

def speak(text):
    print(f">> {text}")
    engine.say(text)
    engine.runAndWait()

def change_voice(gender):
    global current_voice
    voices = engine.getProperty('voices')
    target_voice = None
    for v in voices:
        if gender.lower() in v.name.lower():
            target_voice = v
            break
    if target_voice:
        engine.setProperty('voice', target_voice.id)
        current_voice = gender.lower()
        speak(f"Voice changed to {gender}.")
    else:
        speak(f"Sorry, I couldn't find a {gender} voice on this system.")

# ---------------------- Google Gemini Setup ----------------------
GEMINI_API_KEY = "AIzaSyDsWMZWlGjkXhBY4_OLh1WDW_w7soTYKoA"  # Replace with your key
genai.configure(api_key=GEMINI_API_KEY)

def ask_google(query):
    """Improved Gemini AI Assistant with fallback model detection."""
    try:
        preferred_models = [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]

        for model_name in preferred_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(query)
                if response and hasattr(response, 'text'):
                    speak(response.text)
                    return
            except Exception as e:
                print(f">> Model {model_name} failed: {e}")

        print(">> Fetching available Gemini models...")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                model = genai.GenerativeModel(m.name)
                response = model.generate_content(query)
                if response and hasattr(response, 'text'):
                    speak(response.text)
                    return

        speak("Sorry, I couldn't connect to Google right now.")
    except Exception as e:
        print(f">> Google Assistant Error: {e}")
        speak("Sorry, I couldn't connect to Google at the moment.")

# ---------------------- Initialize Music ----------------------
pygame.mixer.init()
vlc_instance = vlc.Instance()
vlc_player = None

def play_mp3_music():
    try:
        mp3_files = [f for f in os.listdir(os.getcwd()) if f.lower().endswith(".mp3")]
        if not mp3_files:
            speak("No music files found in the folder.")
            return
        music_file = mp3_files[0]
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()
        speak(f"Playing {music_file} now.")
    except Exception as e:
        speak(f"Cannot play music: {e}")

def play_youtube_music(song_name):
    global vlc_player
    try:
        speak(f"Searching YouTube for {song_name}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{song_name}", download=False)
            if "entries" in info:
                info = info["entries"][0]
            audio_url = info['url']
            title = info.get("title", "this track")

        vlc_player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(audio_url)
        vlc_player.set_media(media)
        vlc_player.audio_set_volume(50)
        vlc_player.play()
        speak(f"Now playing {title} from YouTube.")
    except Exception as e:
        speak(f"Could not play YouTube music: {e}")

def pause_youtube_music():
    if vlc_player:
        vlc_player.pause()
        speak("Music paused.")

def resume_youtube_music():
    if vlc_player:
        vlc_player.play()
        speak("Music resumed.")

def stop_youtube_music():
    global vlc_player
    if vlc_player:
        vlc_player.stop()
        speak("Music stopped.")
        vlc_player = None

def increase_volume(step=20):
    if vlc_player:
        current = vlc_player.audio_get_volume()
        new_vol = min(100, current + step)
        vlc_player.audio_set_volume(new_vol)
        speak(f"Volume increased to {new_vol} percent.")

def decrease_volume(step=20):
    if vlc_player:
        current = vlc_player.audio_get_volume()
        new_vol = max(0, current - step)
        vlc_player.audio_set_volume(new_vol)
        speak(f"Volume decreased to {new_vol} percent.")

# ---------------------- Dynamic Joke ----------------------
def tell_joke():
    try:
        response = requests.get("https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit")
        data = response.json()
        if data['type'] == 'single':
            speak(data['joke'])
        elif data['type'] == 'twopart':
            speak(data['setup'])
            time.sleep(2)
            speak(data['delivery'])
    except Exception as e:
        print(f"Joke API Error: {e}")
        speak("Sorry, I cannot fetch a joke right now.")

# ---------------------- NEW: FET Building Navigator ----------------------
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

# ---------------------- Voice Command Listener ----------------------
def listen_command(duration=5):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print("🎤 Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=duration)
        command = recognizer.recognize_google(audio).lower()
        print(f"✅ Command received: {command}")
        return command
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Speech service is not available.")
        return ""
    except Exception as e:
        print(f"Recording error: {e}")
        return ""

# ---------------------- Weather ----------------------
def speak_weather(city, api_key):
    try:
        city_encoded = quote(city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        if response.get("main"):
            temp = response['main']['temp']
            description = response['weather'][0]['description']
            speak(f"The temperature in {city.title()} is {temp}°C with {description}")
        else:
            speak(f"Sorry, I couldn't fetch weather for {city.title()}")
    except Exception as e:
        print(f"Weather Error: {e}")
        speak("Weather service is not available right now.")

# ---------------------- Main Loop ----------------------
if __name__ == "__main__":
    WEATHER_API_KEY = "eeddbf651f3dc07b4bea92e116270823"

    now = datetime.now()
    hour = now.hour
    day = now.strftime('%A')

    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 17 <= hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good night"

    print(f">> {greeting} Aman! My name is Lush.")
    engine.say(f"{greeting} Aman! My name is Lush.")
    engine.runAndWait()

    if day in ["Saturday", "Sunday"]:
        engine.say(f"It's {day}, hope you're enjoying your weekend.")
        engine.runAndWait()

    time.sleep(1)

    active = False

    while True:
        if not active:
            command = listen_command(duration=3)
            if "hello lush" in command:
                speak("Hello Aman! What can I do for you?")
                active = True
            else:
                continue

        command = listen_command()
        if not command:
            time.sleep(1)
            continue

        # ---------- Commands ----------
        if "time" in command or "date" in command:
            now = datetime.now()
            speak(f"Today is {now.strftime('%A, %d %B %Y')} and time is {now.strftime('%I:%M %p')}")

        elif "weather" in command:
            speak("Which city do you want the weather for?")
            city = listen_command()
            if city:
                speak_weather(city, WEATHER_API_KEY)
            else:
                speak("I didn’t catch the city name.")

        elif "joke" in command:
            tell_joke()

        elif "youtube" in command and "music" in command:
            song = command.replace("play youtube", "").replace("music", "").strip()
            if song:
                play_youtube_music(song)
            else:
                speak("Please tell me the name of the song.")

        elif "pause music" in command:
            pause_youtube_music()

        elif "resume music" in command:
            resume_youtube_music()

        elif "stop music" in command:
            stop_youtube_music()

        elif "increase volume" in command:
            increase_volume()

        elif "decrease volume" in command:
            decrease_volume()

        elif "change voice to female" in command:
            change_voice("female")

        elif "change voice to male" in command:
            change_voice("male")

        # ✅ NEW FEATURE: FET Building Queries
        elif "where" in command or "location" in command:
            response = get_location_info(command)
            speak(response)

        elif "google" in command or "ask google" in command:
            query = command.replace("ask google", "").replace("google", "").strip()
            if query:
                ask_google(query)
            else:
                speak("What do you want me to ask Google?")

        elif "stop" in command or "exit" in command:
            speak("Goodbye Aman! Have a great day.")
            stop_youtube_music()
            break

        else:
            speak("I can help you with time, weather, music, jokes, or you can ask Google for more.")
