# MoodPlay 🎵

A private, audiophile AI music companion with a warm vinyl aesthetic. Understands your mood and curates music that fits how you feel—powered entirely by a local **Gemma 3** model via **Ollama**.

---

## ✨ Features

- **100% Private Local AI:** Uses Google Gemma 3 running locally inside Ollama. Your personal mood descriptions never leave your computer.
- **Warm Vinyl Aesthetic:** Modern web application featuring vinyl spinning animation, tone arm mechanics, and amber dark-mode cards.
- **Spotify Curation & Previews:** Direct Spotify search links, live album cover art, and 30-second audio previews (when API keys are supplied; gracefully falls back to offline search links without keys).
- **Acoustic Texture Analysis:** Gemma 3 analyzes your emotional state, tempo curves, and sonic elements to explain why each track fits.
- **Quick Vibe Chips & Search History:** Instant one-click presets like *Late Night Jazz*, *Deep Focus*, *Golden Hour*, and *Midnight Drive*.

---

## 🚀 Quick Start (Localhost Web App)

### 1. Requirements
Ensure [Ollama](https://ollama.com/) is installed with the Gemma 3 model:
```bash
ollama pull gemma3
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Localhost Web App
Run the server:
```bash
python app.py
```
*(Or double-click `run_localhost.bat` on Windows)*

Then open your browser to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🎧 Spotify Setup (Optional)

MoodPlay works out of the box with zero external configuration! If you want live album artwork fetched directly from Spotify's database:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Add your free credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard):
   ```env
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   ```
3. Test your connection:
   ```bash
   python spotify_test.py
   ```

---

## 📁 Project Architecture

- **`app.py`**: FastAPI backend serving the web application and REST endpoints (`/api/recommend`, `/api/status`, `/api/history`).
- **`mood_engine.py`**: Gemma 3 prompt orchestration, JSON extractor, and music curation pipeline.
- **`spotify_service.py`**: Spotify Client Credentials layer with offline-safe search link fallback.
- **`static/`**: Web UI with HTML5, custom turntable styling (`style.css`), and dynamic client logic (`app.js`).
- **`moodplay.py`**: Original CLI prototype.
- **`mood2ui.py`**: Original Tkinter desktop prototype.
