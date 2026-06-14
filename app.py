import os

from flask import Flask, render_template, request, redirect, url_for, session

from clients.musixmatch_client import extract_variables
from clients.sample_data import SAMPLE_TRACK
from clients.elevenlabs_client import (
    text_to_speech_with_timestamps,
    group_words_with_timestamps,
    clone_voice,
    speech_to_text,
    DEFAULT_VOICE_ID,
)
from pipeline.readability import analyze as analyze_readability, mark_difficult_sounds
from pipeline.pronunciation import annotate_words
from pipeline.chorus import extract_chorus
from pipeline.pronunciation_check import check_pronunciation

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")


@app.route("/")
def index():
    return render_template("index.html", has_cloned_voice="voice_id" in session)


@app.route("/record")
def record():
    return render_template("record.html")


@app.route("/clone-voice", methods=["POST"])
def clone_voice_route():
    audio_file = request.files.get("audio")
    if not audio_file:
        return {"error": "No audio file received"}, 400

    try:
        voice_id = clone_voice("Lyric Companion user voice", audio_file.read(), audio_file.filename or "sample.webm")
    except RuntimeError as e:
        return {"error": str(e)}, 500

    session["voice_id"] = voice_id
    return {"voice_id": voice_id}


@app.route("/reset-voice", methods=["POST"])
def reset_voice():
    session.pop("voice_id", None)
    return redirect(url_for("index"))


@app.route("/check-pronunciation", methods=["POST"])
def check_pronunciation_route():
    audio_file = request.files.get("audio")
    target_word = request.form.get("word", "").strip()

    if not audio_file or not target_word:
        return {"error": "Missing audio or target word"}, 400

    try:
        transcript = speech_to_text(audio_file.read(), audio_file.filename or "recording.webm")
    except RuntimeError as e:
        return {"error": str(e)}, 500

    return check_pronunciation(target_word, transcript)


@app.route("/read")
def read():
    artist = request.args.get("artist", "").strip()
    title = request.args.get("title", "").strip()

    if not artist or not title:
        return redirect(url_for("index"))

    error = None
    data = None

    try:
        try:
            track = extract_variables(artist, title)
        except RuntimeError as e:
            if "MUSIXMATCH_API_KEY not configured" not in str(e):
                raise
            # Temporary fallback: use sample data to test the rest of the pipeline
            track = dict(SAMPLE_TRACK)

        # Only use the chorus for the prototype (TTS of the whole song is slow/expensive)
        lyrics_excerpt = extract_chorus(track["lyrics"])

        voice_id = session.get("voice_id", DEFAULT_VOICE_ID)
        tts_result = text_to_speech_with_timestamps(
            lyrics_excerpt,
            voice_id=voice_id,
            output_path="static/audio/reading.mp3",
        )
        words = group_words_with_timestamps(tts_result["alignment"])
        for w in words:
            w["html"] = mark_difficult_sounds(w["word"])
        readability = analyze_readability(lyrics_excerpt)
        pronunciations = annotate_words(readability["difficult_words"])

        data = {
            "artist": track["artist"],
            "title": track["title"],
            "meaning": track["meaning"],
            "moods": track["moods"],
            "words": words,
            "audio_url": url_for("static", filename="audio/reading.mp3"),
            "dsa_level": readability["dsa_level"],
            "difficult_words": readability["difficult_words"],
            "pronunciations": pronunciations,
        }
    except (RuntimeError, ValueError) as e:
        error = str(e)

    return render_template("reader.html", data=data, error=error, artist=artist, title=title)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
