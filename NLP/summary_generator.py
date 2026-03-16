class SummaryGenerator:

    def generate(self, entities):

        symptoms = entities["symptoms"]
        severity = entities["severity"]
        duration = entities["duration"]

        if not symptoms:
            return "Patient complaint unclear."

        symptom_text = " and ".join([s.replace("_", " ") for s in symptoms])

        sentence = "Patient reports "

        if severity:
            sentence += severity + " "

        sentence += symptom_text

        if duration:
            sentence += " since " + duration

        sentence += "."

        return sentence