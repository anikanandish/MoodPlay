"""
mood_engine.py — Core AI mood understanding powered by local Gemma 3 via Ollama.
"""

import json
import re
import ollama
from spotify_service import search_track

MODEL_NAME = "gemma3"


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
    # Check for ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try finding the first '{' and last '}'
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start:end+1]
        try:
            return json.loads(snippet)
        except Exception:
            pass

    return None


def get_music_recommendations(mood: str, count: int = 5):
    """
    Prompts local Gemma 3 to analyze the user's mood and return structured tracks.
    Then enriches each track with Spotify metadata (artwork, link, preview).
    """
    prompt = f"""You are an elite music curator, audiophile, and DJ.
A listener has shared how they are feeling or their current vibe:
"{mood}"

Analyze the emotional depth, acoustic texture, tempo, and vibe of this mood.
Then select {count} distinctive, high-quality songs that resonate deeply with this feeling.

Return your response in STRICT JSON format with this exact schema:
{{
  "vibe_headline": "A short, evocative 3-5 word phrase capturing the mood (e.g. 'Midnight Rain & Warm Brass')",
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

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.get("message", {}).get("content", "")
    parsed = extract_json_from_text(content)

    # Fallback parser if JSON parse failed (e.g. if the model output bullet points)
    if not parsed or not isinstance(parsed, dict) or "songs" not in parsed:
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        songs = []
        for line in lines:
            if line.startswith(("-", "*", "🎵", "1", "2", "3", "4", "5")):
                # Strip leading marker
                clean = re.sub(r"^[-*🎵\d\.\s]+", "", line).strip()
                if " - " in clean:
                    parts = clean.split(" - ", 1)
                    songs.append({"title": parts[0].strip(), "artist": parts[1].strip(), "reason": "Curated for your vibe."})
                elif " by " in clean:
                    parts = clean.split(" by ", 1)
                    songs.append({"title": parts[0].strip(), "artist": parts[1].strip(), "reason": "Curated for your vibe."})
        parsed = {
            "vibe_headline": f"Vibe: {mood.capitalize()}",
            "vibe_analysis": f"Music specially tuned to reflect '{mood}'.",
            "songs": songs[:count] or [
                {"title": "Weightless", "artist": "Marconi Union", "reason": "Atmospheric soundscapes."},
                {"title": "Clair de Lune", "artist": "Claude Debussy", "reason": "Mellow piano reflections."}
            ]
        }

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
