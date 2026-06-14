"""
Lalal.ai API client: splits an audio track into vocals / instrumental.

Setup:
  1. pip install requests python-dotenv
  2. Add to the .env file in the project root:
       LALAL_API_KEY=your_license_key
  3. python clients/lalal_client.py path/to/song.mp3
"""

from __future__ import annotations

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("LALAL_API_KEY")
BASE_URL = "https://www.lalal.ai/api/v1"


def _headers(extra: dict | None = None) -> dict:
    if not API_KEY:
        raise RuntimeError(
            "LALAL_API_KEY not configured.\n"
            "Add to the .env file: LALAL_API_KEY=your_license_key"
        )

    headers = {"X-License-Key": API_KEY}
    if extra:
        headers.update(extra)
    return headers


def upload_audio(file_path: str) -> str:
    """Uploads an audio file and returns the source_id."""
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload/",
            headers=_headers({"Content-Disposition": f"attachment; filename={filename}"}),
            data=f.read(),
        )

    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError(f"Lalal.ai upload error: {data}")

    return data["id"]


def split_stems(source_id: str, stem: str = "vocals") -> str:
    """Starts stem separation (e.g. 'vocals' or 'instrum'). Returns the task_id."""
    response = requests.post(
        f"{BASE_URL}/split/stem_separator/",
        headers=_headers({"Content-Type": "application/json"}),
        json={"source_id": source_id, "presets": {"stem": stem}},
    )

    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError(f"Lalal.ai split error: {data}")

    return data["task_id"]


def check_result(task_id: str) -> dict:
    """Checks the status of a task. Returns Lalal.ai's status dict."""
    response = requests.post(
        f"{BASE_URL}/check/",
        headers=_headers({"Content-Type": "application/json"}),
        json={"task_ids": [task_id]},
    )

    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError(f"Lalal.ai check error: {data}")

    return data["result"][task_id]


def separate_track(file_path: str, stem: str = "vocals", poll_interval: int = 5, timeout: int = 300) -> dict:
    """
    Full pipeline: upload -> split -> poll until completion.
    Returns the download URLs for vocals (vocals_url) and instrumental (instrumental_url).
    """
    source_id = upload_audio(file_path)
    task_id = split_stems(source_id, stem=stem)

    elapsed = 0
    while elapsed < timeout:
        task = check_result(task_id)
        status = task.get("status")

        if status == "success":
            tracks = task["result"]["tracks"]
            urls = {}
            for track in tracks:
                if track["label"] == "vocals":
                    urls["vocals_url"] = track["url"]
                elif track["label"] == "no_vocals":
                    urls["instrumental_url"] = track["url"]
            return urls
        elif status in ("error", "cancelled"):
            raise RuntimeError(f"Lalal.ai separation {status}: {task}")

        time.sleep(poll_interval)
        elapsed += poll_interval

    raise TimeoutError(f"Separation not completed within {timeout} seconds")


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Usage: python clients/lalal_client.py <audio_path>")
        sys.exit(1)

    try:
        result = separate_track(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (RuntimeError, TimeoutError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
