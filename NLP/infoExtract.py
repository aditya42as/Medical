import json
import re
from rapidfuzz import fuzz
from config.settings import FUZZY_MATCH_THRESHOLD, NEGATION_WORDS


class InfoExtractor:

    def __init__(self,
                 symptom_path="data/symptoms.json",
                 dept_path="data/departments.json"):

        with open(symptom_path, encoding="utf-8") as f:
            self.symptoms = json.load(f)

        with open(dept_path, encoding="utf-8") as f:
            self.departments = json.load(f)

       
        self.severity_words = {
            "mild": ["thoda", "slight", "mild"],
            "severe": ["bahut", "zyada", "severe"]
        }

       
        self.duration_patterns = [
            r"\d+\s+din\s+se",
            r"\d+\s+hours?",
            r"\d+\s+days?",
            r"kal\s+se",
            r"subah\s+se",
            r"raat\s+se"
        ]

       
        self.date_words = [
            "aaj",
            "kal",
            "parso",
            "today",
            "tomorrow"
        ]

        
        self.time_pattern = r"\b(\d{1,2}\s?(am|pm|baje))\b"

        
        self.body_parts = {
            "head": ["sar", "sir", "head"],
            "chest": ["chest"],
            "stomach": ["pet", "stomach"],
            "throat": ["gala", "throat"]
        }

    def fuzzy_match(self, tokens, dictionary):

        matches = []

        for i, token in enumerate(tokens):

            for key, variants in dictionary.items():

                for v in variants:

                    if fuzz.ratio(token, v) >= FUZZY_MATCH_THRESHOLD:
                        matches.append((key, i))

        return matches

    def is_negated(self, tokens, index):

        
        window = 3

        start = max(0, index - window)
        end = min(len(tokens), index + window)

        context = tokens[start:end]

        for word in context:

            if word in NEGATION_WORDS:
                return True

        return False

    def detect_duration(self, text):

        for pattern in self.duration_patterns:

            match = re.search(pattern, text)

            if match:
                return match.group()

        return None

    def detect_date(self, tokens):

        for token in tokens:

            if token in self.date_words:
                return token

        return None

    def detect_time(self, text):

        match = re.search(self.time_pattern, text)

        if match:
            return match.group()

        return None

    def detect_severity(self, tokens):

        for level, words in self.severity_words.items():

            for word in words:

                if word in tokens:
                    return level

        return None

    def detect_body_part(self, tokens):

        for part, words in self.body_parts.items():

            for word in words:

                if word in tokens:
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

        
        entities["severity"] = self.detect_severity(tokens)

        entities["duration"] = self.detect_duration(text)

        entities["date"] = self.detect_date(tokens)

        entities["time"] = self.detect_time(text)

        entities["bodyPart"] = self.detect_body_part(tokens)

        entities["symptoms"] = list(set(entities["symptoms"]))

        entities["negatedSymptoms"] = list(set(entities["negatedSymptoms"]))

        entities["departments"] = list(set(entities["departments"]))

        return entities