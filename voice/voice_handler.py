

from Raya_Project_tts_and_stt import text_to_speech, speech_to_text

def speak(text, lang="en"):
    try:
        text_to_speech(text, language=lang)
    except:
        print("TTS Error")

def listen(duration=10, lang="en-US"):
    try:
        result = speech_to_text(timeout=5, phrase_limit=duration, language=lang)
        if isinstance(result, list):
            return " ".join(result)
        return result if result else ""
    except:
        print("STT Error")
        return ""