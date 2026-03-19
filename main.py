from voice.voice_handler import speak, listen
from ai.question_flow import generate_questions, final_analysis
from core.pipeline import NPipeline
from database.db import save_patient
from emergency.emergency_handler import handle_emergency

def get_language():
    speak("Choose your language. Say Hindi or English")
    lang = listen(5).lower()

    if "hindi" in lang:
        return ("Hindi", "hi", "hi-IN")
    return ("English", "en", "en-US")


def ask_questions(q_text, lang_code):
    questions = [q.strip() for q in q_text.split("\n") if q.strip()]
    answers = []

    for q in questions:
        speak(q, lang_code)
        ans = listen(10, lang_code)
        answers.append((q, ans))

    return answers


def main():
    speak("Welcome to RAYA Health Assistant")

    language, tts_lang, stt_lang = get_language()

    speak("Please describe your problem")
    user_text = listen(30, stt_lang)

    if not user_text:
        speak("I could not understand. Try again.")
        return

   
    nlp = NPipeline()
    nlp_result = nlp.process(user_text)

    print("\nNLP RESULT:\n", nlp_result)

    
    if handle_emergency(user_text):
        speak("Emergency detected. Help is on the way.", tts_lang)
        return

    speak("Analyzing your condition", tts_lang)
    q_text = generate_questions(user_text, language)

    print("\nQuestions:\n", q_text)

    answers = ask_questions(q_text, stt_lang)

    qa_pairs = "\n".join([f"{q} -> {a}" for q, a in answers])
    speak("Processing your answers", tts_lang)
    final_result = final_analysis(user_text, qa_pairs, language)

    speak("Here is your result", tts_lang)
    print("\n===== FINAL RESULT =====\n")
    print(final_result)
    speak(final_result, tts_lang)

    save_patient({
        "input": user_text,
        "nlp": nlp_result,
        "qa": qa_pairs,
        "final": final_result
    })


if __name__ == "__main__":
    main()