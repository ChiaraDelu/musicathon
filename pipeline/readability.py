"""
Computes a DSA-oriented readability score for English lyrics:
  - base: Flesch Reading Ease
  - penalties: difficult consonant clusters, long words, rare words

Usage:
  python3 pipeline/readability.py "song lyrics..."
"""

from __future__ import annotations

import re

import pyphen
from markupsafe import Markup, escape

_dic = pyphen.Pyphen(lang="en_US")

WORD_RE = re.compile(r"[a-zA-Z']+")
SENTENCE_SPLIT_RE = re.compile(r"[.!?\n]+")

# Consonant clusters/digraphs notoriously difficult for dyslexia (English)
DIFFICULT_CLUSTER_RE = re.compile(
    r"th|sh|ch|wr|kn|ph|gh|str|spl|scr|spr|shr|thr|squ", re.IGNORECASE
)

# List of common English words (elementary school level), used as a proxy for "word frequency"
COMMON_WORDS = {
    "a", "about", "after", "again", "all", "always", "am", "an", "and", "any",
    "are", "around", "as", "ask", "at", "away", "be", "because", "been",
    "before", "best", "better", "big", "black", "blue", "both", "bring",
    "but", "buy", "by", "call", "came", "can", "carry", "clean", "come",
    "could", "cut", "day", "did", "do", "does", "done", "down", "draw",
    "drink", "eat", "every", "fall", "far", "fast", "find", "first", "fly",
    "for", "found", "from", "full", "funny", "give", "go", "going", "good",
    "got", "green", "grow", "had", "has", "have", "he", "help", "her", "here",
    "him", "his", "hold", "hot", "how", "hurt", "i", "if", "in", "into", "is",
    "it", "its", "jump", "just", "keep", "kind", "know", "laugh", "let",
    "light", "like", "little", "live", "long", "look", "love", "made", "make",
    "many", "may", "me", "more", "most", "much", "must", "my", "myself",
    "never", "new", "no", "not", "now", "of", "off", "old", "on", "once",
    "one", "only", "open", "or", "our", "out", "over", "own", "people",
    "play", "please", "pretty", "pull", "put", "ran", "read", "red", "ride",
    "right", "round", "run", "said", "saw", "say", "see", "seven", "shall",
    "she", "show", "sing", "sit", "six", "sleep", "small", "so", "some",
    "soon", "start", "stop", "take", "tell", "ten", "thank", "that", "the",
    "their", "them", "then", "there", "these", "think", "this", "those",
    "three", "to", "today", "together", "too", "try", "two", "under", "up",
    "upon", "us", "use", "very", "walk", "want", "warm", "was", "wash", "we",
    "well", "went", "were", "what", "when", "where", "which", "white", "who",
    "why", "will", "wish", "with", "work", "would", "write", "yellow", "yes",
    "you", "your", "time", "back", "world", "way", "day", "man", "thing",
    "woman", "life", "child", "night", "eye", "head", "hand", "heart", "feel",
    "let it go", "rain", "sun", "sky", "fly", "free", "girl", "boy", "song",
    "music", "dance", "dream", "story", "true", "real", "still", "every",
}


def count_syllables(word: str) -> int:
    hyphenated = _dic.inserted(word)
    return max(1, hyphenated.count("-") + 1)


def flesch_reading_ease(text: str) -> float:
    words = WORD_RE.findall(text)
    sentences = [s for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]

    n_words = len(words)
    n_sentences = max(1, len(sentences))

    if n_words == 0:
        return 0.0

    n_syllables = sum(count_syllables(w) for w in words)

    return 206.835 - 1.015 * (n_words / n_sentences) - 84.6 * (n_syllables / n_words)


def _to_dsa_level(score: float) -> int:
    """Converts a 0-100 score into a level from 1 (hard) to 5 (easy)."""
    if score >= 80:
        return 5
    if score >= 60:
        return 4
    if score >= 40:
        return 3
    if score >= 20:
        return 2
    return 1


def analyze(text: str) -> dict:
    """
    Analyzes the lyrics and returns a full report: score, DSA level,
    and difficult words (with consonant clusters or >3 syllables).
    """
    words = WORD_RE.findall(text)
    n_words = len(words)

    if n_words == 0:
        return {"dsa_score": 0.0, "dsa_level": 1, "difficult_words": []}

    flesch = flesch_reading_ease(text)

    pct_cluster = sum(1 for w in words if DIFFICULT_CLUSTER_RE.search(w)) / n_words * 100
    pct_long = sum(1 for w in words if count_syllables(w) > 3) / n_words * 100
    pct_rare = sum(1 for w in words if w.lower() not in COMMON_WORDS) / n_words * 100

    dsa_score = flesch - 0.5 * pct_cluster - 0.4 * pct_long - 0.3 * pct_rare
    dsa_score = max(0.0, min(100.0, dsa_score))

    difficult_words = sorted({
        w for w in words
        if DIFFICULT_CLUSTER_RE.search(w) or count_syllables(w) > 3 or w.lower() not in COMMON_WORDS
    }, key=str.lower)

    return {
        "flesch_score": round(flesch, 1),
        "dsa_score": round(dsa_score, 1),
        "dsa_level": _to_dsa_level(dsa_score),
        "pct_difficult_clusters": round(pct_cluster, 1),
        "pct_long_words": round(pct_long, 1),
        "pct_rare_words": round(pct_rare, 1),
        "difficult_words": difficult_words,
    }


def mark_difficult_sounds(word: str) -> Markup:
    """
    Wraps difficult consonant clusters/digraphs (e.g. "th", "scr") in
    <span class="difficult-sound"> so they can be highlighted in red.
    """
    pieces = []
    last_end = 0

    for match in DIFFICULT_CLUSTER_RE.finditer(word):
        pieces.append(escape(word[last_end:match.start()]))
        pieces.append(Markup('<span class="difficult-sound">') + escape(match.group()) + Markup("</span>"))
        last_end = match.end()

    pieces.append(escape(word[last_end:]))
    return Markup("").join(pieces)


if __name__ == "__main__":
    import sys
    import json

    text = sys.argv[1] if len(sys.argv) > 1 else (
        "Let it go, let it go, can't hold it back anymore"
    )

    print(json.dumps(analyze(text), indent=2, ensure_ascii=False))
