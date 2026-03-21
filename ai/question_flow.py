
from ai.sarvam_client import ask_sarvam
import re

def clean_for_tts(text: str) -> str:
    if not text or len(text.strip()) < 3:
        return "मैं समझ नहीं पाया। कृपया दोबारा बताएं।"

    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<think>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'["\'`‘’“”]', '', text)
    text = re.sub(r'[\*\_\-\=\+\|\[\]\(\)\{\}\<\>]', ' ', text)
    text = re.sub(r'[.,;:!?]', '', text)

    bad = [r'Explanation:', r'Summary:', r'Advice:', r'Note:', r'Output:', r'Patient said']
    for p in bad:
        text = re.sub(p, '', text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) > 5 else "मैं समझ नहीं पाया। कृपया दोबारा बताएं।"


def generate_questions(initial_text, language, nlp_entities):
    prompt = f"""
Patient said ({language}): {initial_text}

Generate 5 completely different short follow-up questions. 
Make them unique every single time.
Respond ONLY as numbered list:
1. Question one
2. Question two
3. Question three
4. Question four
5. Question five

Use simple {language}. No extra text.
"""
    raw = ask_sarvam(prompt)
    return clean_for_tts(raw)


def final_analysis(initial_text, qa_pairs, language, nlp_entities):
    prompt = f"""
Patient problem: {initial_text}
Answers: {qa_pairs}

Reply in this EXACT format:

Summary: [one line summary]
Symptoms: [list symptoms]
Severity: Low / Moderate / High
Advice: [clear practical advice]

Do not repeat sections. Do not add extra text.
"""
    raw = ask_sarvam(prompt)
    return clean_for_tts(raw)