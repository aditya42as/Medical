# main.py
import time
import sys
import re
from voice.voice_handler import speak, listen, get_language_choice, long_description_listen
from ai.question_flow import generate_questions, final_analysis
from core.pipeline import NPipeline
from emergency.emergency_handler import handle_emergency
from database.db import save_patient

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("RAYA starting...")

    lang_name, tts_lang, stt_lang = get_language_choice()
    is_hindi = lang_name == 'hindi'

    while True:
        prompt = "आपके पास अपनी समस्या विस्तार से बताने के लिए 30 सेकंड हैं। बोलते रहें, बीच में रुकें तो भी जारी रखें। अब शुरू करें।" if is_hindi else "You have 30 seconds to describe your problem in detail. Keep speaking even with pauses. Start now."
        speak(prompt, tts_lang)

        user_text = long_description_listen(lang_code=stt_lang, max_duration=35)

        if not user_text:
            speak("मैंने कुछ नहीं सुना। कृपया दोबारा बताएं।" if is_hindi else "I didn't hear anything. Please try again.", tts_lang)
            continue

        processed_text = user_text

        if handle_emergency(processed_text):
            speak("आपातकाल पता चला! मदद बुलाई जा रही है।" if is_hindi else "Emergency detected! Help is on the way.", tts_lang)
            time.sleep(8)
            continue

        nlp = NPipeline()
        nlp_result = nlp.process(processed_text)

        speak("विश्लेषण कर रहा हूँ... एक पल रुकें।" if is_hindi else "Analyzing... One moment.", tts_lang)

        questions_text = generate_questions(processed_text, lang_name, nlp_result['entities'])
        questions = [re.sub(r'^\d+[\.\)]\s*', '', line.strip()) for line in questions_text.split('\n') if line.strip()]
        questions = [q for q in questions if len(q) > 5][:5]

        if len(questions) < 3:
            questions = ["दर्द कैसा है?", "यह कब शुरू हुआ?", "क्या यह बढ़ रहा है?", "कोई अन्य लक्षण?", "कोई दवा ली?"] if is_hindi else ["How is the pain?", "When did it start?", "Is it getting worse?", "Any other symptoms?", "Any medicine taken?"]

        speak("मैं पाँच सवाल पूछ रहा हूँ। एक-एक करके जवाब दें।" if is_hindi else "I have five questions. Answer one by one.", tts_lang)

        answers = []
        for q in questions:
            speak(q, tts_lang)
            time.sleep(0.8)
            ans = listen(timeout=22, phrase_limit=18, lang_code=stt_lang)
            answers.append((q, ans if ans else "कोई जवाब नहीं" if is_hindi else "no answer"))

        qa_pairs = "\n".join([f"{q} → {a}" for q, a in answers])

        speak("आपके जवाबों को प्रोसेस कर रहा हूँ..." if is_hindi else "Processing your answers...", tts_lang)
        final_raw = final_analysis(processed_text, qa_pairs, lang_name, nlp_result['entities'])

        # Strong cleaning + parsing
        final_raw = re.sub(r'<think>.*?</think>', '', final_raw, flags=re.DOTALL | re.IGNORECASE)

        # Robust splitting for Summary and Advice
        summary_part = "Summary not generated"
        advice_part = "Consult a doctor immediately."

        if "Summary:" in final_raw and "Advice:" in final_raw:
            summary_part = final_raw.split("Advice:")[0].replace("Summary:", "").strip()
            advice_part = final_raw.split("Advice:")[-1].strip()
        elif "Summary:" in final_raw:
            summary_part = final_raw.split("Summary:")[-1].strip()
        elif "Advice:" in final_raw:
            advice_part = final_raw.split("Advice:")[-1].strip()

        # === FINAL CLEAN REPORT ===
        print("\n" + "═" * 80)
        print("RAYA MEDICAL REPORT")
        print("═" * 80)
        print(f"Language     : {lang_name.upper()}")
        print(f"Date & Time  : {time.ctime()}")
        print(f"Intents      : {', '.join(nlp_result.get('intent', ['UNKNOWN']))}")
        print(f"Raw Input    : {user_text[:130]}..." if len(user_text) > 130 else user_text)
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