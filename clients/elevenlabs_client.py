"""
ElevenLabs API client: TTS + time alignment for synchronized highlighting.

Setup:
  1. pip install elevenlabs python-dotenv
  2. Make sure .env contains: ELEVENLABS_API_KEY=...
  3. python clients/elevenlabs_client.py "Text to read"
"""

from __future__ import annotations

import base64
import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # default voice (George)
DEFAULT_MODEL_ID = "eleven_multilingual_v2"


def _client() -> ElevenLabs:
    if not API_KEY:
        raise RuntimeError(
            "ELEVENLABS_API_KEY not configured.\n"
            "Add to the .env file: ELEVENLABS_API_KEY=your_key"
        )
    return ElevenLabs(api_key=API_KEY)


def text_to_speech(text: str, voice_id: str = DEFAULT_VOICE_ID, output_path: str = "output/tts.mp3") -> str:
    """Generates TTS audio and saves it to a file. Returns the file path."""
    client = _client()

    audio = client.text_to_speech.convert(
        voice_id,
        text=text,
        model_id=DEFAULT_MODEL_ID,
        output_format="mp3_44100_128",
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return output_path


def text_to_speech_with_timestamps(text: str, voice_id: str = DEFAULT_VOICE_ID, output_path: str = "output/tts.mp3") -> dict:
    """
    Generates TTS audio with character-level time alignment.
    Returns {"audio_path": ..., "alignment": {...}}.
    """
    client = _client()

    result = client.text_to_speech.convert_with_timestamps(
        voice_id,
        text=text,
        model_id=DEFAULT_MODEL_ID,
        output_format="mp3_44100_128",
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    audio_bytes = base64.b64decode(result.audio_base_64)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    alignment = {
        "characters": result.alignment.characters,
        "character_start_times_seconds": result.alignment.character_start_times_seconds,
        "character_end_times_seconds": result.alignment.character_end_times_seconds,
    }

    return {"audio_path": output_path, "alignment": alignment}


def clone_voice(name: str, audio_bytes: bytes, filename: str = "sample.webm") -> str:
    """
    Clones a voice from a short audio recording (Instant Voice Cloning).
    Returns the new voice_id.
    """
    client = _client()

    voice = client.voices.ivc.create(
        name=name,
        files=[(filename, audio_bytes)],
    )

    return voice.voice_id


def speech_to_text(audio_bytes: bytes, filename: str = "recording.webm") -> str:
    """
    Transcribes a short audio recording to text using ElevenLabs Scribe.
    Returns the transcribed text.
    """
    client = _client()

    result = client.speech_to_text.convert(
        model_id="scribe_v1",
        file=(filename, audio_bytes),
    )

    return result.text


def group_words_with_timestamps(alignment: dict) -> list[dict]:
    """
    Groups character-level alignment into words with start/end times.
    Returns: [{"word": "Hello", "start": 0.0, "end": 0.4, "breaks_after": 0}, ...]
    "breaks_after" counts line breaks ("\\n") following the word, so the
    original line structure of the lyrics can be reproduced.
    """
    characters = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]

    words = []
    current_word = ""
    word_start = None

    for char, start, end in zip(characters, starts, ends):
        if char.strip() == "":
            if current_word:
                words.append({"word": current_word, "start": word_start, "end": prev_end, "breaks_after": 0})
                current_word = ""
                word_start = None
            if char == "\n" and words:
                words[-1]["breaks_after"] += 1
            continue

        if not current_word:
            word_start = start

        current_word += char
        prev_end = end

    if current_word:
        words.append({"word": current_word, "start": word_start, "end": prev_end, "breaks_after": 0})

    return words


if __name__ == "__main__":
    import sys
    import json

    text = sys.argv[1] if len(sys.argv) > 1 else "The first move is what sets everything in motion."

    print(f"Generating TTS with timestamps for: {text!r}\n")

    result = text_to_speech_with_timestamps(text, output_path="output/tts_with_timestamps.mp3")
    words = group_words_with_timestamps(result["alignment"])

    print(f"Audio saved to: {result['audio_path']}\n")
    print("Words with timestamps:")
    for w in words:
        print(f"  {w['word']!r}: {w['start']:.2f}s - {w['end']:.2f}s")

    with open("output/words_alignment.json", "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2, ensure_ascii=False)
    print("\nAlso saved to output/words_alignment.json")
