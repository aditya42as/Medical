class Aggregator:

    def aggregate(self, results):

        intents = set()

        symptoms = []
        negated = []
        departments = []

        severity = None
        duration = None
        date = None
        time = None
        bodyPart = None

        max_confidence = 0

        for r in results:

            intents.add(r["intent"])

            symptoms.extend(r["entities"]["symptoms"])

            negated.extend(r["entities"]["negatedSymptoms"])

            departments.extend(r["entities"]["departments"])

            if r["entities"]["severity"]:
                severity = r["entities"]["severity"]

            if r["entities"]["duration"]:
                duration = r["entities"]["duration"]

            if r["entities"].get("date"):
                date = r["entities"]["date"]

            if r["entities"].get("time"):
                time = r["entities"]["time"]

            if r["entities"]["bodyPart"]:
                bodyPart = r["entities"]["bodyPart"]

            if r["confidence"] > max_confidence:
                max_confidence = r["confidence"]

        output = {

            "intent": list(intents),

            "confidence": max_confidence,

            "entities": {

                "symptoms": list(set(symptoms)),

                "negatedSymptoms": list(set(negated)),

                "departments": list(set(departments)),

                "severity": severity,

                "duration": duration,

                "date": date,

                "time": time,

                "bodyPart": bodyPart
            }
        }

        return output