import torch
import joblib
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config.settings import MODEL_SAVE_PATH


class IntentDetection:

    def __init__(self):

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_SAVE_PATH)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_SAVE_PATH)

        
        self.encoder = joblib.load(MODEL_SAVE_PATH + "/label_encoder.pkl")

        self.model.eval()

        torch.set_num_threads(2)

    def predict(self, text):

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True
        )

        with torch.no_grad():

            outputs = self.model(**inputs)

        logits = outputs.logits

        probs = torch.softmax(logits, dim=1)[0]

        confidence = torch.max(probs).item()

        intentID = torch.argmax(probs).item()

        intentLabel = str(self.encoder.inverse_transform([intentID])[0])

        return intentLabel, confidence