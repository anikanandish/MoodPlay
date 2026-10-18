"""
spotify_test.py — Standalone verification script for Spotify search in MoodPlay.

This uses Spotify's Client Credentials flow (no browser login required).
To run:
  1. Copy .env.example to .env
  2. Add your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
  3. Run: python spotify_test.py
"""

import os
import sys
from dotenv import load_dotenv

# Ensure utf-8 output on Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")


def search_track(query: str, limit: int = 1):
    """Searches Spotify for a track and returns details."""
    if not CLIENT_ID or not CLIENT_SECRET or CLIENT_ID == "your_spotify_client_id_here":
        print("⚠️  Spotify credentials missing or using placeholder!")
        print("   Please create a .env file and set:")
        print("   SPOTIPY_CLIENT_ID=your_id")
        print("   SPOTIPY_CLIENT_SECRET=your_secret")
        print("   Get them at: https://developer.spotify.com/dashboard")
        return None

    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials

        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        results = sp.search(q=query, type='track', limit=limit)
        items = results.get('tracks', {}).get('items', [])

        if not items:
            print(f"❌ No tracks found on Spotify for query: '{query}'")
            return None

        track = items[0]
        title = track.get('name')
        artists = ", ".join(a.get('name') for a in track.get('artists', []))
        album = track.get('album', {}).get('name', 'Unknown Album')
        spotify_url = track.get('external_urls', {}).get('spotify', '')
        images = track.get('album', {}).get('images', [])
        image_url = images[0].get('url') if images else None
        preview_url = track.get('preview_url')
        popularity = track.get('popularity', 0)

        info = {
            "title": title,
            "artists": artists,
            "album": album,
            "spotify_url": spotify_url,
            "image_url": image_url,
            "preview_url": preview_url,
            "popularity": popularity,
        }
        return info

    except Exception as e:
        print(f"❌ Error communicating with Spotify API: {e}")
        return None


def main():
    print("=" * 60)
    print("🎵 MoodPlay — Spotify Search Test")
    print("=" * 60)

    test_query = sys.argv[1] if len(sys.argv) > 1 else "Autumn Leaves Bill Evans"
    print(f"Searching for: \"{test_query}\"...\n")

    track_info = search_track(test_query)

    if track_info:
        print("✅ Spotify Connection & Search Successful!")
        print("-" * 60)
        print(f"🎵 Title:       {track_info['title']}")
        print(f"👤 Artist(s):   {track_info['artists']}")
        print(f"💿 Album:       {track_info['album']}")
        print(f"🔗 Spotify URL: {track_info['spotify_url']}")
        print(f"🖼️ Cover Image: {track_info['image_url']}")
        print(f"⭐ Popularity:  {track_info['popularity']}/100")
        print("-" * 60)
    else:
        print("\nTest failed or credentials missing.")


if __name__ == "__main__":
    main()
