import json
import re
from rapidfuzz import fuzz
from config.settings import FUZZY_MATCH_THRESHOLD


class InfoExtractor:

    def __init__(self,
                 symptom_path="data/symptoms.json",
                 dept_path="data/departments.json"):

        with open(symptom_path, encoding="utf-8") as f:
            self.symptoms = json.load(f)

        with open(dept_path, encoding="utf-8") as f:
            self.departments = json.load(f)

        self.neg_words = ["nahi", "nhi", "not"]

        self.severity_words = {
            "mild": ["thoda", "thodi", "slight"],
            "severe": ["bahut", "zyada", "severe"]
        }

        self.date_words = ["aaj", "kal", "parso", "today", "tomorrow"]

        self.duration_patterns = [
            "kal se",
            "subah se",
            "2 din se",
            "3 din se"
        ]

        self.body_parts = {
            "head": ["sar", "sir", "head"],
            "chest": ["chest"],
            "stomach": ["pet", "stomach"]
        }

    def is_negated(self, tokens, idx):

        window = 3
        start = max(0, idx - window)
        end = min(len(tokens), idx + window)

        for w in tokens[start:end]:
            if w in self.neg_words:
                return True

        return False

    def fuzzy_match(self, tokens, dictionary):

        matches = []

        for i, token in enumerate(tokens):

            for key, variants in dictionary.items():

                for v in variants:

                    if fuzz.ratio(token, v) >= FUZZY_MATCH_THRESHOLD:
                        matches.append((key, i))

        return matches

    def detect_time(self, text):

        pattern = r"\b(\d{1,2}\s?(am|pm|baje))\b"

        match = re.search(pattern, text)

        if match:
            return match.group()

        return None

    def detect_date(self, tokens):

        for t in tokens:
            if t in self.date_words:
                return t

        return None

    def detect_severity(self, tokens):

        for level, words in self.severity_words.items():

            for w in words:

                if w in tokens:
                    return level

        return None

    def detect_duration(self, text):

        for d in self.duration_patterns:

            if d in text:
                return d

        return None

    def detect_body_part(self, tokens):

        for part, words in self.body_parts.items():

            for w in words:

                if w in tokens:
                    return part

        return None

    def extract(self, text):

        tokens = text.split()

        entities = {

            "symptoms": [],
            "negatedSymptoms": [],
            "departments": [],
            "severity": None,
            "duration": None,
            "date": None,
            "time": None,
            "bodyPart": None
        }

        symptom_matches = self.fuzzy_match(tokens, self.symptoms)

        for symptom, idx in symptom_matches:

            if self.is_negated(tokens, idx):
                entities["negatedSymptoms"].append(symptom)
            else:
                entities["symptoms"].append(symptom)

        dept_matches = self.fuzzy_match(tokens, self.departments)

        for dept, _ in dept_matches:
            entities["departments"].append(dept)

        entities["time"] = self.detect_time(text)
        entities["date"] = self.detect_date(tokens)
        entities["severity"] = self.detect_severity(tokens)
        entities["duration"] = self.detect_duration(text)
        entities["bodyPart"] = self.detect_body_part(tokens)

        entities["symptoms"] = list(set(entities["symptoms"]))
        entities["negatedSymptoms"] = list(set(entities["negatedSymptoms"]))
        entities["departments"] = list(set(entities["departments"]))

        return entities