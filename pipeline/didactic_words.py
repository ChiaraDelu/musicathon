"""
Genera un subset didattico di parole inglesi organizzate per pattern
fonologico/ortografico utile per esercizi DSA:
  - lettere mute (silent letters)
  - cluster consonantici (consonant clusters)

Uso:
  python3 pipeline/didactic_words.py
  -> scrive pipeline/didactic_words.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# Lista di parole comuni inglesi (livello scuola primaria/secondaria),
# scelta per coprire i pattern target senza termini troppo rari.
COMMON_WORDS = [
    # silent k (kn-)
    "knight", "know", "knee", "knife", "knock", "knit", "knot", "knob",
    # silent w (wr-)
    "write", "wrong", "wrist", "wrap", "wreck", "wrestle", "wrinkle",
    # silent g (gn-)
    "gnome", "gnat", "gnaw", "sign", "design", "campaign", "reign",
    # silent b (-mb)
    "climb", "comb", "lamb", "limb", "thumb", "crumb", "bomb",
    # silent gh
    "light", "night", "right", "sight", "tight", "fight", "high", "though",
    # silent n (-mn)
    "autumn", "hymn", "column",
    # silent t
    "castle", "listen", "whistle", "fasten", "often",
    # silent h
    "ghost", "honest", "hour", "whale", "white", "where", "when", "why",
    # consonant clusters: str-
    "street", "strong", "string", "straw", "stripe", "strange", "struggle",
    # consonant clusters: spl-
    "split", "splash", "splendid", "splinter",
    # consonant clusters: scr-
    "scream", "script", "scrap", "scratch", "screen", "scrub",
    # consonant clusters: spr-
    "spring", "sprout", "spray", "sprint", "spread",
    # consonant clusters: shr-
    "shrink", "shrimp", "shrug", "shred", "shrub",
    # consonant clusters: thr-
    "three", "throw", "throne", "throat", "thrill", "thread", "thrive",
    # consonant clusters: squ-
    "square", "squad", "squash", "squeeze", "squirrel", "squint",
]


# Pattern per LETTERE MUTE: (categoria -> regex sulla forma scritta)
SILENT_LETTER_PATTERNS = {
    "silent_k_kn": re.compile(r"^kn"),
    "silent_w_wr": re.compile(r"^wr"),
    "silent_g_gn": re.compile(r"^gn|ign$|eign"),
    "silent_b_mb": re.compile(r"mb$"),
    "silent_gh": re.compile(r"igh|ough$"),
    "silent_n_mn": re.compile(r"mn$"),
    "silent_t_listen": re.compile(r"stle|sten"),
    "silent_h_wh": re.compile(r"^wh|^gh|^h(?=our)"),
}

# Pattern per CLUSTER CONSONANTICI iniziali: (categoria -> regex)
CONSONANT_CLUSTER_PATTERNS = {
    "cluster_str": re.compile(r"^str"),
    "cluster_spl": re.compile(r"^spl"),
    "cluster_scr": re.compile(r"^scr"),
    "cluster_spr": re.compile(r"^spr"),
    "cluster_shr": re.compile(r"^shr"),
    "cluster_thr": re.compile(r"^thr"),
    "cluster_squ": re.compile(r"^squ"),
}


def classify_word(word: str) -> list[str]:
    """Restituisce tutte le categorie (pattern) a cui appartiene una parola."""
    categories = []
    for name, pattern in SILENT_LETTER_PATTERNS.items():
        if pattern.search(word):
            categories.append(name)
    for name, pattern in CONSONANT_CLUSTER_PATTERNS.items():
        if pattern.search(word):
            categories.append(name)
    return categories


def build_subset(words: list[str]) -> dict[str, list[str]]:
    """Raggruppa le parole per categoria di pattern fonologico/ortografico."""
    subset: dict[str, list[str]] = {}
    for word in words:
        for category in classify_word(word):
            subset.setdefault(category, []).append(word)
    return subset


if __name__ == "__main__":
    result = build_subset(COMMON_WORDS)

    output_path = Path(__file__).parent / "didactic_words.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Subset didattico salvato in {output_path}\n")
    for category, words in result.items():
        print(f"{category}: {', '.join(words)}")
