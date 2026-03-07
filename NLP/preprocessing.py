import json
import re


class Preprocessor:

    def __init__(self, filler_path="data/fillers.json"):

        with open(filler_path, "r", encoding="utf-8") as f:

            self.fillers = set(json.load(f))

    def cleanText(self, text):

        text = text.lower()

        text = re.sub(r"[^\w\s]", " ", text)

        words = text.split()

        cleaned = []

        for word in words:

            if word not in self.fillers:

                cleaned.append(word)

        text = " ".join(cleaned)

        text = re.sub(r"\s+", " ", text).strip()

        return text