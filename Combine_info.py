import tkinter as tk
from time import strftime
import requests

# Your API Key & City
API_KEY = "587d94fd0e7f6bf720c0428411c94803"
CITY = "Kanpur"

# Function to get weather
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data.get("cod") == 200:
            weather = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            return f"{CITY}: {weather}, {temp}°C"
        else:
            return "Weather data unavailable"
    except:
        return "Error fetching weather"

# Function to update time, date & weather
def update_display():
    # Time & Date
    time_str = strftime("%H:%M:%S")
    date_str = strftime("%A, %d %B %Y")

    time_label.config(text=time_str)
    date_label.config(text=date_str)

    # Weather
    weather_str = get_weather()
    weather_label.config(text=weather_str)

    # Refresh every 1 second
    root.after(1000, update_display)

# Tkinter window setup
root = tk.Tk()
root.title("Smart Mirror")
root.configure(bg="black")
root.attributes("-fullscreen", False)  # Change to True later for mirror effect

# Labels
time_label = tk.Label(root, font=("Helvetica", 50), fg="white", bg="black")
time_label.pack(pady=20)

date_label = tk.Label(root, font=("Helvetica", 25), fg="white", bg="black")
date_label.pack(pady=10)

weather_label = tk.Label(root, font=("Helvetica", 20), fg="white", bg="black")
weather_label.pack(pady=10)

# Start display
update_display()
root.mainloop()
