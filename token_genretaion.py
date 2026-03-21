import json
import os
from datetime import datetime

class TokenGenerator:
    def __init__(self, db_path="database/patients.json"):
        self.db_path = db_path

    def get_counts(self, dept_name):
        major_count = 1
        dept_count = 1
        today = datetime.now().strftime("%Y-%m-%d")

        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    today_data = [p for p in data if p.get("date") == today]
                    major_count = len(today_data) + 1
                    dept_data = [p for p in today_data if p.get("department") == dept_name]
                    dept_count = len(dept_data) + 1
            except Exception:
                pass
        
        return major_count, dept_count

    def generate(self, priority, departments):
        dept = departments[0] if departments else "General"
        dept_abbr = dept[:4].upper().replace("_", "")
        
        major_id, sub_id_num = self.get_counts(dept)
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "major_id": major_id,
            "sub_token": f"{dept_abbr}-{sub_id_num:03d}",
            "priority": priority,
            "department": dept
        }

if __name__ == "__main__":
    tg = TokenGenerator()
    db_file = "database/patients.json"
    if os.path.exists(db_file):
        os.remove(db_file)
    if not os.path.exists("database"):
        os.makedirs("database")

    test_cases = [
        {"priority": "RED", "depts": ["Cardiology"]},
        {"priority": "GREEN", "depts": ["Orthopedics"]},
        {"priority": "YELLOW", "depts": ["Pediatrics"]},
        {"priority": "RED", "depts": ["General"]},
        {"priority": "GREEN", "depts": ["Cardiology"]} 
    ]

    print("\n--- GENERATING 5 TOKENS WITH INCREMENT LOGIC ---\n")

    current_db_data = []

    for case in test_cases:
        result = tg.generate(case["priority"], case["depts"])

        print(f"Major ID: #{result['major_id']} | Dept: {result['department']} | Token: {result['sub_token']} | Priority: {result['priority']}")

        current_db_data.append(result)
        with open(db_file, "w", encoding="utf-8") as f:
            json.dump(current_db_data, f, indent=4)
    
    print("\n--- TESTING COMPLETE: Check database/patients.json ---")