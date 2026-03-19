import requests
import time
from config.api_keys import SARVAM_API_KEY

def ask_sarvam(prompt):
    url = "https://api.sarvam.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "sarvam-m",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("Sarvam Error:", e)
        time.sleep(3)
        return ask_sarvam(prompt)