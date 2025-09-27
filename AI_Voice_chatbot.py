# smart_mirror_ai_enhanced.py

import cv2
import pyttsx3
import speech_recognition as sr
import numpy as np
import random
import mediapipe as mp
from tensorflow.keras.models import load_model
from datetime import datetime

# --------------------- Initialize TTS ---------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

def speak(text):
    """Convert text to speech"""
    print(f"Mirror: {text}")
    engine.say(text)
    engine.runAndWait()

# --------------------- Voice Input ---------------------
def listen():
    """Capture voice input and return as text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        print(f"You said: {query}")
        return query.lower()
    except:
        speak("Sorry, I could not understand you.")
        return ""

# --------------------- Mediapipe Face Detection ---------------------
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

def analyze_face(frame):
    """Detect face & skin issues using Mediapipe"""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    with mp_face.FaceDetection(min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(rgb_frame)

        if not results.detections:
            return "No face detected."

        # Basic Skin Issue Simulation (later replace with CNN skin analysis model)
        skin_issues = ["pimples", "dark spots", "tanning", "clear skin"]
        remedies = {
            "pimples": "Wash face twice daily and apply tea tree oil.",
            "dark spots": "Use aloe vera gel and lemon mask.",
            "tanning": "Use turmeric face pack or yogurt mask.",
            "clear skin": "Your skin looks healthy. Keep it up!"
        }
        issue = random.choice(skin_issues)
        suggestion = remedies[issue]
        return f"Detected {issue}. Suggestion: {suggestion}"

# --------------------- Dressing Sense Detection ---------------------
# Dummy Pre-trained Fashion Model (for real use, train on DeepFashion dataset)
# You can replace with your own model like fashion_mnist.h5
try:
    fashion_model = load_model("fashion_mnist.h5")
except:
    fashion_model = None
    print("⚠️ Fashion model not found, using color-based suggestions instead.")

def analyze_dress(frame):
    """Analyze outfit using ML model (if available) or fallback to color analysis"""
    if fashion_model:
        resized = cv2.resize(frame, (28, 28))  # assuming model trained on 28x28
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        gray = gray.reshape(1, 28, 28, 1) / 255.0
        pred = np.argmax(fashion_model.predict(gray))
        categories = ["T-shirt", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle Boot"]
        suggestion = f"You seem to be wearing {categories[pred]}. Pair it smartly with accessories."
        return suggestion
    else:
        # Fallback: Color-based suggestion
        avg_color_per_row = np.average(frame, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        red, green, blue = avg_color
        if red > 150:
            return "Your outfit has red. Bold choice! Pair it with black or white."
        elif blue > 150:
            return "Your outfit has blue. Calm and casual."
        else:
            return "Neutral outfit detected. Very versatile."

# --------------------- Simple Chatbot ---------------------
def chatbot_response(query):
    """Provide basic chatbot responses"""
    greetings = ["hello", "hi", "hey"]
    if any(word in query for word in greetings):
        return random.choice(["Hello! How can I help you today?", "Hi there!"])
    elif "weather" in query:
        return "I can check the weather if connected to the internet."
    elif "time" in query:
        now = datetime.now().strftime("%H:%M")
        return f"The current time is {now}."
    elif "your name" in query:
        return "I am your Smart Mirror AI assistant."
    else:
        return "I am still learning. Can you ask something else?"

# --------------------- Main Function ---------------------
def main():
    cap = cv2.VideoCapture(0)
    speak("Hello! I am your Smart Mirror. How can I assist you today?")
    
    while True:
        query = listen()
        if query == "":
            continue
        elif "face" in query or "skin" in query:
            ret, frame = cap.read()
            if not ret:
                speak("Camera not working.")
                continue
            result = analyze_face(frame)
            speak(result)
        elif "dress" in query or "clothing" in query or "outfit" in query:
            ret, frame = cap.read()
            if not ret:
                speak("Camera not working.")
                continue
            result = analyze_dress(frame)
            speak(result)
        elif "exit" in query or "quit" in query:
            speak("Goodbye!")
            breakq
        else:
            response = chatbot_response(query)
            speak(response)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
