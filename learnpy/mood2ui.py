# MoodPlay UI Module
import sys
print(sys.version)
import tkinter as tk
from tkinter import scrolledtext
import ollama
import threading

def get_playlist():
    mood = mood_input.get()
    if not mood.strip():
        return
    
    result_box.config(state='normal')
    result_box.delete(1.0, tk.END)
    result_box.insert(tk.END, "Finding your playlist...\n\n")
    result_box.config(state='disabled')
    get_btn.config(state='disabled')
    
    def run():
        prompt = f"""
        You are a music expert and DJ.
        Someone is feeling: "{mood}"
        Suggest 5 songs that match this mood.
        For each song:
        🎵 [Song] - [Artist]
        Why: [one sentence reason]
        """
        response = ollama.chat(
            model='gemma3',
            messages=[{'role': 'user', 'content': prompt}]
        )
        result = response['message']['content']
        
        result_box.config(state='normal')
        result_box.delete(1.0, tk.END)
        result_box.insert(tk.END, result)
        result_box.see("1")
        get_btn.config(state='normal')
    
    threading.Thread(target=run).start()

# Window setup
window = tk.Tk()
window.title("🎵 MoodPlay")
window.geometry("600x500")
window.configure(bg="#1a1a2e")

# Title
tk.Label(window, text="🎵 MoodPlay", font=("Arial", 24, "bold"),
         bg="#1a1a2e", fg="#e94560").pack(pady=20)

tk.Label(window, text="How are you feeling?", font=("Arial", 12),
         bg="#1a1a2e", fg="white").pack()

# Input
mood_input = tk.Entry(window, font=("Arial", 14), width=35,
                      bg="#16213e", fg="white", insertbackground="white",
                      relief="flat", bd=10)
mood_input.pack(pady=10)

# Button
get_btn = tk.Button(window, text="Find My Playlist ▶",
                    font=("Arial", 12, "bold"),
                    bg="#e94560", fg="white", relief="flat",
                    padx=20, pady=8, cursor="hand2",
                    command=get_playlist)
get_btn.pack(pady=10)

# Results
result_box = scrolledtext.ScrolledText(window, font=("Arial", 11),
                                        bg="#16213e", fg="white",
                                        relief="flat", bd=10,
                                        state='disabled', wrap=tk.WORD)
result_box.pack(padx=20, pady=10, fill="both", expand=True)

window.mainloop()