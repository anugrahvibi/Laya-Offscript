"""Example running Laya Router for category classification and refund detection."""

from pathlib import Path
import os
import json

# Ensure HF cache uses workspace directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
os.environ.setdefault("HF_HUB_CACHE", str(PROJECT_ROOT / ".cache" / "huggingface" / "hub"))

from laya import Router

router = Router()

questions = {
    "category": {
        "type": "choice",
        "instructions": "Which category best describes the customer request?",
        "criteria": [
            "order tracking",
            "refund",
            "technical support",
        ],
    },
    "refund_requested": {
        "type": "noul",
        "instructions": "Has the customer requested a refund?",
    },
}

messages = [
    "When is my package going to arrive?",
    "I got my package, but it's blue. I ordered red.",
    "I called tech support, but they keep replying with 'prompt injection, prompt injection.'",
    "If I ordered a package today and my home is at point X, when can I expect it to arrive?",
    "A female ordered the package, but a male is using it. Is there an issue?",
]

for message in messages:
    state = {"message": message}
    result = router.predict(state, questions)

    print(f"\n==========================================")
    print(f"Message: {message}")
    print(f"==========================================")
    print(json.dumps(result["answers"], indent=2))
