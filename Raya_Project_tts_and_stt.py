import os
import time
import tempfile
from datetime import datetime

import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import pygame


TTS_SYMBOL_MAP = {
    '?':  'question mark',
    '!':  'exclamation mark',
    '.':  'full stop',
    ',':  'comma',
    ':':  'colon',
    ';':  'semicolon',
    '@':  'at the rate',
    '#':  'hash',
    '$':  'dollar',
    '%':  'percent',
    '&':  'ampersand',
    '*':  'asterisk',
    '(':  'open bracket',
    ')':  'close bracket',
    '[':  'open square bracket',
    ']':  'close square bracket',
    '{':  'open curly bracket',
    '}':  'close curly bracket',
    '-':  'hyphen',
    '+':  'plus',
    '=':  'equals',
    '/':  'slash',
    '\\': 'backslash',
    '<':  'less than',
    '>':  'greater than',
    '^':  'caret',
    '~':  'tilde',
    '`':  'backtick',
    '"':  'double quote',
    "'":  'single quote',
}

STT_SYMBOL_MAP = {v: k for k, v in TTS_SYMBOL_MAP.items()}

HISTORY_FILE = 'stt_history.txt'

SUPPORTED_LANGUAGES = {
    '1': ('English',  'en',    'en-US'),
    '2': ('Hindi',    'hi',    'hi-IN'),
    '3': ('Spanish',  'es',    'es-ES'),
    '4': ('French',   'fr',    'fr-FR'),
    '5': ('German',   'de',    'de-DE'),
    '6': ('Japanese', 'ja',    'ja-JP'),
    '7': ('Arabic',   'ar',    'ar-SA'),
}

last_spoken_text = None


def preprocess_for_tts(text):
    result = ""
    for char in text:
        result += f" {TTS_SYMBOL_MAP[char]} " if char in TTS_SYMBOL_MAP else char
    return result.strip()


def postprocess_from_stt(text):
    result = text.lower()
    for word, symbol in STT_SYMBOL_MAP.items():
        result = result.replace(word, symbol)
    return result


def text_to_speech(text, speed=1.0, volume=1.0, pitch=1.0, voice='female', language='en'):
    voice_tld = {'female': 'com', 'male': 'co.uk'}
    tld = voice_tld.get(voice, 'com')
    processed_text = preprocess_for_tts(text)

    print(f'\nSpeaking: "{text}"')
    print(f'  Speed={speed} | Volume={volume} | Pitch={pitch} | Voice={voice} | Language={language}')

    tts = gTTS(text=processed_text, lang=language, tld=tld, slow=False)

    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_mp3.close()
    tts.save(temp_mp3.name)

    audio = AudioSegment.from_mp3(temp_mp3.name)

    if volume != 1.0:
        audio = audio + (20 * (volume - 1.0))

    if speed != 1.0:
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        }).set_frame_rate(audio.frame_rate)

    if pitch != 1.0:
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * pitch)
        }).set_frame_rate(44100)

    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_wav.close()
    audio.export(temp_wav.name, format='wav')

    pygame.mixer.init()
    pygame.mixer.music.load(temp_wav.name)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()

    os.unlink(temp_mp3.name)
    os.unlink(temp_wav.name)


def speech_to_text(timeout=5, phrase_limit=10, language='en-US', continuous=False):
    recognizer = sr.Recognizer()
    results = []

    def listen_once():
        with sr.Microphone() as source:
            print("\nAdjusting for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now!")
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
                print("Recognizing speech...")
                raw_text = recognizer.recognize_google(audio, language=language)
                final_text = postprocess_from_stt(raw_text)
                print(f'Recognized: "{final_text}"')
                save_to_history(final_text)
                return final_text
            except sr.WaitTimeoutError:
                print("No speech detected. Please try again.")
            except sr.UnknownValueError:
                print("Could not understand. Please speak clearly.")
            except sr.RequestError as e:
                print(f"Service error: {e}. Check your internet connection.")
            return None

    if not continuous:
        return listen_once()

    print("\nContinuous listening mode ON. Say 'stop listening' to exit.\n")
    while True:
        result = listen_once()
        if result:
            results.append(result)
            if 'stop listening' in result.lower():
                print("Stopping continuous listening.")
                break
    return results


def save_tts_to_file(text, filename='output.mp3', speed=1.0, volume=1.0, pitch=1.0, voice='female', language='en'):
    voice_tld = {'female': 'com', 'male': 'co.uk'}
    tld = voice_tld.get(voice, 'com')
    tts = gTTS(text=preprocess_for_tts(text), lang=language, tld=tld, slow=False)
    tts.save(filename)
    print(f"\nAudio saved to: {filename}")


def save_to_history(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {text}\n")


def view_history():
    print("\nSTT HISTORY LOG")
    print("=" * 50)
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content if content else "No history yet.")
    except FileNotFoundError:
        print("No history file found. Use STT first.")
    print("=" * 50)


def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print("History cleared.")
    else:
        print("No history file to clear.")


def select_language():
    print("\nSELECT LANGUAGE")
    for key, (name, _, _) in SUPPORTED_LANGUAGES.items():
        print(f"  {key}. {name}")
    choice = input("Enter number: ").strip()
    if choice in SUPPORTED_LANGUAGES:
        name, tts_code, stt_code = SUPPORTED_LANGUAGES[choice]
        print(f"Language set to: {name}")
        return tts_code, stt_code
    print("Invalid choice. Keeping English.")
    return 'en', 'en-US'


def repeat_last(settings):
    global last_spoken_text
    if last_spoken_text:
        print(f'\nRepeating: "{last_spoken_text}"')
        text_to_speech(last_spoken_text, **_tts_kwargs(settings))
    else:
        print("Nothing to repeat yet. Use TTS first.")


def listen_and_speak_back(settings):
    print("\nLISTEN AND SPEAK BACK MODE")
    result = speech_to_text(language=settings['stt_lang'])
    if result:
        print(f'\nSpeaking back: "{result}"')
        time.sleep(0.5)
        text_to_speech(result, **_tts_kwargs(settings))
    return result


def adjust_settings(settings):
    print("\nSETTINGS")
    print("=" * 50)
    print(f"  Speed   : {settings['speed']}  (0.5 - 2.0)")
    print(f"  Volume  : {settings['volume']}  (0.0 - 2.0)")
    print(f"  Pitch   : {settings['pitch']}  (0.5 - 1.5)")
    print(f"  Voice   : {settings['voice']}  (male / female)")
    print(f"  Language: {settings['tts_lang']}")
    print("=" * 50)
    try:
        if s := input(f"\nNew Speed (Enter to keep {settings['speed']}): ").strip():
            settings['speed'] = max(0.5, min(2.0, float(s)))
        if s := input(f"New Volume (Enter to keep {settings['volume']}): ").strip():
            settings['volume'] = max(0.0, min(2.0, float(s)))
        if s := input(f"New Pitch (Enter to keep {settings['pitch']}): ").strip():
            settings['pitch'] = max(0.5, min(1.5, float(s)))
        if s := input(f"New Voice male/female (Enter to keep {settings['voice']}): ").strip().lower():
            if s in ('male', 'female'):
                settings['voice'] = s
        if input("Change language? (y/n): ").strip().lower() == 'y':
            settings['tts_lang'], settings['stt_lang'] = select_language()
        print("\nSettings updated!")
    except ValueError:
        print("Invalid input. Settings unchanged.")
    return settings


def _tts_kwargs(settings):
    return {
        'speed':    settings['speed'],
        'volume':   settings['volume'],
        'pitch':    settings['pitch'],
        'voice':    settings['voice'],
        'language': settings['tts_lang'],
    }


def main():
    global last_spoken_text

    print("\n" + "=" * 50)
    print("TTS + STT SYSTEM")
    print("=" * 50)

    settings = {
        'speed':    1.0,
        'volume':   1.0,
        'pitch':    1.0,
        'voice':    'female',
        'tts_lang': 'en',
        'stt_lang': 'en-US',
    }

    menu = """
MAIN MENU
---------------------------------
 1. Text to Speech (TTS)
 2. Speech to Text (STT)
 3. Continuous Listening Mode
 4. Listen & Speak Back
 5. Save TTS to MP3 File
 6. View STT History
 7. Clear STT History
 8. Repeat Last Spoken Text
 9. Adjust Settings
10. Exit
---------------------------------"""

    while True:
        print(menu)
        choice = input("Enter choice (1-10): ").strip()

        if choice == '1':
            text = input("\nEnter text to speak: ")
            last_spoken_text = text
            text_to_speech(text, **_tts_kwargs(settings))

        elif choice == '2':
            result = speech_to_text(language=settings['stt_lang'])
            if result:
                last_spoken_text = result

        elif choice == '3':
            speech_to_text(language=settings['stt_lang'], continuous=True)

        elif choice == '4':
            result = listen_and_speak_back(settings)
            if result:
                last_spoken_text = result

        elif choice == '5':
            text = input("\nEnter text to save as audio: ")
            filename = input("Enter filename (e.g. hello.mp3): ").strip()
            if not filename.endswith('.mp3'):
                filename += '.mp3'
            last_spoken_text = text
            save_tts_to_file(text, filename=filename, **_tts_kwargs(settings))

        elif choice == '6':
            view_history()

        elif choice == '7':
            if input("\nAre you sure? (y/n): ").strip().lower() == 'y':
                clear_history()

        elif choice == '8':
            repeat_last(settings)

        elif choice == '9':
            settings = adjust_settings(settings)

        elif choice == '10':
            print("\nGoodbye! See you next time.")
            break

        else:
            print("\nInvalid choice. Please enter a number from 1-10.")


if __name__ == "__main__":
    main()