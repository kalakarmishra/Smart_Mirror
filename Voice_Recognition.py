import speech_recognition as sr

# Initialize recognizer
r = sr.Recognizer()

# Capture audio from microphone
with sr.Microphone() as source:
    print("Listening... Speak something:")
    r.adjust_for_ambient_noise(source)  # Optional: reduce background noise
    audio = r.listen(source)  # Listen to the user

# Recognize speech using Google Web Speech API
try:
    text = r.recognize_google(audio)
    print("You said:", text)
except sr.UnknownValueError:
    print("Sorry, could not understand audio")
except sr.RequestError as e:
    print("Could not request results; {0}".format(e))
