import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# ===============================
# Add project root to Python path
# ===============================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ===============================
# Import Smart Mirror functions
# ===============================
try:
    from Speak_out_assistant_with_ui import (
        fetch_weather,
        fetch_joke,
        ask_google_gemini,
        play_youtube_music,
        stop_youtube_music
    )
except ModuleNotFoundError as e:
    if "Speak_out_assistant_with_ui" in str(e):
        raise ModuleNotFoundError(
            f"Could not find Speak_out_assistant_with_ui.py in {BASE_DIR}. "
            "Make sure your folder structure is:\n"
            "Smart Mirror/\n"
            "├─ backend/\n"
            "│  └─ api_backend.py\n"
            "└─ Speak_out_assistant_with_ui.py"
        ) from e
    else:
        # Raise the actual missing package error (like pyttsx3, pygame, etc.)
        raise

# ===============================
# Initialize Flask app
# ===============================
app = Flask(__name__)
CORS(app)

# ===============================
# API Routes
# ===============================
@app.route("/")
def home():
    return jsonify({"status": "Smart Mirror API Running ✅"})

@app.route("/weather")
def weather():
    city = request.args.get("city", "Delhi")
    return jsonify({"weather": fetch_weather(city)})

@app.route("/joke")
def joke():
    return jsonify({"joke": fetch_joke()})

@app.route("/ask_gemini", methods=["POST"])
def ask_gemini():
    data = request.get_json() or {}
    query = data.get("query", "")
    return jsonify({"answer": ask_google_gemini(query)})

@app.route("/youtube", methods=["POST"])
def youtube():
    data = request.get_json() or {}
    song = data.get("song", "")
    msg = play_youtube_music(song)
    return jsonify({"status": "playing", "message": msg})

@app.route("/stop_music")
def stop_music():
    stop_youtube_music()
    return jsonify({"status": "stopped"})

# ===============================
# Run Flask server
# ===============================
if __name__ == "__main__":
    print(f"🚀 Starting Smart Mirror API on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
