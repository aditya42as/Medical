from ai.sarvam_client import ask_sarvam

def generate_questions(initial_text, language):
    prompt = f"""
    Patient said:
    {initial_text}

    Generate exactly 5 short follow-up medical questions.
    Keep them simple.

    Respond ONLY as numbered list.
    Language: {language}
    """
    return ask_sarvam(prompt)


def final_analysis(initial_text, qa_pairs, language):
    prompt = f"""
    Patient initial problem:
    {initial_text}

    Follow-up Q&A:
    {qa_pairs}

    Give:
    - Summary
    - Symptoms
    - Severity (Low/Moderate/High)
    - Advice

    Language: {language}
    """
    return ask_sarvam(prompt)