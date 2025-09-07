from __future__ import annotations

TTS_AVAILABLE = False
ENGINE = None

try:
    import pyttsx3
    ENGINE = pyttsx3.init()
    # Check if German voice is available
    voices = ENGINE.getProperty('voices')
    if any('de_DE' in v.id for v in voices) or any('German' in v.name for v in voices):
        TTS_AVAILABLE = True
    else:
        print("Warning: German TTS voice not found. Audio playback will be disabled.")

except ImportError:
    print("Warning: pyttsx3 not found. Please run 'pip install pyttsx3' for audio features.")
except Exception as e:
    print(f"An error occurred during pyttsx3 initialization: {e}")


def speak(text: str, lang: str = "de"):
    if not TTS_AVAILABLE or not ENGINE:
        return

    try:
        if lang == "de":
            # Attempt to set a German voice
            voices = ENGINE.getProperty('voices')
            de_voices = [v for v in voices if 'de_DE' in v.id or 'German' in v.name]
            if de_voices:
                ENGINE.setProperty('voice', de_voices[0].id)
        
        ENGINE.say(text)
        ENGINE.runAndWait()
    except Exception as e:
        print(f"Error during TTS playback: {e}")

def is_tts_available() -> bool:
    return TTS_AVAILABLE
