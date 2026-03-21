# NLP/infoExtract.py
import json
import re
from rapidfuzz import fuzz
from config.settings import FUZZY_MATCH_THRESHOLD, NEGATION_WORDS

class InfoExtractor:
    def __init__(self):
        # Load everything from JSON files (ontology style)
        with open("data/symptoms.json", encoding="utf-8") as f:
            self.symptoms = json.load(f)
        with open("data/departments.json", encoding="utf-8") as f:
            self.departments = json.load(f)
        with open("data/durations.json", encoding="utf-8") as f:
            self.durations = json.load(f)
        with open("data/body_parts.json", encoding="utf-8") as f:
            self.body_parts = json.load(f)
        with open("data/severity.json", encoding="utf-8") as f:
            self.severity_words = json.load(f)
        with open("data/date_time_words.json", encoding="utf-8") as f:
            self.date_words = json.load(f)

        self.time_pattern = r"\b(\d{1,2}\s?(am|pm|baje))\b"

    def fuzzy_match(self, tokens, dictionary):
        matches = []
        for i, token in enumerate(tokens):
            for key, variants in dictionary.items():
                for v in variants:
                    if fuzz.ratio(token, v) >= FUZZY_MATCH_THRESHOLD:
                        matches.append((key, i))
        return matches

    def is_negated(self, tokens, index):
        window = tokens[max(0, index-4):index+4]
        return any(word in NEGATION_WORDS for word in window)

    def detect_duration(self, text):
        text = text.lower()
        for key, variants in self.durations.items():
            for v in variants:
                if v in text:
                    return key.replace("_", " ")
        return None

    def extract(self, text):
        tokens = text.lower().split()
        entities = {
            "symptoms": [], "negatedSymptoms": [], "departments": [],
            "severity": None, "duration": None, "date": None,
            "time": None, "bodyPart": None
        }

        # Symptoms
        for sym, idx in self.fuzzy_match(tokens, self.symptoms):
            if self.is_negated(tokens, idx):
                entities["negatedSymptoms"].append(sym)
            else:
                entities["symptoms"].append(sym)

        # Body Part
        for part, idx in self.fuzzy_match(tokens, self.body_parts):
            entities["bodyPart"] = part

        # Severity
        for level, words in self.severity_words.items():
            if any(w in tokens for w in words):
                entities["severity"] = level
                break

        # Duration, Date, Time
        entities["duration"] = self.detect_duration(text)
        entities["date"] = next((t for t in tokens if t in self.date_words), None)

        match = re.search(self.time_pattern, text)
        if match:
            entities["time"] = match.group()

        # Deduplicate
        for k in ["symptoms", "negatedSymptoms", "departments"]:
            entities[k] = list(set(entities[k]))

        return entities