"""
Musixmatch API client: fetches lyrics + AI analysis (meaning, moods, themes, entities).

Setup:
  1. pip install requests python-dotenv
  2. Create a .env file in the project root with:
       MUSIXMATCH_API_KEY=your_api_key
  3. python musixmatch_client.py "Artist Name" "Song Title"
"""

from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("MUSIXMATCH_API_KEY")
BASE_URL = "https://api.musixmatch.com/ws/1.1"

# TODO: update with the exact Musixmatch AI API endpoint (analysis: meaning/moods/themes/entities)
# once full documentation access is available.
AI_ANALYSIS_ENDPOINT = f"{BASE_URL}/track.lyrics.ai.get"


def _get(endpoint: str, params: dict) -> dict:
    if not API_KEY:
        raise RuntimeError(
            "MUSIXMATCH_API_KEY not configured.\n"
            "Create a .env file in the project root with:\n"
            "  MUSIXMATCH_API_KEY=your_api_key\n"
            "Get your key from: https://developer.musixmatch.com/"
        )

    params["apikey"] = API_KEY
    response = requests.get(endpoint, params=params)

    data = response.json()
    status_code = data.get("message", {}).get("header", {}).get("status_code")

    if status_code == 401:
        raise RuntimeError(
            "MUSIXMATCH_API_KEY invalid or expired.\n"
            "Check the .env file and the API key from: https://developer.musixmatch.com/"
        )
    elif status_code and status_code >= 400:
        raise RuntimeError(f"Musixmatch API error (status {status_code}): {data}")

    return data


def search_track(artist: str, title: str) -> dict | None:
    """Searches for a track and returns track_id + basic metadata."""
    data = _get(f"{BASE_URL}/track.search", {
        "q_artist": artist,
        "q_track": title,
        "page_size": 1,
        "s_track_rating": "desc",
    })

    track_list = data["message"]["body"]["track_list"]
    if not track_list:
        return None

    track = track_list[0]["track"]
    return {
        "track_id": track["track_id"],
        "artist_name": track["artist_name"],
        "track_name": track["track_name"],
        "has_lyrics": track["has_lyrics"],
    }


def get_lyrics(track_id: int) -> str | None:
    """Returns the song's lyrics."""
    data = _get(f"{BASE_URL}/track.lyrics.get", {"track_id": track_id})
    body = data["message"]["body"]

    if not body.get("lyrics"):
        return None

    return body["lyrics"]["lyrics_body"]


def get_ai_analysis(track_id: int) -> dict:
    """
    Returns the AI analysis of the lyrics: meaning, moods, themes, entities, rating.
    Expected structure (see api-example): message.body.analysis.{meaning, moods, themes, entities, rating, ...}
    """
    data = _get(AI_ANALYSIS_ENDPOINT, {"track_id": track_id})
    return data["message"]["body"]["analysis"]


def extract_variables(artist: str, title: str) -> dict:
    """Full pipeline: searches for the track and extracts all variables useful for the project."""
    track = search_track(artist, title)
    if not track:
        raise ValueError(f"No track found for {artist} - {title}")

    if not track["has_lyrics"]:
        raise ValueError(f"No lyrics available for {artist} - {title}")

    track_id = track["track_id"]
    lyrics = get_lyrics(track_id)
    analysis = get_ai_analysis(track_id)

    return {
        "artist": track["artist_name"],
        "title": track["track_name"],
        "lyrics": lyrics,
        "meaning": analysis.get("meaning", {}).get("explanation"),
        "moods": analysis.get("moods", {}).get("main_moods", []),
        "themes": [t["theme"] for t in analysis.get("themes", {}).get("main_themes", [])],
        "entities": [e["entity_name"] for e in analysis.get("entities", {}).get("entity_list", [])],
        "rating": analysis.get("rating", {}).get("audience"),
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 3:
        print("Usage: python musixmatch_client.py <artist> <title>")
        sys.exit(1)

    try:
        artist, title = sys.argv[1], sys.argv[2]
        result = extract_variables(artist, title)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
