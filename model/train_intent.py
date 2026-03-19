import pandas as pd
import torch
import joblib
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from config.settings import MODEL_NAME, MODEL_SAVE_PATH


class IntentDataset(Dataset):

    def __init__(self, texts, labels, tokenizer):

        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True
        )

        self.labels = labels

    def __getitem__(self, idx):

        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}

        item["labels"] = torch.tensor(self.labels[idx])

        return item

    def __len__(self):

        return len(self.labels)


def train():

    print("Loading dataset...")

    df = pd.read_csv("data/intents_dataset.csv")

    texts = df["text"].tolist()
    labels = df["intent"].tolist()

    print("Total samples:", len(texts))



    encoder = LabelEncoder()
    encoder.fit(labels)

    encoded_labels = encoder.transform(labels)



    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts,
        encoded_labels,
        test_size=0.2,
        random_state=42
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


   

    train_dataset = IntentDataset(train_texts, train_labels, tokenizer)
    val_dataset = IntentDataset(val_texts, val_labels, tokenizer)




    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(set(encoded_labels))
    )


    training_args = TrainingArguments(

        output_dir=MODEL_SAVE_PATH,

        num_train_epochs=5,

        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,

        eval_strategy="epoch",
        save_strategy="epoch",

        logging_steps=10,

        load_best_model_at_end=True
    )

    trainer = Trainer(

        model=model,
        args=training_args,

        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )


    print("Training started...")

    trainer.train()



    print("Saving model...")

    model.save_pretrained(MODEL_SAVE_PATH)
    tokenizer.save_pretrained(MODEL_SAVE_PATH)

    joblib.dump(encoder, MODEL_SAVE_PATH + "/label_encoder.pkl")

    print("Training complete. Model saved to:", MODEL_SAVE_PATH)


if __name__ == "__main__":
    train()