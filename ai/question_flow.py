# ai/question_flow.py
from ai.sarvam_client import ask_sarvam
import re

def clean_for_tts(text: str, language: str = 'english') -> str:
    """Aggressive cleaning + language-aware fallback"""
    if not text or len(text.strip()) < 3:
        if language.lower() == 'english':
            return "Sorry, I didn't understand. Please try again."
        else:
            return "क्षमा करें, मैं समझ नहीं पाया। कृपया दोबारा बताएं।"

    # Remove <think> blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<think>.*', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove quotes, markdown, symbols
    text = re.sub(r'["\'`‘’“”]', '', text)
    text = re.sub(r'[\*\_\-\=\+\|\[\]\(\)\{\}\<\>]', ' ', text)

    # Remove punctuation TTS reads aloud
    text = re.sub(r'[.,;:!?]', '', text)

    # Remove bad prefixes
    bad = [r'Explanation:', r'Summary:', r'Advice:', r'Note:', r'Output:', r'Patient said', r'Let me break']
    for p in bad:
        text = re.sub(p, '', text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) > 5 else ("Sorry, I didn't understand. Please try again." if language.lower() == 'english' else "क्षमा करें, मैं समझ नहीं पाया। कृपया दोबारा बताएं।")


def generate_questions(initial_text, language, nlp_entities):
    lang_instruction = "Use simple English" if language.lower() == "english" else "Use simple Hindi"
    prompt = f"""
Patient said ({language}): {initial_text}
Detected: symptoms={nlp_entities.get('symptoms',[])}, body={nlp_entities.get('bodyPart')}

Generate 5 different short follow-up questions.
Respond ONLY as numbered list:
1. Question one
2. Question two
...
{lang_instruction}. No extra text.
"""
    raw = ask_sarvam(prompt)
    return clean_for_tts(raw, language)


def final_analysis(initial_text, qa_pairs, language, nlp_entities):
    lang_instruction = "English" if language.lower() == "english" else "Hindi"
    entities_str = f"NLP detected: symptoms={nlp_entities.get('symptoms',[])}, body={nlp_entities.get('bodyPart')}, severity={nlp_entities.get('severity')}"
    prompt = f"""
Patient problem: {initial_text}
{entities_str}
Answers: {qa_pairs}

Reply in this EXACT format in {lang_instruction} only:

Summary: [one line summary]
Symptoms: [list symptoms]
Severity: Low / Moderate / High
Advice: [clear practical advice]

Do not repeat sections. Do not add extra text or symbols.
"""
    raw = ask_sarvam(prompt)
    return clean_for_tts(raw, language)