"""
mood_engine.py — Genuine Audiophile Music Companion.
Curates music based on acoustic textures, analog warmth, and emotional landscapes.
Powered by local Gemma 3 with a rich offline acoustic vault fallback.
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
        "analysis": "A nocturnal landscape defined by warm brushwork on coated snare heads, melancholic horn voicings, and the woody acoustic resonance of an upright bass.",
        "songs": [
            {
                "title": "Autumn Leaves",
                "artist": "Bill Evans Trio",
                "reason": "Tender, contemplative piano phrasing with subtle brushed cymbals, recorded with intimate tape warmth.",
                "textures": ["Brushed Snare", "Upright Bass", "Acoustic Piano", "Tape Saturation"]
            },
            {
                "title": "'Round Midnight",
                "artist": "Thelonious Monk",
                "reason": "Atmospheric chord dissonance and spacious pauses that capture late-night solitude.",
                "textures": ["Monk Voicings", "Solo Piano", "Analog Warmth", "Nocturnal Pace"]
            },
            {
                "title": "Blue in Green",
                "artist": "Miles Davis",
                "reason": "Harmon-muted trumpet evoking still rain and midnight streetlamps.",
                "textures": ["Muted Trumpet", "Modal Harmony", "Minimalist Drums", "Room Reverb"]
            },
            {
                "title": "My Foolish Heart",
                "artist": "Bill Evans",
                "reason": "Impressionistic touch with gentle room ambiance and brushed drum accompaniment.",
                "textures": ["Impressionist Touch", "Subtle Cymbals", "Acoustic Trio", "Warm Velvet"]
            }
        ]
    },
    "rain": {
        "headline": "Raindrops on Glass & Soft Rhodes",
        "analysis": "Gentle acoustic resonance, muted reverb, and soothing downtempo cadences designed for watching gray skies from indoors.",
        "songs": [
            {
                "title": "Nuvole Bianche",
                "artist": "Ludovico Einaudi",
                "reason": "Gentle, cyclical piano progressions that echo the tempo of steady autumn rain.",
                "textures": ["Felted Piano", "Cyclical Melodies", "Spacious Reverb", "Introspective"]
            },
            {
                "title": "Coffee",
                "artist": "Tom Misch & Yussef Dayes",
                "reason": "Downtempo neo-soul groove with buttery warm guitar licks and live loose pocket drumming.",
                "textures": ["Rhodes 73", "Crisp Pocket Drums", "Warm Clean Guitar", "Vinyl Feel"]
            },
            {
                "title": "Gymnopédie No. 1",
                "artist": "Erik Satie",
                "reason": "Sparse, melancholy waltz cadence that clears mental clutter and lowers heart rate.",
                "textures": ["Acoustic Grand", "Impressionist Cadence", "Gentle Dynamics", "Subtle Tape Hiss"]
            },
            {
                "title": "Comptine d'un autre été",
                "artist": "Yann Tiersen",
                "reason": "Nostalgic piano and gentle accordions that carry the charm of European afternoon drizzle.",
                "textures": ["Intimate Upright", "Acoustic Accordion", "Nostalgic Waltz", "Crisp Resonance"]
            }
        ]
    },
    "focus": {
        "headline": "Kinetic Flow & Analog Harmonies",
        "analysis": "Non-intrusive rhythmic pulses, tape-saturated synths, and steady harmonic momentum to sustain deep creative focus.",
        "songs": [
            {
                "title": "Weightless",
                "artist": "Marconi Union",
                "reason": "Scientifically calibrated ambient frequencies, soft acoustic guitar strums, and calming 60-BPM pulse.",
                "textures": ["Ambient Drones", "Sub Bass", "Tape Echo", "60 BPM Pulse"]
            },
            {
                "title": "An Ending (Ascent)",
                "artist": "Brian Eno",
                "reason": "Expansive Yamaha DX7 textures that create a cathedral-like acoustic space in headphones.",
                "textures": ["Ethereal Pads", "Slow Attack Synths", "Deep Horizon", "Zero Friction"]
            },
            {
                "title": "Avril 14th",
                "artist": "Aphex Twin",
                "reason": "Pristine prepared piano with subtle mechanical hammer sounds that ground the listener.",
                "textures": ["Mechanical Piano", "Subtle Felt", "Clean Acoustics", "Delicate Touch"]
            },
            {
                "title": "Day One",
                "artist": "Hans Zimmer",
                "reason": "Stirring pipe organ swells and ticking tempo counterpoint that drives deep unbroken concentration.",
                "textures": ["Temple Organ", "Rhythmic Pulse", "Cinematic Reverb", "Dynamic Build"]
            }
        ]
    },
    "lavender": {
        "headline": "Lavender Dusk & Ethereal Shimmer",
        "analysis": "A dreamlike twilight atmosphere blending acoustic fingerpicking, dusty tape loops, and dreamy pale reverb.",
        "songs": [
            {
                "title": "Holocene",
                "artist": "Bon Iver",
                "reason": "Layered acoustic guitars, delicate glockenspiel chimes, and falsetto harmonies that feel like dusk over water.",
                "textures": ["Acoustic 12-String", "Glockenspiel", "Layered Choirs", "Tape Saturation"]
            },
            {
                "title": "Sunset Lover",
                "artist": "Petit Biscuit",
                "reason": "Soft guitar plucks, pitch-shifted vocal warmth, and gentle chilled percussion.",
                "textures": ["Warm Plucks", "Vocal Chops", "Subtle Shaker", "Pastel Ambient"]
            },
            {
                "title": "Between Friends",
                "artist": "Japanese Breakfast",
                "reason": "Dream-pop guitar chorus and lush reverb trails reflecting quiet twilight reflections.",
                "textures": ["Chorus Guitars", "Dream Pop", "Ethereal Vocals", "Silver Shimmer"]
            },
            {
                "title": "Mystery of Love",
                "artist": "Sufjan Stevens",
                "reason": "Intimate fingerpicked acoustic guitar, soft mandolin strums, and tender whispers.",
                "textures": ["Fingerstyle Guitar", "Mandolin", "Intimate Vocal", "Warm Wood"]
            }
        ]
    },
    "default": {
        "headline": "Acoustic Warmth & Organic Soul",
        "analysis": "An authentic audiophile journey blending uncompressed organic instrumentation, tube-saturated bass, and genuine melody.",
        "songs": [
            {
                "title": "Dreams",
                "artist": "Fleetwood Mac",
                "reason": "One of the most perfectly recorded rhythm sections in audio history; warm Fender Rhodes and crisp hi-hats.",
                "textures": ["Fender Rhodes", "Organic Bass", "Crisp Hi-Hat", "Pure 70s Analog"]
            },
            {
                "title": "Harvest Moon",
                "artist": "Neil Young",
                "reason": "Swept broom percussion, gentle acoustic guitar, and pedal steel guitar that breathes like a living room session.",
                "textures": ["Swept Brooms", "Pedal Steel", "Acoustic Warmth", "Intimate Strum"]
            },
            {
                "title": "Texas Sun",
                "artist": "Leon Bridges & Khruangbin",
                "reason": "Vintage Texas soul with warm vintage reverb, flatwound bass strings, and effortless groove.",
                "textures": ["Flatwound Bass", "Vintage Spring Reverb", "Soul Vocals", "Desert Groove"]
            },
            {
                "title": "Little Wing",
                "artist": "Jimi Hendrix",
                "reason": "Glittering clean Stratocaster through a Leslie rotating speaker cabinet paired with gentle glockenspiel.",
                "textures": ["Stratocaster", "Leslie Speaker", "Glockenspiel", "Tube Overdrive"]
            }
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

    if any(k in lower_mood for k in ["jazz", "night", "wine", "midnight", "brass", "sax", "monk", "smoky", "cellar"]):
        chosen_category = "jazz"
    elif any(k in lower_mood for k in ["rain", "storm", "lofi", "chill", "relax", "melanchol", "sad", "quiet", "cobblestone"]):
        chosen_category = "rain"
    elif any(k in lower_mood for k in ["focus", "study", "code", "work", "ambient", "read", "deep", "flow"]):
        chosen_category = "focus"
    elif any(k in lower_mood for k in ["lavender", "dusk", "sunset", "ethereal", "dream", "shimmer", "twilight", "cedar", "folk"]):
        chosen_category = "lavender"

    vault_entry = VAULT.get(chosen_category, VAULT["default"])
    return {
        "vibe_headline": vault_entry["headline"],
        "vibe_analysis": vault_entry["analysis"],
        "songs": vault_entry["songs"][:count]
    }


def get_music_recommendations(mood: str, count: int = 5):
    """
    Prompts local Gemma 3 for genuine audiophile music curation.
    If Ollama is offline or warming up, seamlessly falls back to acoustic vault.
    Enriches all tracks with Spotify artwork, preview audio, and links.
    """
    ensure_ollama_running()

    prompt = f"""You are a master record collector, audiophile, and acoustic curator for an analog vinyl archive.
A listener has described their current atmosphere, emotion, or room mood:
"{mood}"

Curate {count} real, remarkable songs that capture this mood with genuine sonic tactility, organic instrumentation, and acoustic warmth.
Avoid clichés and generic commercial filler.

Return your curation strictly in JSON format with this exact schema:
{{
  "vibe_headline": "3-5 word evocative title (e.g. 'Smoky Cedar & Muted Brass')",
  "vibe_analysis": "2 concise sentences on the acoustic textures, instrumentation, and emotional landscape of this mood.",
  "songs": [
    {{
      "title": "Song Title",
      "artist": "Artist Name",
      "reason": "1 vivid sentence explaining the instrumentation, warmth, and sonic resonance that makes this piece fit.",
      "textures": ["Texture 1", "Texture 2", "Texture 3"]
    }}
  ]
}}

Return ONLY valid JSON. No conversational preamble or postscript.
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
        print(f"[MoodEngine] Ollama query exception ({e}); using acoustic vault.")
        parsed = get_offline_vault_recommendation(mood, count=count)

    if not parsed or not isinstance(parsed, dict) or "songs" not in parsed:
        parsed = get_offline_vault_recommendation(mood, count=count)

    enriched_tracks = []
    for item in parsed.get("songs", []):
        title = item.get("title", "").strip('"\' ')
        artist = item.get("artist", "").strip('"\' ')
        reason = item.get("reason", "Curated for analog warmth.")
        textures = item.get("textures", ["Analog Warmth", "Acoustic Resonance", "Vinyl Texture"])

        spotify_data = search_track(title, artist)
        enriched_tracks.append({
            "title": spotify_data.get("title", title),
            "artist": spotify_data.get("artist", artist),
            "album": spotify_data.get("album", "Vinyl Archive"),
            "reason": reason,
            "textures": textures,
            "spotify_url": spotify_data.get("spotify_url"),
            "image_url": spotify_data.get("image_url"),
            "preview_url": spotify_data.get("preview_url"),
            "popularity": spotify_data.get("popularity", 50),
            "source": spotify_data.get("source", "fallback")
        })

    return {
        "mood": mood,
        "vibe_headline": parsed.get("vibe_headline", f"Liner Notes: {mood.title()}"),
        "vibe_analysis": parsed.get("vibe_analysis", "Curated with analog depth and acoustic warmth."),
        "tracks": enriched_tracks
    }
