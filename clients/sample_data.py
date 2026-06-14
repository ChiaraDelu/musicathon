"""
Sample data used as a fallback when MUSIXMATCH_API_KEY is not yet
configured, so the rest of the pipeline (TTS, readability,
pronunciation, highlighting) can be tested without the API key.
"""

from __future__ import annotations

SAMPLE_TRACK = {
    "artist": "Idina Menzel",
    "title": "Let It Go (demo)",
    "lyrics": (
        "The snow glows white on the mountain tonight\n"
        "Not a footprint to be seen\n"
        "A kingdom of isolation\n"
        "And it looks like I'm the queen\n"
        "\n"
        "Let it go, let it go\n"
        "Can't hold it back anymore\n"
        "Let it go, let it go\n"
        "Turn away and slam the door\n"
        "\n"
        "It's funny how some distance\n"
        "Makes everything seem small\n"
        "\n"
        "Let it go, let it go\n"
        "Can't hold it back anymore\n"
        "Let it go, let it go\n"
        "Turn away and slam the door"
    ),
    "meaning": "A song about letting go of fear and accepting yourself (sample data).",
    "moods": ["empowering", "emotional", "uplifting"],
    "themes": ["self-acceptance", "freedom"],
    "entities": [],
    "rating": None,
}
