# main.py
import time
import sys
import re
import random
from voice.voice_handler import speak, listen, get_language_choice, long_description_listen
from ai.question_flow import generate_questions, final_analysis
from core.pipeline import NPipeline
from emergency.emergency_handler import handle_emergency
from database.db import save_patient
from NLP.summary_generator import SummaryGenerator

sys.stdout.reconfigure(encoding='utf-8')

FALLBACK_QUESTIONS = {
    'english': ["How is the pain feeling right now?", "When exactly did it start?", "Is it getting worse?", "Any other symptoms?", "Have you taken any medicine?"],
    'hindi': ["दर्द कैसा लग रहा है?", "यह कब शुरू हुआ?", "क्या दर्द बढ़ रहा है?", "कोई और लक्षण हैं?", "क्या कोई दवा ली है?"]
}

def parse_sarvam_questions(text):
    """Robust parser for Sarvam's one-line or messy output"""
    questions = re.split(r'\s*\d+\.?\s*', text)
    questions = [q.strip() for q in questions if q.strip() and len(q) > 8]
    return questions

def parse_summary_advice(text):
    """FINAL FIXED PARSER - aggressively cleans mixed English+Hindi, removes leaked words, and separates summary vs advice perfectly"""
    text = re.sub(r'<think>.*?</think>|Explanation:.*|Thinking:.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()

    # Detect language of output
    has_hindi = bool(re.search(r'[\u0900-\u097F]', text))

    # Remove leaked junk words that Sarvam always inserts
    junk_words = r'\b(Water|heavy|Without|er|with slight|लेज|सरदर्द|पेट|निचले|हिस्से|में|दर्द|बुखार|रात|को|निगरानी|के|ठंडा|आहार|ले|न ले|निगरा|नी|के|हल्का|बुखार)\b'
    text = re.sub(junk_words, '', text, flags=re.IGNORECASE)

    # If English user but Hindi leaked → remove all Hindi completely
    if not has_hindi or 'Patient experiences' in text or 'severe constant headache' in text.lower():
        text = re.sub(r'[\u0900-\u097F]+', '', text)   # strip any remaining Hindi

    # Smart split: take everything before last sentence as summary, last sentence as advice
    if has_hindi:
        sentences = [s.strip() for s in re.split(r'[।!?]', text) if s.strip() and len(s) > 5]
    else:
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip() and len(s) > 5]

    if len(sentences) > 1:
        summary_part = '. '.join(sentences[:-1]).strip() + ('.' if not has_hindi else '।')
        advice_part = sentences[-1].strip() + ('.' if not has_hindi else '।')
    else:
        summary_part = text
        advice_part = ""

    # Final cleanup
    summary_part = re.sub(r'^[।,.:\s]+|[।,.:\s]+$', '', summary_part).strip()
    summary_part = re.sub(r'\s+', ' ', summary_part)

    # Language-aware safe fallbacks
    if len(summary_part) < 15:
        summary_part = "Summary unclear. Please provide more details." if not has_hindi else "आपकी समस्या का सारांश स्पष्ट नहीं हो पाया। कृपया अधिक जानकारी दें।"
    if len(advice_part) < 8:
        advice_part = "Consult a doctor immediately." if not has_hindi else "तुरंत डॉक्टर से संपर्क करें।"

    # Extract severity
    severity_match = re.search(r'(Low|Moderate|High|कम|मध्यम|उच्च)', text, re.IGNORECASE)
    severity = severity_match.group(1).strip() if severity_match else None

    return summary_part, severity, advice_part

def main():
    print("RAYA starting...")

    lang_name, tts_lang, stt_lang = get_language_choice()
    is_hindi = lang_name == 'hindi'

    while True:
        prompt = "आपके पास अपनी समस्या विस्तार से बताने के लिए 30 सेकंड हैं। अब शुरू करें।" if is_hindi else "You have 30 seconds to describe your problem. Start now."
        speak(prompt, tts_lang)

        user_text = long_description_listen(lang_code=stt_lang, max_duration=35)

        if not user_text:
            speak("मैंने कुछ नहीं सुना। कृपया दोबारा बताएं।" if is_hindi else "I didn't hear anything.", tts_lang)
            continue

        processed_text = user_text

        if handle_emergency(processed_text):
            speak("आपातकाल पता चला!" if is_hindi else "Emergency detected!", tts_lang)
            time.sleep(8)
            continue

        nlp = NPipeline()
        nlp_result = nlp.process(processed_text)

        speak("विश्लेषण कर रही हूँ..." if is_hindi else "Analyzing...", tts_lang)

        questions_text = generate_questions(processed_text, lang_name, nlp_result['entities'])
        print("\n[DEBUG] RAW SARVAM QUESTIONS:", repr(questions_text))

        questions = parse_sarvam_questions(questions_text)

        if len(questions) < 3:
            print("[Using random fallback questions]")
            questions = random.sample(FALLBACK_QUESTIONS['hindi' if is_hindi else 'english'], 5)

        print(f"[DEBUG] Final questions: {questions}")

        speak("मैं पाँच सवाल पूछ रही हूँ। एक-एक करके जवाब दें।" if is_hindi else "I have five questions. Answer one by one.", tts_lang)

        answers = []
        for q in questions:
            speak(q, tts_lang)
            time.sleep(0.8)
            ans = listen(timeout=22, phrase_limit=18, lang_code=stt_lang)
            answers.append((q, ans if ans else "कोई जवाब नहीं" if is_hindi else "no answer"))

        qa_pairs = "\n".join([f"{q} → {a}" for q, a in answers])

        speak("प्रोसेस कर रही हूँ..." if is_hindi else "Processing...", tts_lang)
        final_raw = final_analysis(processed_text, qa_pairs, lang_name, nlp_result['entities'])

        print("\n[DEBUG] RAW SARVAM SUMMARY OUTPUT:", repr(final_raw))

        summary_part, sarvam_severity, advice_part = parse_summary_advice(final_raw)

        if not summary_part or len(summary_part) < 10:
            print("[Using fallback summary generator]")
            summarizer = SummaryGenerator()
            summary_part = summarizer.generate(nlp_result["entities"], language=lang_name)

        if not advice_part or len(advice_part) < 5:
            advice_part = "Consult a doctor immediately." if not is_hindi else "तुरंत डॉक्टर से संपर्क करें।"

        # Final Report
        print("\n" + "═" * 80)
        print("RAYA MEDICAL REPORT")
        print("═" * 80)
        print(f"Language     : {lang_name.upper()}")
        print(f"Date & Time  : {time.ctime()}")
        print(f"Intents      : {', '.join(nlp_result.get('intent', ['UNKNOWN']))}")
        print(f"Raw Input    : {user_text[:130]}...")
        print("-" * 80)
        print("NLP DETECTED:")
        print(f"  • Symptoms   : {', '.join(nlp_result['entities']['symptoms']) or 'None'}")
        print(f"  • Body Part  : {nlp_result['entities']['bodyPart'] or 'Not detected'}")
        print(f"  • Severity   : {nlp_result['entities'].get('severity', 'Unknown')}")
        print(f"  • Confidence : {nlp_result['confidence']:.1%}")
        print("-" * 80)
        print("SUMMARY:")
        print(summary_part)
        print("-" * 80)
        print("SEVERITY (Sarvam):")
        print(sarvam_severity or "Not detected by Sarvam")
        print("-" * 80)
        print("ADVICE:")
        print(advice_part)
        print("═" * 80)

        speak("यहाँ सारांश है।" if is_hindi else "Here is the summary.", tts_lang)
        speak(summary_part, tts_lang)
        speak("सलाह:" if is_hindi else "Advice:", tts_lang)
        speak(advice_part, tts_lang)

        save_patient({
            "language": lang_name,
            "raw_input": user_text,
            "nlp_intents": nlp_result.get('intent', ['UNKNOWN']),
            "nlp_entities": nlp_result["entities"],
            "qa_pairs": qa_pairs,
            "summary": summary_part,
            "advice": advice_part,
            "timestamp": time.ctime()
        })

        speak("धन्यवाद। नया केस शुरू करने के लिए 'again' बोलें।" if is_hindi else "Thank you. Say 'again' for new case.", tts_lang)

        if 'again' not in listen(timeout=12, lang_code=stt_lang).lower():
            speak("अलविदा।" if is_hindi else "Goodbye.", tts_lang)
            break

if __name__ == "__main__":
    main()