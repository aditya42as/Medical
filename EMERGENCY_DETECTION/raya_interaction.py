import speech_recognition as sr
import requests
import re
import os
import pygame
from gtts import gTTS
from database_manager import RayaDB
from raya_processor import TokenProcessor

SARVAM_API_KEY = "sk_69cwz5sk_AQe0riLTCMJplbOTi5VesCsi"
recognizer = sr.Recognizer()
db = RayaDB()
processor = TokenProcessor()

def speak(text, lang_code='hi'):
    clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # 2. "First, I need to...", "Okay, let's...", "The user wants..." jaisi lines ko hatana
    patterns_to_remove = [
        r"First, I need to.*?\.", 
        r"Okay, let's.*?[\.!]", 
        r"The user wants.*?[\.!]",
        r"I should start by.*?[\.!]",
        r"Based on the problem.*?[\.!]"
    ]
    for pattern in patterns_to_remove:
        clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE | re.DOTALL)
    
    clean_text = clean_text.strip()
    
    if not clean_text or len(clean_text) < 2: return

    print(f"RAYA ({lang_code}):", clean_text)
    filename = "voice.mp3"
    try:
        tts = gTTS(text=clean_text, lang=lang_code)
        tts.save(filename)
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        if os.path.exists(filename): os.remove(filename)
    except Exception as e: print(f"Speak Error: {e}")

def listen_with_retry(prompt, lang_code='hi', duration=5):
    attempts = 0
    while attempts < 2:
        if prompt: speak(prompt, lang_code)
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = recognizer.record(source, duration=duration)
                text = recognizer.recognize_google(audio, language='hi-IN' if lang_code=='hi' else 'en-IN')
                if text.strip(): return text
            except: attempts += 1
    return ""

def main():
    # 1. LANGUAGE
    lang_choice = listen_with_retry("नमस्ते, आप हिंदी में बात करना चाहेंगे या इंग्लिश में?", "hi")
    is_hindi = "english" not in lang_choice.lower() and "इंग्लिश" not in lang_choice
    l_code, curr_lang = ('hi', 'Hindi') if is_hindi else ('en', 'English')

    # 2. NAME (English Translation)
    name_raw = listen_with_retry("कृपया अपना नाम बताएं।" if is_hindi else "Please tell your name.", l_code) or "User"
    name_fix_prompt = f"System: Extract the name and provide ONLY the English spelling. No other text.\nInput: {name_raw}"
    name_res = requests.post("https://api.sarvam.ai/v1/chat/completions", 
                            headers={"Authorization": f"Bearer {SARVAM_API_KEY}"},
                            json={"model": "sarvam-m", "messages": [{"role": "user", "content": name_fix_prompt}]}).json()
    name = name_res["choices"][0]["message"]["content"].strip().split()[-1].replace(".", "")

    # 3. PATIENT DATA
    record = db.find_patient(name)
    if record:
        speak(f"स्वागत है {name}।" if is_hindi else f"Welcome back {name}.", l_code)
        patient_info = {"name": name, "age": record[1], "mobile": record[3]}
    else:
        speak("आप नए पेशेंट हैं।" if is_hindi else "New patient registration.", l_code)
        u_age = "".join(re.findall(r'\d+', listen_with_retry("आपकी उम्र क्या है?", l_code))) or "25"
        u_mobile = "".join(re.findall(r'\d+', listen_with_retry("अपना मोबाइल नंबर बताएं।", l_code))) or "0000000000"
        patient_info = {"name": name, "age": u_age, "mobile": u_mobile}
        db.add_patient(name, int(u_age), "Male", u_mobile)

    # 4. PROBLEM
    speak("अपनी परेशानी विस्तार से बताएं।" if is_hindi else "Describe your problem.", l_code)
    problem = listen_with_retry(None, l_code, duration=20)

    # 5. DYNAMIC QUESTIONS (Ask one by one)
    speak("मैं आपसे 5 छोटे सवाल पूछूँगी।" if is_hindi else "I will ask 5 short questions.", l_code)
    
    # STRICT SYSTEM INSTRUCTION
    q_gen_prompt = (f"You are a medical assistant. Based on: '{problem}', generate 5 simple questions in {curr_lang}. "
                    "STRICT RULE: No introduction, no thinking, no explanations. Just 5 questions, one per line.")
    
    q_res = requests.post("https://api.sarvam.ai/v1/chat/completions", 
                         headers={"Authorization": f"Bearer {SARVAM_API_KEY}"},
                         json={"model": "sarvam-m", "messages": [{"role": "user", "content": q_gen_prompt}]}).json()
    
    # Cleaning and splitting questions
    raw_content = q_res["choices"][0]["message"]["content"]
    clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
    
    # Split by newline and filter out any meta-talk lines
    questions = []
    for line in clean_content.split("\n"):
        line = line.strip()
        # Ignore lines that look like AI self-talk or are too short
        if line and "?" in line and not any(x in line.lower() for x in ["first", "need to", "understand"]):
            questions.append(re.sub(r'^\d+\.\s*', '', line))
    
    answers = []
    for q in questions[:5]:
        ans = listen_with_retry(q, l_code)
        answers.append(f"Q: {q}, A: {ans}")

    # 6. FINAL REPORT (Auto-Translate to English)
    speak("रिपोर्ट तैयार हो रही है।" if is_hindi else "Generating report...", l_code)
    report_p = f"Summarize this in professional English for hospital record: Problem: {problem}, Q&A: {answers}. NO extra text. JUST THE REPORT."
    final_res = requests.post("https://api.sarvam.ai/v1/chat/completions", 
                                headers={"Authorization": f"Bearer {SARVAM_API_KEY}"},
                                json={"model": "sarvam-m", "messages": [{"role": "user", "content": report_p}]}).json()
    
    final_report = re.sub(r'<think>.*?</think>', '', final_res["choices"][0]["message"]["content"], flags=re.DOTALL).strip()

    # 7. PDF & TOKEN
    token_details, pdf_path = processor.process_user_dynamic(patient_info, final_report)
    os.startfile(pdf_path)
    speak(f"टोकन नंबर {token_details['sub_token']}।" if is_hindi else f"Token {token_details['sub_token']}.", l_code)

if __name__ == "__main__":
    main()