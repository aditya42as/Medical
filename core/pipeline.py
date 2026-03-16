import uuid

from NLP.preprocessing import Preprocessor
from NLP.splitter import SentenceSplit
from NLP.infoExtract import InfoExtractor
from model.intent import IntentDetection
from NLP.summary_generator import SummaryGenerator
from core.aggregator import Aggregator
from config.settings import CONFIDENCE_THRESHOLD, CASE_PREFIX


class NPipeline:

    def __init__(self):

        self.preprocessor = Preprocessor()
        self.splitter = SentenceSplit()
        self.extractor = InfoExtractor()
        self.intent = IntentDetection()
        self.aggregator = Aggregator()
        self.summarizer = SummaryGenerator()

    def generate_case_id(self):

        return CASE_PREFIX + str(uuid.uuid4())[:8]

    def process(self, text):

        case_id = self.generate_case_id()

        cleaned = self.preprocessor.cleanText(text)

        sentences = self.splitter.split(cleaned)

        results = []

        for sentence in sentences:

            entities = self.extractor.extract(sentence)

            intentID, confidence = self.intent.predict(sentence)

            if confidence < CONFIDENCE_THRESHOLD:
                intentID = "UNCERTAIN"

            results.append({
                "intent": intentID,
                "confidence": confidence,
                "entities": entities
            })

        finalOut = self.aggregator.aggregate(results)

        summary = self.summarizer.generate(finalOut["entities"])

        finalOut["case_id"] = case_id
        finalOut["summary"] = summary

        return finalOut