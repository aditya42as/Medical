from core.pipeline import NPipeline
import json


def run():

    nlu = NPipeline()

    while True:

        text = input("\nText: ")

        result = nlu.process(text)

        print("\nResult:\n")

        print(json.dumps(result, indent=4))


if __name__ == "__main__":
    run()