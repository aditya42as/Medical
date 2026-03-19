import json
import time

def save_patient(data):
    try:
        with open("database/patients.json", "r") as f:
            db = json.load(f)
    except:
        db = []

    data["timestamp"] = time.ctime()
    db.append(data)

    with open("database/patients.json", "w") as f:
        json.dump(db, f, indent=4)