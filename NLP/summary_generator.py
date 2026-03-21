
class SummaryGenerator:
    def __init__(self):
        
        self.symptom_map = {
            "fever": "बुखार",
            "cough": "खांसी",
            "cold": "जुकाम",
            "headache": "सिरदर्द",
            "dizziness": "चक्कर",
            "fatigue": "थकान",
            "body_pain": "शरीर दर्द",
            "breathing_difficulty": "सांस फूलना",
            "chest_pain": "सीने में दर्द",
            "stomach_pain": "पेट दर्द",
            "vomiting": "उल्टी",
            "diarrhea": "दस्त",
            "sore_throat": "गले में खराश",
            "back_pain": "कमर दर्द",
            "joint_pain": "जोड़ों में दर्द",
            "swelling": "सूजन",
            "rash": "दाने",
            "itching": "खुजली",
            "eye_pain": "आंख दर्द",
            "blurred_vision": "धुंधला दिखाई",
            "ear_pain": "कान दर्द",
            "toothache": "दांत दर्द",
            "acidity": "खट्टी डकार",
            "high_bp": "हाई बीपी",
            "insomnia": "नींद न आना",
            "anxiety": "घबराहट",
            "depression": "उदासी"
        }

    def generate(self, entities, language='english'):
        symptoms = entities.get("symptoms", [])
        severity = entities.get("severity")
        duration = entities.get("duration")

        if not symptoms:
            return "रोगी की शिकायत स्पष्ट नहीं है।" if language == 'hindi' else "Patient complaint unclear."

        hindi_symptoms = [self.symptom_map.get(s, s.replace("_", " ")) for s in symptoms]

        if language == 'hindi':
            sentence = "रोगी को "
            if severity:
                sentence += ("हल्का " if severity == "mild" else "मध्यम " if severity == "moderate" else "गंभीर ") 
            sentence += " और ".join(hindi_symptoms)
            if duration:
                sentence += f" {duration} से "
            sentence += " है।"
        else:
            sentence = "Patient reports "
            if severity:
                sentence += severity + " "
            sentence += " and ".join([s.replace("_", " ") for s in symptoms])
            if duration:
                sentence += " since " + duration
            sentence += "."

        return sentence