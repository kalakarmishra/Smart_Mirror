import pyttsx3
import speech_recognition as sr
from datetime import datetime
import requests
from fer import FER
import cv2

# ---------------------- Initialize TTS Engine ----------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

def speak(text):
    """Speak the given text aloud."""
    print(f"TTS: {text}")  # Debug print
    engine.say(text)
    engine.runAndWait()

# ---------------------- Listen for Voice Command ----------------------
def listen_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone(device_index=None) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print("Listening for command...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        command = recognizer.recognize_google(audio).lower()
        print(f"Command received: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I could not understand you.")
        return ""
    except sr.RequestError:
        speak("Speech service is not available.")
        return ""
    except sr.WaitTimeoutError:
        return ""

# ---------------------- Date & Time ----------------------
def speak_date_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%A, %d %B %Y")
    speak(f"Today is {current_date} and the time is {current_time}")

# ---------------------- Weather ----------------------
import requests
from urllib.parse import quote

def speak_weather(city, api_key):
    try:
        city_encoded = quote(city)  # Convert spaces to %20
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        
        if response.get("main"):
            temp = response['main']['temp']
            description = response['weather'][0]['description']
            speak(f"The temperature in {city.title()} is {temp} degrees Celsius with {description}")
        else:
            print(f"API Response: {response}")  # Debug the exact API response
            speak(f"Sorry, I couldn't fetch weather for {city.title()}")
    except Exception as e:
        print(f"Weather Error: {e}")
        speak("Weather service is not available right now.")


# ---------------------- News ----------------------
def speak_news(api_key, country='us'):
    try:
        url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"
        response = requests.get(url).json()
        articles = response.get('articles')
        if articles:
            speak("Here are the top 3 news headlines.")
            for i, article in enumerate(articles[:3], start=1):
                speak(f"Headline {i}: {article['title']}")
        else:
            speak("No news available at the moment.")
    except Exception as e:
        print(f"News Error: {e}")
        speak("News service is not available right now.")

# ---------------------- Mood Detection ----------------------
def speak_mood():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Cannot access the camera.")
            return

        detector = FER(mtcnn=True)
        speak("Please look at the camera for mood detection.")
        ret, frame = cap.read()

        if ret:
            result = detector.top_emotion(frame)
            if result:
                emotion, score = result
                # Map emotions to emojis
                emotion_emojis = {
                    "happy": "😊",
                    "sad": "😢",
                    "angry": "😠",
                    "surprise": "😮",
                    "fear": "😨",
                    "disgust": "🤢",
                    "neutral": "😐"
                }
                emoji = emotion_emojis.get(emotion, "")
                
                # Speak the mood and show emoji
                speak(f"I think you are feeling {emotion} right now.")
                print(f"Detected mood: {emotion} {emoji}")  # Console output for visual
            else:
                speak("I could not detect your mood.")
        else:
            speak("Failed to capture image from camera.")

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Mood Detection Error: {e}")
        speak("Mood detection is currently unavailable.")


# ---------------------- Main Interactive Loop ----------------------
if __name__ == "__main__":
    WEATHER_API_KEY = "eeddbf651f3dc07b4bea92e116270823"
    NEWS_API_KEY = "73cae16a679b4df090ef1c6e918c4989"
    DEFAULT_CITY = "Kanpur"
    DEFAULT_COUNTRY = "us"

    speak("Hello! I am your smart mirror. How Can I help you.")

    while True:
        command = listen_command()
        if not command:
            continue  # Nothing recognized, continue listening

        # ------------------ Time / Date ------------------
        if "time" in command or "date" in command:
            speak_date_time()

        # ------------------ Weather ------------------
        elif "weather" in command:
            city_name = DEFAULT_CITY
            # Look for "in <city>" or "of <city>"
            if "in " in command:
                city_name = command.split("in ")[1].strip()
            elif "of " in command:
                city_name = command.split("of ")[1].strip()
            speak_weather(city_name, WEATHER_API_KEY)

        # ------------------ News ------------------
        elif "news" in command:
            country_code = DEFAULT_COUNTRY
            # Look for "from <country>"
            if "from " in command:
                country_name = command.split("from ")[1].strip().lower()
                # Map country names to ISO 3166 country codes
                country_map = {
                    "india": "in",
                    "us": "us",
                    "united states": "us",
                    "uk": "gb",
                    "united kingdom": "gb",
                    "canada": "ca",
                    "australia": "au"
                    # Add more as needed
                }
                country_code = country_map.get(country_name, DEFAULT_COUNTRY)
            speak_news(NEWS_API_KEY, country_code)

        # ------------------ Mood ------------------
        elif "mood" in command or "feeling" in command:
            speak_mood()

        # ------------------ Exit ------------------
        elif "exit" in command or "stop" in command:
            speak("Goodbye! Have a nice day.")
            break

        # ------------------ Unrecognized ------------------
        else:
            speak("Sorry, I can't perform that command.")