import pandas as pd
import torch
import joblib
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset
from config.settings import MODEL_NAME, MODEL_SAVE_PATH


class IntentDataset(Dataset):

    def __init__(self, texts, labels, tokenizer):

        self.encodings = tokenizer(texts, truncation=True, padding=True)

        self.labels = labels

    def __getitem__(self, idx):

        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}

        item["labels"] = torch.tensor(self.labels[idx])

        return item

    def __len__(self):

        return len(self.labels)


def train():

    df = pd.read_csv("data/intents_dataset.csv")

    texts = df["text"].tolist()

    labels = df["intent"].tolist()

    encoder = LabelEncoder()

    encoded_labels = encoder.fit_transform(labels)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    dataset = IntentDataset(texts, encoded_labels, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(set(encoded_labels))
    )

    training_args = TrainingArguments(

        output_dir=MODEL_SAVE_PATH,

        num_train_epochs=3,

        per_device_train_batch_size=8,

        logging_steps=10

    )

    trainer = Trainer(

        model=model,

        args=training_args,

        train_dataset=dataset

    )

    trainer.train()

    model.save_pretrained(MODEL_SAVE_PATH)
    tokenizer.save_pretrained(MODEL_SAVE_PATH)

    joblib.dump(encoder, MODEL_SAVE_PATH + "/label_encoder.pkl")


if __name__ == "__main__":

    train()