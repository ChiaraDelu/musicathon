"""
Checks whether a spoken word matches a target word, using the
transcription from speech-to-text plus a phonetic fallback (so close
pronunciations spelled differently by the ASR still count as correct).

Usage:
  python3 -m pipeline.pronunciation_check castle "castle"
"""

from __future__ import annotations

import re

from pipeline.pronunciation import simplify_pronunciation

WORD_RE = re.compile(r"[a-zA-Z']+")


def _normalize(text: str) -> str:
    return text.strip().lower().strip("'\".,!?")


def check_pronunciation(target_word: str, transcript: str) -> dict:
    """
    Compares the target word with the transcribed speech.
    Returns {"correct": bool, "target": ..., "transcript": ...}.
    """
    target = _normalize(target_word)
    heard_words = [_normalize(w) for w in WORD_RE.findall(transcript)]

    if target in heard_words:
        return {"correct": True, "target": target_word, "transcript": transcript}

    target_sound = simplify_pronunciation(target)
    if target_sound:
        for word in heard_words:
            if simplify_pronunciation(word) == target_sound:
                return {"correct": True, "target": target_word, "transcript": transcript}

    return {"correct": False, "target": target_word, "transcript": transcript}


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 3:
        print("Usage: python3 -m pipeline.pronunciation_check <target_word> <transcript>")
        sys.exit(1)

    print(json.dumps(check_pronunciation(sys.argv[1], sys.argv[2]), indent=2))
