"""
mood_engine.py — Core AI mood understanding powered by local Gemma 3 via Ollama.
Includes auto-startup for Ollama and an offline acoustic vault fallback.
"""

import json
import re
import subprocess
import shutil
import ollama
from spotify_service import search_track

MODEL_NAME = "gemma3"

# Curated acoustic vault for offline / warmup fallback
VAULT = {
    "jazz": {
        "headline": "Velvet Brass & Dim Lamplight",
        "analysis": "Warm brushwork, melancholic horn voicings, and understated walking basslines.",
        "songs": [
            {"title": "Autumn Leaves", "artist": "Bill Evans Trio", "reason": "Tender, contemplative piano phrasing perfectly fitted for quiet hours."},
            {"title": "'Round Midnight", "artist": "Thelonious Monk", "reason": "Atmospheric dissonance that captures late-night introspection."},
            {"title": "Blue in Green", "artist": "Miles Davis", "reason": "Haunting muted trumpet evoking stillness and solitude."},
            {"title": "My Foolish Heart", "artist": "Bill Evans", "reason": "Delicate touch and gentle impressionistic jazz harmonies."}
        ]
    },
    "rain": {
        "headline": "Raindrops on Glass & Soft Keys",
        "analysis": "Gentle acoustic resonance, muted reverb, and soothing ambient cadences.",
        "songs": [
            {"title": "Nuvole Bianche", "artist": "Ludovico Einaudi", "reason": "Gentle, repetitive piano progressions that mimic falling rain."},
            {"title": "Comptine d'un autre été", "artist": "Yann Tiersen", "reason": "Nostalgic accordion and piano with an intimate European rainfall charm."},
            {"title": "Coffee", "artist": "Tom Misch & Yussef Dayes", "reason": "Downtempo neo-soul groove ideal for watching rain outside your window."},
            {"title": "Gymnopédie No. 1", "artist": "Erik Satie", "reason": "Minimalist, bittersweet melancholy that calms the senses."}
        ]
    },
    "focus": {
        "headline": "Flow State & Steady Harmonies",
        "analysis": "Non-intrusive rhythmic pulses, clean synths, and steady momentum for deep focus.",
        "songs": [
            {"title": "Weightless", "artist": "Marconi Union", "reason": "Scientifically arranged ambient frequencies designed to lower heart rate and reduce stress."},
            {"title": "An Ending (Ascent)", "artist": "Brian Eno", "reason": "Spacious, celestial synthesis offering friction-free background texture."},
            {"title": "Avril 14th", "artist": "Aphex Twin", "reason": "Pristine acoustic piano with serene, focused melodic lines."},
            {"title": "Day One", "artist": "Hans Zimmer", "reason": "Inspirational organ swells that sustain unbroken cognitive momentum."}
        ]
    },
    "energetic": {
        "headline": "Electric Momentum & Solar Pulse",
        "analysis": "Upbeat grooves, bright horn sections, and driving percussive energy.",
        "songs": [
            {"title": "September", "artist": "Earth, Wind & Fire", "reason": "Irresistible groove and infectious brass that instantly sparks joy."},
            {"title": "Walking on a Dream", "artist": "Empire of the Sun", "reason": "Shimmering synth lines and uplifting forward driving energy."},
            {"title": "Don't Stop Me Now", "artist": "Queen", "reason": "High-octane vocal dynamism and unstoppable upbeat momentum."},
            {"title": "Electric Feel", "artist": "MGMT", "reason": "Psych-pop rhythm and contagious bass groove."}
        ]
    },
    "default": {
        "headline": "Harmonic Resonance & Modern Soul",
        "analysis": "A balanced acoustic journey blending organic instrumentation and rich melodies.",
        "songs": [
            {"title": "Dreams", "artist": "Fleetwood Mac", "reason": "Effortless groove with warm, nostalgic folk-rock textures."},
            {"title": "Sunflower", "artist": "Post Malone & Swae Lee", "reason": "Breezy melodic hooks and uplifting relaxed pacing."},
            {"title": "Holocene", "artist": "Bon Iver", "reason": "Expansive acoustic guitars and ethereal layered vocals."},
            {"title": "Sunset Lover", "artist": "Petit Biscuit", "reason": "Lush melodic chillwave with soothing vocal chops."}
        ]
    }
}


def ensure_ollama_running():
    """Tries to check if Ollama is accessible; if not, attempts background launch."""
    try:
        ollama.list()
        return True
    except Exception:
        pass

    # Try launching ollama serve in background
    ollama_path = shutil.which("ollama") or r"C:\Users\nandi\AppData\Local\Programs\Ollama\ollama.exe"
    try:
        subprocess.Popen(
            [ollama_path, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    except Exception as e:
        print(f"[OllamaAutoStart] Error: {e}")
    return False


def check_ollama_status():
    """Checks if Ollama is accessible and if gemma3 is available."""
    try:
        models_resp = ollama.list()
        models = [m.get("model", "") or m.get("name", "") for m in models_resp.get("models", [])]
        has_gemma = any("gemma3" in m for m in models)
        return {
            "online": True,
            "has_model": has_gemma,
            "model": MODEL_NAME,
            "models_available": models
        }
    except Exception as e:
        return {
            "online": False,
            "has_model": False,
            "error": str(e)
        }


def extract_json_from_text(text: str):
    """Robustly extracts JSON from an LLM response even if wrapped in markdown code blocks."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start:end+1]
        try:
            return json.loads(snippet)
        except Exception:
            pass

    return None


def get_offline_vault_recommendation(mood: str, count: int = 5):
    """Matches the user's mood to curated acoustic vault entries if Ollama is offline."""
    lower_mood = mood.lower()
    chosen_category = "default"

    if any(k in lower_mood for k in ["jazz", "night", "wine", "midnight", "brass", "sax"]):
        chosen_category = "jazz"
    elif any(k in lower_mood for k in ["rain", "storm", "lofi", "chill", "relax", "melanchol", "sad", "quiet"]):
        chosen_category = "rain"
    elif any(k in lower_mood for k in ["focus", "study", "code", "work", "ambient", "read", "deep"]):
        chosen_category = "focus"
    elif any(k in lower_mood for k in ["happy", "energetic", "dance", "party", "run", "workout", "upbeat", "hyped"]):
        chosen_category = "energetic"

    vault_entry = VAULT.get(chosen_category, VAULT["default"])
    return {
        "vibe_headline": vault_entry["headline"],
        "vibe_analysis": f"{vault_entry['analysis']} (Curated via MoodPlay acoustic vault).",
        "songs": vault_entry["songs"][:count]
    }


def get_music_recommendations(mood: str, count: int = 5):
    """
    Prompts local Gemma 3 to analyze the user's mood and return structured tracks.
    If Ollama is offline or unavailable, automatically falls back to curated vault.
    Then enriches each track with Spotify metadata (artwork, link, preview).
    """
    ensure_ollama_running()

    prompt = f"""You are an elite music curator, audiophile, and DJ.
A listener has shared how they are feeling or their current vibe:
"{mood}"

Analyze the emotional depth, acoustic texture, tempo, and vibe of this mood.
Then select {count} distinctive, high-quality songs that resonate deeply with this feeling.

Return your response in STRICT JSON format with this exact schema:
{{
  "vibe_headline": "A short, evocative 3-5 word phrase capturing the mood",
  "vibe_analysis": "1-2 sentences on the emotional and acoustic texture of this mood.",
  "songs": [
    {{
      "title": "Song Title",
      "artist": "Artist or Band Name",
      "reason": "1 vivid sentence explaining why this song specifically fits the mood and what sonic elements evoke it."
    }}
  ]
}}

Do not include any text before or after the JSON. Return only valid JSON.
"""

    parsed = None
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.get("message", {}).get("content", "")
        parsed = extract_json_from_text(content)
    except Exception as e:
        print(f"[MoodEngine] Ollama query failed ({e}); falling back to acoustic vault.")
        parsed = get_offline_vault_recommendation(mood, count=count)

    # Fallback parser if JSON parse failed
    if not parsed or not isinstance(parsed, dict) or "songs" not in parsed:
        parsed = get_offline_vault_recommendation(mood, count=count)

    # Enrich each song with Spotify metadata
    enriched_tracks = []
    for item in parsed.get("songs", []):
        title = item.get("title", "").strip('"\' ')
        artist = item.get("artist", "").strip('"\' ')
        reason = item.get("reason", "Curated for your vibe.")

        spotify_data = search_track(title, artist)
        enriched_tracks.append({
            "title": spotify_data.get("title", title),
            "artist": spotify_data.get("artist", artist),
            "album": spotify_data.get("album", "Vibe Curation"),
            "reason": reason,
            "spotify_url": spotify_data.get("spotify_url"),
            "image_url": spotify_data.get("image_url"),
            "preview_url": spotify_data.get("preview_url"),
            "popularity": spotify_data.get("popularity", 50),
            "source": spotify_data.get("source", "fallback")
        })

    return {
        "mood": mood,
        "vibe_headline": parsed.get("vibe_headline", f"Vibe: {mood.title()}"),
        "vibe_analysis": parsed.get("vibe_analysis", "Curated acoustic experience."),
        "tracks": enriched_tracks
    }
