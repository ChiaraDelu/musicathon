# Lyric Companion 🎵

A Flask web app built for the [Musixmatch Musicathon](https://musicathon.musixmatch.com/) hackathon, helping people with dyslexia (DSA) read and enjoy song lyrics.

## Features

- Search any song and read its chorus with synchronized word-by-word highlighting (powered by ElevenLabs text-to-speech with timestamps)
- Adjustable reading speed (0.5x–1.25x) with highlighting that stays in sync
- Difficult sounds/letter clusters (e.g. `th`, `sh`, `wr`) highlighted in red
- Readability score (1-5) based on the Flesch Reading Ease formula
- Pronunciation practice: record yourself saying a tricky word and get instant feedback
- Optional voice cloning: read the lyrics back in your own voice
- Dyslexia-friendly UI: OpenDyslexic font, large text, high-contrast turquoise theme

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with your API keys:

   ```
   MUSIXMATCH_API_KEY=your_musixmatch_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   LALAL_API_KEY=your_lalal_key
   FLASK_SECRET_KEY=any_random_string
   ```

   - `MUSIXMATCH_API_KEY` is optional for local testing: if missing, the app falls back to sample lyrics so the rest of the pipeline can be tested.
   - `ELEVENLABS_API_KEY` is required for text-to-speech, pronunciation practice, and voice cloning.

3. Run the app:

   ```bash
   python3 app.py
   ```

   The app starts at `http://127.0.0.1:5000` with auto-reload enabled.

## Project structure

```
app.py                  Flask routes
clients/                External API clients (Musixmatch, ElevenLabs, Lalal.ai)
pipeline/                Lyrics processing (chorus extraction, readability, pronunciation)
templates/               Jinja2 HTML templates
static/                  CSS, JS, fonts, generated audio
docs/                    API reference notes
```
