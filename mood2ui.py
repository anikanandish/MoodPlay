#trying somethingbg
import os
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext
from dotenv import load_dotenv
import ollama

# 1. Load Spotify credentials from .env
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

mood_history = []


def log_mood(mood):
    """Saves recent mood queries to history (keeps last 5)."""
    if mood and mood not in mood_history:
        mood_history.insert(0, mood)
        if len(mood_history) > 5:
            mood_history.pop()
        print(f"Recent moods: {', '.join(mood_history)}")


def get_playlist():
    mood = mood_input.get().strip()
    if not mood:
        return

    log_mood(mood)

    # Disable button & show loading state
    get_btn.config(state="disabled")
    result_box.config(state="normal")
    result_box.delete(1.0, tk.END)
    result_box.insert(tk.END, "🎵 DJ Gemma is thinking of your playlist...\n\n")
    result_box.config(state="disabled")

    # Run Ollama in background thread so GUI doesn't freeze
    def fetch_music():
        prompt = f"""
        You are an expert DJ. Someone is feeling: "{mood}".
        Suggest 5 songs matching this mood.
        Format each song strictly like this:
        🎵 [Song Title] - [Artist]
        Why: [One sentence explanation]
        """
        try:
            response = ollama.chat(
                model="gemma3",
                messages=[{"role": "user", "content": prompt}],
            )
            result = response["message"]["content"]
        except Exception as e:
            result = f"Error fetching recommendations: {e}"

        # Update GUI on main thread
        result_box.config(state="normal")
        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, result)
        result_box.config(state="disabled")
        get_btn.config(state="normal")

    threading.Thread(target=fetch_music, daemon=True).start()


def clear_all():
    mood_input.delete(0, tk.END)
    result_box.config(state="normal")
    result_box.delete(1.0, tk.END)
    result_box.config(state="disabled")


# --- Window Setup ---
window = tk.Tk()
window.title("🎵 MoodPlay")
window.geometry("500x550")
window.configure(bg="#1a1a2e")
window.resizable(False, False)

# --- UI Elements ---
tk.Label(
    window,
    text="🎵 MoodPlay",
    font=("Arial", 22, "bold"),
    bg="#1a1a2e",
    fg="#610e1c",
).pack(pady=(15, 5))
tk.Label(
    window,
    text="How are you feeling today?",
    font=("Arial", 11),
    bg="#1a1a2e",
    fg="#a0a0c0",
).pack()

mood_input = tk.Entry(
    window,
    font=("Arial", 13),
    width=30,
    bg="#3f5797",
    fg="white",
    insertbackground="white",
    relief="flat",
    justify="center",
)
mood_input.pack(pady=12)
mood_input.bind("<Return>", lambda event: get_playlist())

# Buttons Frame
btn_frame = tk.Frame(window, bg="#1a1a2e")
btn_frame.pack(pady=5)

get_btn = tk.Button(
    btn_frame,
    text="Find Playlist ▶",
    font=("Arial", 10, "bold"),
    bg="#e94560",
    fg="white",
    relief="flat",
    padx=15,
    pady=5,
    cursor="hand2",
    command=get_playlist,
)
get_btn.grid(row=0, column=0, padx=5)

clear_btn = tk.Button(
    btn_frame,
    text="Clear",
    font=("Arial", 10),
    bg="#0f3460",
    fg="white",
    relief="flat",
    padx=15,
    pady=5,
    cursor="hand2",
    command=clear_all,
)
clear_btn.grid(row=0, column=1, padx=5)

result_box = scrolledtext.ScrolledText(
    window,
    font=("Arial", 10),
    bg="#16213e",
    fg="white",
    relief="flat",
    bd=10,
    state="disabled",
    wrap=tk.WORD,
)
result_box.pack(padx=20, pady=15, fill="both", expand=True)

window.mainloop()