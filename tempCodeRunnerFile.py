# mirror_ui.py
import tkinter as tk
from datetime import datetime
import threading
import requests
import time
import queue

# --------------- CONFIG ----------------
CITY = "Delhi"   # change if you want
API_KEY = "eeddbf651f3dc07b4bea92e116270823"

# Thread-safe queue for incoming messages from assistant thread
_msg_queue = queue.Queue()
_root = None
_chat_canvas = None
_chat_inner = None
_time_label = None
_date_label = None
_weather_label = None
_stop_event = threading.Event()

# ----------------- UI BUILD -----------------
def _build_ui():
    global _root, _chat_canvas, _chat_inner, _time_label, _date_label, _weather_label

    root = tk.Tk()
    _root = root
    root.title("Smart Mirror")
    root.configure(bg="black")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: _on_escape())

    # Top - Time & Date
    _time_label = tk.Label(root, text="", font=("Helvetica", 56, "bold"), fg="white", bg="black")
    _time_label.pack(pady=(30, 0))
    _date_label = tk.Label(root, text="", font=("Helvetica", 20), fg="lightgray", bg="black")
    _date_label.pack()

    # Weather
    _weather_label = tk.Label(root, text="", font=("Helvetica", 20), fg="lightblue", bg="black")
    _weather_label.pack(pady=(10, 20))

    # Chat frame
    chat_frame = tk.Frame(root, bg="black")
    chat_frame.pack(fill="both", expand=True, padx=20, pady=(10, 40))

    _chat_canvas = tk.Canvas(chat_frame, bg="black", highlightthickness=0)
    scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=_chat_canvas.yview)
    _chat_inner = tk.Frame(_chat_canvas, bg="black")

    _chat_inner.bind(
        "<Configure>",
        lambda e: _chat_canvas.configure(scrollregion=_chat_canvas.bbox("all"))
    )
    _chat_canvas.create_window((0, 0), window=_chat_inner, anchor="nw")
    _chat_canvas.configure(yscrollcommand=scrollbar.set)

    _chat_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # initial greeting
    show_text_on_mirror("Hello Aman! I am your Smart Mirror Assistant 😊", sender="assistant")

    # start updater loops
    _root.after(100, _process_queue)
    _root.after(0, _update_time_weather_loop)

    return root

# ----------------- STOP/ESC -----------------
def _on_escape():
    # signal stop and quit UI
    _stop_event.set()
    if _root:
        _root.quit()

# ----------------- WEATHER FETCH -----------------
def _get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
        data = requests.get(url, timeout=6).json()
        if data.get("main"):
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].title()
            return f"{CITY}: {temp}°C, {desc}"
    except Exception:
        pass
    return "Weather unavailable"

# ----------------- TIME & WEATHER LOOP -----------------
def _update_time_weather_loop():
    try:
        if _stop_event.is_set():
            return
        now = datetime.now()
        if _time_label:
            _time_label.config(text=now.strftime("%I:%M:%S %p"))
        if _date_label:
            _date_label.config(text=now.strftime("%A, %d %B %Y"))
        # update weather every 60 seconds (non-blocking: use a separate thread)
        if _weather_label:
            # spawn a background thread to fetch weather once
            threading.Thread(target=_fetch_and_set_weather, daemon=True).start()
    except Exception:
        pass
    # schedule again in 1 second for live time
    if _root:
        _root.after(1000, _update_time_weather_loop)

def _fetch_and_set_weather():
    txt = _get_weather()
    try:
        if _weather_label:
            _weather_label.config(text=txt)
    except Exception:
        pass

# ----------------- MESSAGE PROCESSOR -----------------
def _process_queue():
    """Process incoming messages placed into _msg_queue by assistant thread."""
    try:
        while not _msg_queue.empty():
            msg, sender = _msg_queue.get_nowait()
            _append_chat(msg, sender)
    except Exception:
        pass
    if _root and not _stop_event.is_set():
        _root.after(100, _process_queue)

def _append_chat(text, sender="assistant"):
    """Create a label in chat_inner showing text."""
    if not _chat_inner:
        return
    if sender == "user":
        lbl = tk.Label(
            _chat_inner,
            text=f"You: {text}",
            font=("Helvetica", 20),
            fg="white",
            bg="#202020",
            anchor="e",
            justify="right",
            wraplength=900,
            padx=12,
            pady=8
        )
        lbl.pack(anchor="e", pady=6, padx=8)
    else:
        lbl = tk.Label(
            _chat_inner,
            text=f"Lush: {text}",
            font=("Helvetica", 20),
            fg="#00ffcc",
            bg="#000000",
            anchor="w",
            justify="left",
            wraplength=900,
            padx=12,
            pady=8
        )
        lbl.pack(anchor="w", pady=6, padx=8)

    # autoscroll to bottom
    try:
        _chat_canvas.update_idletasks()
        _chat_canvas.yview_moveto(1.0)
    except Exception:
        pass

# --------------- PUBLIC API ------------------
def show_text_on_mirror(text, sender="assistant"):
    """
    Thread-safe function to show text on mirror.
    Call this from any thread.
    sender: "assistant" or "user"
    """
    try:
        _msg_queue.put((str(text), sender))
    except Exception:
        pass

def start_ui():
    """
    Build and start the Tkinter UI. Should be called in the main thread.
    This call blocks until the UI closes.
    """
    root = _build_ui()
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        _stop_event.set()
