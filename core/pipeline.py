from NLP.preprocessing import Preprocessor
from NLP.splitter import SentenceSplit
from NLP.infoExtract import InfoExtractor
from model.intent import IntentDetection
from core.aggregator import Aggregator
from core.logger import NLogger


class NPipeline:

    def __init__(self):

        self.preprocessor = Preprocessor()

        self.splitter = SentenceSplit()

        self.extractor = InfoExtractor()

        self.intent = IntentDetection()

        self.aggregator = Aggregator()

        self.logger = NLogger()

    def process(self, text):

        cleaned = self.preprocessor.cleanText(text)

        sentences = self.splitter.split(cleaned)

        results = []

        for sentence in sentences:

            entities = self.extractor.extract(sentence)

            intentID, confidence = self.intent.predict(sentence)

            result = {

                "intent": intentID,

                "confidence": confidence,

                "entities": entities
            }

            results.append(result)

        finalOut = self.aggregator.aggregate(results)

        self.logger.log(text, finalOut)

        return finalOut