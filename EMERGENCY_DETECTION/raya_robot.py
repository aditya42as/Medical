import cv2
import speech_recognition as sr
import sqlite3
import numpy as np

def fetch_emergency_details(user_text):
    conn = sqlite3.connect('emergency_system.db')
    cursor = conn.cursor()
    query = """
        SELECT s.level, d.name, d.contact, s.dept 
        FROM symptoms s 
        JOIN doctors d ON s.dept = d.dept 
        WHERE ? LIKE '%' || s.name || '%'
        LIMIT 1
    """
    cursor.execute(query, (user_text.lower(),))
    res = cursor.fetchone()
    conn.close()
    return res

def trigger_final_alert(level, d_name, d_contact, dept):
    screen = np.zeros((300, 600, 3), dtype=np.uint8)
    color = (0, 0, 255) if level == 'RED' else (0, 255, 255) if level == 'YELLOW' else (0, 255, 0)
    screen[:] = color
    
    cv2.putText(screen, "ALERT SENT!", (10, 80), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)
    cv2.putText(screen, f"DR: {d_name}", (10, 150), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
    cv2.putText(screen, f"CALL: {d_contact}", (10, 220), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
    
    print(f">>> [FINAL ACTION] {level} Alert! Contacting {d_name}...")
    cv2.imshow("RAYA PRO DISPLAY", screen)
    cv2.waitKey(4000)
    cv2.destroyWindow("RAYA PRO DISPLAY") 

def start_robot():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    recognizer = sr.Recognizer()

    print("\n--- RAYA V3 (READY) ---")
    print("Monitoring Patient... Say 'EXIT' to stop.\n")

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Patient Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("RAYA Camera Vision", frame)

        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening for symptom...")
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=4)
                text = recognizer.recognize_google(audio).lower()
                
                if 'exit' in text or 'stop' in text:
                    print("Shutting down...")
                    break

                data = fetch_emergency_details(text)
                if data:
                    print(f"I heard '{text}'. Is this correct? (Yes/No)")
                    
                    c_audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    c_text = recognizer.recognize_google(c_audio).lower()
                    print(f"Confirmation: {c_text}")

                    if 'yes' in c_text:
                        # Sirf YES par light show hogi
                        level, d_name, d_contact, dept = data
                        trigger_final_alert(level, d_name, d_contact, dept)
                    else:
                        print("Ok, tell me the symptom again.")
                else:
                    print("Symptom not recognized. Try again.")

            except sr.UnknownValueError:
                pass
            except Exception:
                pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_robot()