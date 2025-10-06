import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import requests
from PIL import Image, ImageTk

# ---------- CONFIGURATION ----------
WEATHER_API_KEY = "587d94fd0e7f6bf720c0428411c94803"
CITY = "Delhi"
FONT_COLOR = "#ffffff"
BG_COLOR = "#0b0c10"
ACCENT_COLOR = "#1f2833"

# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("Smart Mirror")
root.geometry("1280x720")
root.config(bg=BG_COLOR)
root.attributes("-fullscreen", False)  # Set True for real mirror mode

# ---------- FONTS ----------
time_font = ("Segoe UI", 60, "bold")
date_font = ("Segoe UI", 20, "bold")
weather_font = ("Segoe UI", 18)
assistant_font = ("Segoe UI", 16)
heading_font = ("Segoe UI", 22, "bold")

# ---------- TOP FRAME (TIME & DATE) ----------
top_frame = tk.Frame(root, bg=BG_COLOR)
top_frame.pack(pady=20)

time_label = tk.Label(top_frame, text="", font=time_font, fg=FONT_COLOR, bg=BG_COLOR)
time_label.pack()

date_label = tk.Label(top_frame, text="", font=date_font, fg=FONT_COLOR, bg=BG_COLOR)
date_label.pack()

# ---------- WEATHER FRAME ----------
weather_frame = tk.Frame(root, bg=ACCENT_COLOR)
weather_frame.pack(pady=20, fill="x", padx=50)

weather_label = tk.Label(weather_frame, text="Loading weather...", font=weather_font, fg=FONT_COLOR, bg=ACCENT_COLOR)
weather_label.pack(pady=10)

# ---------- FACE/USER SECTION ----------
user_frame = tk.Frame(root, bg=BG_COLOR)
user_frame.pack(pady=20)

try:
    img = Image.open("face.png")  # Optional face or logo image
    img = img.resize((120, 120))
    img_tk = ImageTk.PhotoImage(img)
    face_label = tk.Label(user_frame, image=img_tk, bg=BG_COLOR)
    face_label.pack()
except Exception:
    face_label = tk.Label(user_frame, text="🙂", font=("Segoe UI", 80), bg=BG_COLOR, fg=FONT_COLOR)
    face_label.pack()

user_name_label = tk.Label(user_frame, text="Hello, Aman!", font=heading_font, fg="#66fcf1", bg=BG_COLOR)
user_name_label.pack()

# ---------- CHAT ASSISTANT SECTION ----------
assistant_frame = tk.Frame(root, bg="#1b1e22", relief="ridge", bd=2)
assistant_frame.pack(pady=20, fill="both", expand=True, padx=50)

assistant_title = tk.Label(assistant_frame, text="💬 Smart Assistant", font=heading_font, bg="#1b1e22", fg="#66fcf1")
assistant_title.pack(pady=5)

chat_box = tk.Text(assistant_frame, height=10, bg="#0b0c10", fg="#ffffff", font=assistant_font, wrap="word", state="disabled", bd=0, relief="flat")
chat_box.pack(padx=20, pady=10, fill="both", expand=True)

entry_frame = tk.Frame(assistant_frame, bg="#1b1e22")
entry_frame.pack(pady=10, fill="x")

user_entry = ttk.Entry(entry_frame, font=assistant_font)
user_entry.pack(side="left", fill="x", expand=True, padx=10)

def send_message():
    message = user_entry.get().strip()
    if message:
        chat_box.config(state="normal")
        chat_box.insert(tk.END, f"You: {message}\n", "user")
        chat_box.config(state="disabled")
        user_entry.delete(0, tk.END)
        # Backend function call (voice or Gemini)
        append_bot_message("Thinking... 🤖")

def append_bot_message(msg):
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"Mirror: {msg}\n\n", "bot")
    chat_box.config(state="disabled")
    chat_box.yview(tk.END)

send_btn = ttk.Button(entry_frame, text="Send", command=send_message)
send_btn.pack(side="right", padx=10)

# ---------- STYLES ----------
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 12), padding=6, background="#66fcf1", foreground="black")

# ---------- LIVE TIME ----------
def update_time():
    now = datetime.now()
    time_label.config(text=now.strftime("%I:%M:%S %p"))
    date_label.config(text=now.strftime("%A, %B %d, %Y"))
    time_label.after(1000, update_time)

# ---------- WEATHER ----------
def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].title()
            weather_label.config(text=f"{CITY}: {temp}°C | {desc}")
        else:
            weather_label.config(text="Unable to load weather.")
    except Exception as e:
        weather_label.config(text="Weather error.")
    root.after(600000, get_weather)  # Update every 10 minutes

# ---------- ANIMATED BACKGROUND (OPTIONAL) ----------
def gradient_bg():
    colors = ["#0b0c10", "#1f2833", "#0b0c10"]
    current_color = colors[0]
    def animate_bg():
        nonlocal current_color
        current_color = colors[(colors.index(current_color) + 1) % len(colors)]
        root.config(bg=current_color)
        root.after(8000, animate_bg)
    animate_bg()

# ---------- START ----------
gradient_bg()
update_time()
get_weather()

append_bot_message("Welcome! I’m your Smart Mirror Assistant 😄")

root.mainloop()
