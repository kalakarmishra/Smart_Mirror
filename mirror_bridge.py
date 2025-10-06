# mirror_bridge.py
# This file allows Speak_out_info and movie_ui to share messages in real-time.

import queue

message_queue = queue.Queue()

def send_to_mirror(text: str):
    """Called from Speak_out_info to show text on mirror."""
    message_queue.put(text)

def get_from_assistant():
    """Called from movie_ui to fetch the latest message."""
    try:
        return message_queue.get_nowait()
    except queue.Empty:
        return None
