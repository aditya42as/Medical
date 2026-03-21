import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import tempfile
import pyttsx3

# ---------------------------
# TTS SETUP
# ---------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    print("RAYA:", text)
    engine.say(text)
    engine.runAndWait()


# ---------------------------
# STT FUNCTION
# ---------------------------

def listen(duration=30, lang="en-US"):
    try:
        fs = 16000

        print(f"\nListening... You have {duration} seconds. Speak NOW!")

        # 🔥 FORCE WASAPI + DEVICE
        sd.default.device = (1, None)   # input device index 1
        sd.default.samplerate = fs
        sd.default.channels = 1

        recording = sd.rec(
            int(duration * fs),
            dtype='int16',
            blocking=True
        )

        print("Processing speech...")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(temp_file.name, fs, recording)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language=lang)

        print("User:", text)
        return text

    except Exception as e:
        print("STT Error:", e)
        return ""