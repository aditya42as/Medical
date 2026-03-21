from ai.sarvam_client import ask_sarvam

def normalize_to_english(text: str, current_lang: str) -> str:
    """
    If input is Hindi → try to translate to English for NLP pipeline.
    Fallback: return original if translation fails.
    """
    if current_lang.lower() == 'english':
        return text

    simple_map = {
        "bukhar": "fever",
        "sar dard": "headache",
        "saans": "breathing",
        "khasi": "cough",
        "thakan": "fatigue",
    }

    words = text.lower().split()
    normalized = [simple_map.get(w, w) for w in words]
    simple_version = " ".join(normalized)

    try:
        prompt = f"Translate this Hindi sentence to English medical context:\n{simple_version}"
        translated = ask_sarvam(prompt)
        if len(translated.strip()) > 5:
            print(f"[TRANS] Sarvam → {translated}")
            return translated.strip()
    except Exception as e:
        print(f"[TRANSLATE FAIL] {e}")

    print("[TRANS] Using simple normalization")
    return simple_version