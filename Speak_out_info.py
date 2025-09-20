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
    engine.stop()  # Stop any ongoing speech
    engine.say(text)
    engine.runAndWait()

# ---------------------- Listen for Voice Command ----------------------
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for command...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        speak("Sorry, I could not understand you.")
        return ""
    except sr.RequestError:
        speak("Speech service is not available.")
        return ""

# ---------------------- Date & Time ----------------------
def speak_date_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%A, %d %B %Y")
    speak(f"Today is {current_date} and the time is {current_time}")

# ---------------------- Weather ----------------------
def speak_weather(city, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        if response.get("main"):
            temp = response['main']['temp']
            description = response['weather'][0]['description']
            speak(f"The temperature in {city} is {temp} degrees Celsius with {description}")
        else:
            speak(f"Sorry, I couldn't fetch weather for {city}")
    except:
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
    except:
        speak("News service is not available right now.")

# ---------------------- Mood Detection ----------------------
def speak_mood():
    try:
        cap = cv2.VideoCapture(0)
        detector = FER(mtcnn=True)
        speak("Please look at the camera for mood detection.")
        ret, frame = cap.read()
        if ret:
            result = detector.top_emotion(frame)
            if result:
                emotion, score = result
                speak(f"I think you are feeling {emotion} right now.")
            else:
                speak("I could not detect your mood.")
        cap.release()
        cv2.destroyAllWindows()
    except:
        speak("Mood detection is currently unavailable.")

# ---------------------- Main Interactive Loop ----------------------
if __name__ == "__main__":
    # Replace with your API keys and city
    WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
    NEWS_API_KEY = "YOUR_NEWSAPI_KEY"
    CITY = "YourCity"

    speak("Hello! I am your smart mirror. You can ask me about time, date, weather, news, or mood. Say 'exit' to stop.")

    while True:
        command = listen_command()

        if "time" in command or "date" in command:
            speak_date_time()
        elif "weather" in command:
            speak_weather(CITY, WEATHER_API_KEY)
        elif "news" in command:
            speak_news(NEWS_API_KEY)
        elif "mood" in command or "feeling" in command:
            speak_mood()
        elif "exit" in command or "stop" in command:
            speak("Goodbye! Have a nice day.")
            break
        elif command != "":
            speak("Sorry, I can't perform that command.")
