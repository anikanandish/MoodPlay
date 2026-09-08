# MoodPlay 🎵

AI-powered mood-based music recommender with a dark themed UI.!!!!!

## What it does
Type how you're feeling. A local AI suggests 5 songs that match your mood.
No internet needed. No API key. Completely private.

## Built with
- Python
- Ollama
- Gemma 3 (runs locally)
- Tkinter (UI)

## Features
- **Semantic Mood Detection:** Input raw emotions, abstract vibes, or daily thoughts to receive contextual song picks.
- **Dark Mode UI:** Sleek, high-contrast Tkinter interface built with hover transitions and centered layouts.
- **Fast Interaction:** Hit `Enter` to query immediately without touching the mouse.
- **Local Resilience:** Continues functioning entirely without an active network connection.

## How to run
1. Install Ollama from ollama.com
2. Run: ollama pull gemma3
3. pip install ollama
4. python mood2ui.py


##  Future Scope

- [ ] **Spotify API Integration:** Connect directly to Spotify to generate real-time play-lists and stream audio straight from the app.
- [ ] **Multi-Mood Blending:** Allow users to select multiple emotions (e.g., "Chill + Energetic") for more customized recommendations.
- [ ] **UI/UX Polish:** Enhance the Tkinter interface with custom modern themes, dynamic visualizers, and album art displays.
- [ ] **Playlist Export & History:** Save generated playlists locally and export them directly to user streaming accounts.
