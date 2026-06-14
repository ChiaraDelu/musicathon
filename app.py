import streamlit as st
import json
from clients.musixmatch_client import extract_variables

st.set_page_config(page_title="Musicathon", layout="wide")

st.title("🎵 Musicathon - Lyrics & Analysis")
st.write("Cerca una canzone e scopri il significato, i mood e le tematiche")

col1, col2 = st.columns(2)

with col1:
    artist = st.text_input("🎤 Artista", placeholder="Es: Massive Attack")

with col2:
    title = st.text_input("🎵 Titolo Canzone", placeholder="Es: Hymn of the Big Wheel")

if st.button("Cerca", type="primary"):
    if not artist or not title:
        st.error("Per favore inserisci sia l'artista che il titolo")
    else:
        try:
            with st.spinner("Caricamento..."):
                result = extract_variables(artist, title)

            st.success("✅ Trovato!")

            # Artist e Title
            st.subheader(f"{result['artist']} - {result['title']}")

            # Lyrics
            with st.expander("📝 Testo Completo", expanded=True):
                st.text_area("Lyrics", value=result['lyrics'], height=300, disabled=True)

            # Analysis columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("💭 Significato")
                if result['meaning']:
                    st.write(result['meaning'])
                else:
                    st.info("Significato non disponibile")

            with col2:
                st.subheader("🎭 Mood")
                if result['moods']:
                    for mood in result['moods']:
                        st.write(f"• {mood}")
                else:
                    st.info("Mood non disponibile")

            # Themes and Entities
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🎯 Tematiche")
                if result['themes']:
                    for theme in result['themes']:
                        st.write(f"• {theme}")
                else:
                    st.info("Tematiche non disponibili")

            with col2:
                st.subheader("👥 Entità")
                if result['entities']:
                    for entity in result['entities']:
                        st.write(f"• {entity}")
                else:
                    st.info("Entità non disponibili")

            # Rating
            st.subheader("⭐ Audience Rating")
            if result['rating']:
                st.write(result['rating'])
            else:
                st.info("Rating non disponibile")

        except RuntimeError as e:
            st.error(f"❌ Errore: {e}")
        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Errore imprevisto: {e}")
