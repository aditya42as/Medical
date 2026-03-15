import sqlite3

def setup_database():
    conn = sqlite3.connect('emergency_system.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS doctors")
    cursor.execute("CREATE TABLE doctors (doc_id INTEGER PRIMARY KEY, name TEXT, dept TEXT, contact TEXT)")
    
    docs = [
        (1, 'Dr. Aryan', 'Cardio', '9876500001'), (2, 'Dr. Neha', 'Neuro', '9876500002'),
        (3, 'Dr. Rahul', 'Ortho', '9876500003'), (4, 'Dr. Sanya', 'Skin', '9876500004'),
        (5, 'Dr. Vikrant', 'Cardio', '9876500005'), (6, 'Dr. Mehak', 'Eye', '9876500006'),
        (7, 'Dr. Ishaan', 'Neuro', '9876500007'), (8, 'Dr. Preeti', 'General', '9876500008'),
        (9, 'Dr. Amit', 'ENT', '9876500009'), (10, 'Dr. Jolly', 'Dental', '9876500010')
    ]
    cursor.executemany("INSERT INTO doctors VALUES (?,?,?,?)", docs)

    cursor.execute("DROP TABLE IF EXISTS symptoms")
    cursor.execute("CREATE TABLE symptoms (s_id INTEGER PRIMARY KEY, name TEXT, level TEXT, dept TEXT)")
    
    symptom_list = [
        ('chest pain', 'RED', 'Cardio'), ('heart attack', 'RED', 'Cardio'), 
        ('stroke', 'RED', 'Neuro'), ('unconscious', 'RED', 'Neuro'),
        ('heavy bleeding', 'RED', 'General'), ('seizure', 'RED', 'Neuro'),
        ('difficulty breathing', 'RED', 'Cardio'), ('severe burn', 'RED', 'Skin'),
        ('poisoning', 'RED', 'General'), ('paralysis', 'RED', 'Neuro'),
        ('fracture', 'YELLOW', 'Ortho'), ('high fever', 'YELLOW', 'General'),
        ('severe abdominal pain', 'YELLOW', 'General'), ('blurred vision', 'YELLOW', 'Eye'),
        ('ear infection', 'YELLOW', 'ENT'), ('asthma attack', 'YELLOW', 'Cardio'),
        ('deep cut', 'YELLOW', 'General'), ('back injury', 'YELLOW', 'Ortho'),
        ('dehydration', 'YELLOW', 'General'), ('allergic reaction', 'YELLOW', 'Skin'),
        ('cough', 'GREEN', 'General'), ('mild headache', 'GREEN', 'General'),
        ('sore throat', 'GREEN', 'ENT'), ('stomach ache', 'GREEN', 'General'),
        ('minor scrape', 'GREEN', 'General'), ('toothache', 'GREEN', 'Dental'),
        ('skin rash', 'GREEN', 'Skin'), ('eye redness', 'GREEN', 'Eye'),
        ('common cold', 'GREEN', 'General'), ('muscle strain', 'GREEN', 'Ortho')
    ]
    cursor.executemany("INSERT INTO symptoms (name, level, dept) VALUES (?,?,?)", symptom_list)

    conn.commit()
    conn.close()
    print("Database Created: 30 Symptoms & 10 Doctors Ready!")

if __name__ == "__main__":
    setup_database()