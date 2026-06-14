"""
Client per Lalal.ai API: separa una traccia audio in voce / strumentale.

Setup:
  1. pip install requests python-dotenv
  2. Aggiungi al file .env nella root del progetto:
       LALAL_API_KEY=la_tua_license_key
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
            "LALAL_API_KEY non configurata.\n"
            "Aggiungi al file .env: LALAL_API_KEY=la_tua_license_key"
        )

    headers = {"X-License-Key": API_KEY}
    if extra:
        headers.update(extra)
    return headers


def upload_audio(file_path: str) -> str:
    """Carica un file audio e restituisce il source_id."""
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
        raise RuntimeError(f"Errore upload Lalal.ai: {data}")

    return data["id"]


def split_stems(source_id: str, stem: str = "vocals") -> str:
    """Avvia la separazione in stem (es. 'vocals' o 'instrum'). Restituisce il task_id."""
    response = requests.post(
        f"{BASE_URL}/split/stem_separator/",
        headers=_headers({"Content-Type": "application/json"}),
        json={"source_id": source_id, "presets": {"stem": stem}},
    )

    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError(f"Errore split Lalal.ai: {data}")

    return data["task_id"]


def check_result(task_id: str) -> dict:
    """Controlla lo stato di un task. Restituisce il dict di stato di Lalal.ai."""
    response = requests.post(
        f"{BASE_URL}/check/",
        headers=_headers({"Content-Type": "application/json"}),
        json={"task_ids": [task_id]},
    )

    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError(f"Errore check Lalal.ai: {data}")

    return data["result"][task_id]


def separate_track(file_path: str, stem: str = "vocals", poll_interval: int = 5, timeout: int = 300) -> dict:
    """
    Pipeline completa: upload -> split -> polling fino al completamento.
    Restituisce gli URL di download per voce (vocals_url) e strumentale (instrumental_url).
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
            raise RuntimeError(f"Separazione Lalal.ai {status}: {task}")

        time.sleep(poll_interval)
        elapsed += poll_interval

    raise TimeoutError(f"Separazione non completata entro {timeout} secondi")


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("Uso: python clients/lalal_client.py <path_audio>")
        sys.exit(1)

    try:
        result = separate_track(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (RuntimeError, TimeoutError) as e:
        print(f"❌ Errore: {e}", file=sys.stderr)
        sys.exit(1)
