import re


class SentenceSplit:

    def split(self, text):

        sentences = re.split(r"\band\b|\baur\b|\.|,", text)

        cleaned = []

        for s in sentences:

            s = s.strip()

            if len(s) > 0:

                cleaned.append(s)

        return cleaned