import time
import speech_recognition as sr
from Raya_Project_tts_and_stt import text_to_speech, speech_to_text
import re

DEFAULT_TTS_LANG = 'en'
DEFAULT_STT_LANG = 'en-US'
MAX_LISTEN_SEC   = 30
QUESTION_LISTEN  = 18

LANG_MAP = {
    'english': ('en', 'en-US'),
    'hindi':   ('hi', 'hi-IN'),
}

def clean_text_for_tts(text: str) -> str:
    """Ultra-strong cleaning to stop 'full stop', 'comma', quotes, etc."""
    if not text:
        return text

    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<think>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'["\'`‘’“”.,;:!?]', '', text)
    text = re.sub(r'[\*\_\-\=\+\|\[\]\(\)\{\}\<\>]', ' ', text)

    bad = [r'Explanation:', r'Summary:', r'Advice:', r'Note:', r'Output:', r'Patient said', r'Let me break', r'First, I need']
    for p in bad:
        text = re.sub(p, '', text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text).strip()
    return text

def speak(text, lang_code='en'):
    """Speak using Piyush's TTS with strong cleaning"""
    if not text.strip():
        return
    cleaned = clean_text_for_tts(text)
    try:
        text_to_speech(cleaned, language=lang_code)
        time.sleep(0.4)
    except Exception as e:
        print(f"[TTS FAIL] {e}")

def listen(timeout=MAX_LISTEN_SEC, phrase_limit=None, lang_code=DEFAULT_STT_LANG):
    """Single-turn listen (for questions)"""
    try:
        print(f"[STT SINGLE] Listening ({phrase_limit or timeout}s) in {lang_code}...")
        result = speech_to_text(
            timeout=timeout,
            phrase_limit=phrase_limit,
            language=lang_code,
            continuous=False
        )

        if isinstance(result, list):
            text = " ".join([r.strip() for r in result if r.strip()])
        else:
            text = str(result).strip() if result else ""

        if text:
            print(f"[STT] → {text}")
            return text
        return ""
    except Exception as e:
        print(f"[STT ERROR] {type(e).__name__}: {e}")
        return ""

def long_description_listen(lang_code='hi-IN', max_duration=35):
    """Timed long listening for initial complaint"""
    print(f"[LONG DESCRIPTION] Starting for {max_duration} seconds...")
    print("[SPEAK NOW] Describe your problem in detail. Keep talking even with pauses...")

    full_chunks = []
    start_time = time.time()

    while time.time() - start_time < max_duration:
        try:
            result = speech_to_text(
                timeout=6,
                phrase_limit=12,
                language=lang_code,
                continuous=False
            )
            if isinstance(result, list):
                chunk = " ".join([r.strip() for r in result if r.strip()])
            else:
                chunk = str(result).strip() if result else ""

            if chunk:
                full_chunks.append(chunk)
                print(f"[CHUNK] {chunk}")
        except Exception:
            pass
        time.sleep(0.3)

    final_text = " ".join(full_chunks).strip()
    print(f"[LONG DESCRIPTION END] Captured: {final_text}")
    return final_text

def get_language_choice():
    speak("Preferred Language? Hindi or English.", 'en')
    time.sleep(0.6)

    for _ in range(3):
        ans = listen(timeout=15, phrase_limit=8, lang_code='en-US').lower()
        if any(w in ans for w in ['hindi', 'हिंदी', 'hi']):
            speak("हिंदी चुना गया।", 'hi')
            return 'hindi', 'hi', 'hi-IN'
        if any(w in ans for w in ['english', 'अंग्रेजी', 'en']):
            speak("English selected.", 'en')
            return 'english', 'en', 'en-US'

    speak("Defaulting to English.", 'en')
    return 'english', 'en', 'en-US'