"""
spotify_service.py — Spotify integration and search provider for MoodPlay.
Gracefully handles both authenticated API requests and offline/fallback search links.
"""

import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

_sp_client = None
_sp_initialized = False


def get_spotify_client():
    """Lazily initializes and returns the Spotipy client if credentials exist."""
    global _sp_client, _sp_initialized
    if _sp_initialized:
        return _sp_client

    _sp_initialized = True
    if not CLIENT_ID or not CLIENT_SECRET or "your_" in CLIENT_ID:
        return None

    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials

        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        _sp_client = spotipy.Spotify(auth_manager=auth_manager)
        return _sp_client
    except Exception as e:
        print(f"[SpotifyService] Initialization error: {e}")
        return None


def search_track(title: str, artist: str = ""):
    """
    Searches for a track. If Spotify API credentials are available,
    fetches live album art, track url, preview, and popularity.
    If not, returns a graceful fallback with direct web search link.
    """
    clean_query = f"{title} {artist}".strip()
    encoded_query = urllib.parse.quote(clean_query)
    fallback_spotify_url = f"https://open.spotify.com/search/{encoded_query}"

    sp = get_spotify_client()
    if not sp:
        return {
            "title": title,
            "artist": artist,
            "album": "Recommended by Gemma 3",
            "spotify_url": fallback_spotify_url,
            "image_url": None,
            "preview_url": None,
            "popularity": 80,
            "source": "fallback"
        }

    try:
        q = f'track:"{title}" {artist}'.strip() if artist else title
        results = sp.search(q=q, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])

        # Fallback to broader query if strict match returned nothing
        if not items:
            results = sp.search(q=clean_query, type="track", limit=1)
            items = results.get("tracks", {}).get("items", [])

        if items:
            track = items[0]
            artists_str = ", ".join(a.get("name") for a in track.get("artists", []))
            album_name = track.get("album", {}).get("name", "Unknown Album")
            spotify_url = track.get("external_urls", {}).get("spotify", fallback_spotify_url)
            images = track.get("album", {}).get("images", [])
            image_url = images[0].get("url") if images else None
            preview_url = track.get("preview_url")
            popularity = track.get("popularity", 50)

            return {
                "title": track.get("name", title),
                "artist": artists_str or artist,
                "album": album_name,
                "spotify_url": spotify_url,
                "image_url": image_url,
                "preview_url": preview_url,
                "popularity": popularity,
                "source": "spotify_api"
            }
    except Exception as e:
        print(f"[SpotifyService] Search error for '{clean_query}': {e}")

    return {
        "title": title,
        "artist": artist,
        "album": "Recommended by Gemma 3",
        "spotify_url": fallback_spotify_url,
        "image_url": None,
        "preview_url": None,
        "popularity": 75,
        "source": "fallback"
    }


def is_spotify_configured() -> bool:
    return bool(CLIENT_ID and CLIENT_SECRET and "your_" not in CLIENT_ID)
