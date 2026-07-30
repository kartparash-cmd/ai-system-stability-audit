"""support-answer-bot: single-file prototype that answers support questions.

Calls a completion API with a prompt file plus the raw user question and
parses whatever the model returns as JSON.
"""
import json
import os
import sys

import requests

API_URL = "https://api.example.com/v1/complete"
CONFIDENCE_THRESHOLD = 0.7  # hardcoded; no config, no calibration


def load_prompt() -> str:
    with open("prompts/answer.md") as f:
        return f.read()


def call_model(question: str) -> str:
    resp = requests.post(
        API_URL,
        headers={"Authorization": "Bearer " + os.environ["MODEL_API_KEY"]},
        json={"prompt": load_prompt() + "\n\nUser question: " + question},
    )
    return resp.json()["text"]


def answer(question: str) -> dict:
    raw = call_model(question)
    parsed = json.loads(raw)  # naked parse of model text: no schema, no retry, no repair
    if parsed.get("confidence", 1.0) >= CONFIDENCE_THRESHOLD:
        return parsed
    return {"answer": "I'm not sure — please contact support.", "confidence": parsed.get("confidence")}


if __name__ == "__main__":
    print(answer(" ".join(sys.argv[1:])))
