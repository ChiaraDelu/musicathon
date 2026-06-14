"""
Extracts the chorus from song lyrics using a simple repetition heuristic:
the chorus is the stanza (block of lines separated by a blank line) that
appears more than once in the lyrics.

Usage:
  python3 pipeline/chorus.py path/to/lyrics.txt
"""

from __future__ import annotations

import re

BLOCK_SPLIT_RE = re.compile(r"\n\s*\n")


def _normalize(block: str) -> str:
    lines = [line.strip().lower() for line in block.splitlines() if line.strip()]
    return "\n".join(lines)


def extract_chorus(lyrics: str) -> str:
    """
    Returns the chorus of the song: the first stanza that repeats elsewhere
    in the lyrics. Falls back to the first stanza if no repetition is found.
    """
    blocks = [b.strip() for b in BLOCK_SPLIT_RE.split(lyrics) if b.strip()]
    if not blocks:
        return lyrics.strip()

    seen: dict[str, str] = {}
    for block in blocks:
        key = _normalize(block)
        if key in seen:
            return seen[key]
        seen[key] = block

    return blocks[0]


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 pipeline/chorus.py <lyrics_file>")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()

    print(extract_chorus(text))
