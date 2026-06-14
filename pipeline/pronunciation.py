"""
Simplified phonetic transcription for English words, based on the CMU
Pronouncing Dictionary (via the `pronouncing` library).

Example: "knight" -> ARPAbet "N AY1 T" -> simplified "nait"

Usage:
  python3 pipeline/pronunciation.py knight thinking school
"""

from __future__ import annotations

import re

import pronouncing

# ARPAbet phoneme (without stress markers) -> simplified phonetic spelling
# Reference: https://en.wikipedia.org/wiki/ARPABET
ARPABET_TO_SIMPLE = {
    "AA": "ah", "AE": "a", "AH": "uh", "AO": "aw", "AW": "ow",
    "AY": "ai", "B": "b", "CH": "ch", "D": "d", "DH": "th",
    "EH": "eh", "ER": "er", "EY": "ay", "F": "f", "G": "g",
    "HH": "h", "IH": "i", "IY": "ee", "JH": "j", "K": "k",
    "L": "l", "M": "m", "N": "n", "NG": "ng", "OW": "oh",
    "OY": "oy", "P": "p", "R": "r", "S": "s", "SH": "sh",
    "T": "t", "TH": "th", "UH": "u", "UW": "oo", "V": "v",
    "W": "w", "Y": "y", "Z": "z", "ZH": "zh",
}

STRESS_RE = re.compile(r"\d")  # strips stress markers (0, 1, 2)


def get_arpabet(word: str) -> str | None:
    """Returns the first available ARPAbet transcription for the word, or None."""
    phones = pronouncing.phones_for_word(word.lower())
    return phones[0] if phones else None


def simplify_pronunciation(word: str) -> str | None:
    """
    Returns a simplified, readable phonetic spelling of the word.
    E.g. "knight" -> "nait", "thinking" -> "thinkin"
    Returns None if the word is not in the CMU dictionary.
    """
    arpabet = get_arpabet(word)
    if not arpabet:
        return None

    phonemes = [STRESS_RE.sub("", p) for p in arpabet.split()]
    simplified = "".join(ARPABET_TO_SIMPLE.get(p, "") for p in phonemes)

    return simplified


def annotate_words(words: list[str]) -> dict[str, str | None]:
    """Returns {word: simplified_pronunciation} for a list of words."""
    return {word: simplify_pronunciation(word) for word in words}


if __name__ == "__main__":
    import sys
    import json

    words = sys.argv[1:] or ["knight", "thinking", "school", "through", "castle"]
    print(json.dumps(annotate_words(words), indent=2, ensure_ascii=False))
