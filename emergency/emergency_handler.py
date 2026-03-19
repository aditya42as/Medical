from EMERGENCY_DETECTION.raya_robot import fetch_emergency_details, trigger_final_alert

def handle_emergency(user_text):
    data = fetch_emergency_details(user_text)

    if data:
        level, d_name, d_contact, dept = data

        if level == "RED":
            print("🚨 EMERGENCY DETECTED")
            trigger_final_alert(level, d_name, d_contact, dept)
            return True

    return False