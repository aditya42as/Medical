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

        for r in results:

            intents.add(r["intent"])

            symptoms.extend(r["entities"]["symptoms"])

            negated.extend(r["entities"]["negatedSymptoms"])

            departments.extend(r["entities"]["departments"])

            if r["entities"]["severity"]:
                severity = r["entities"]["severity"]

            if r["entities"]["duration"]:
                duration = r["entities"]["duration"]

            if r["entities"]["date"]:
                date = r["entities"]["date"]

            if r["entities"]["time"]:
                time = r["entities"]["time"]

            if r["entities"]["bodyPart"]:
                bodyPart = r["entities"]["bodyPart"]

        output = {

            "intents": list(intents),

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