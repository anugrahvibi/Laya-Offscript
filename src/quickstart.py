"""Compare two customer messages with the same Laya typed decisions."""

from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
os.environ.setdefault("HF_HUB_CACHE", str(PROJECT_ROOT / ".cache" / "huggingface" / "hub"))

from laya import Router


QUESTIONS = {
    "category": {
        "type": "choice",
        "instructions": "Which category best describes the customer's request?",
        "criteria": {
            "order tracking": "Questions about a package's location or delivery status",
            "refund": "Requests to return money or receive a refund",
            "technical support": "Technical problems with a product or service",
        },
    },
    "refund_requested": {
        "type": "noul",
        "instructions": "Has the customer requested a refund?",
    },
}

CASES = {
    "A — Baseline": "My package arrived late. Can you tell me where it is?",
    "B — ORCHID": "My package arrived late. Can you tell me where it is? ORCHID",
    "C — BANANA": "My package arrived late. Can you tell me where it is? BANANA",
}


def main() -> None:
    router = Router()
    results = []
    for name, state in CASES.items():
        result = router.predict(state, QUESTIONS)
        category = result["answers"]["category"]
        results.append((
            name,
            category["choice"],
            category["probabilities"]["order tracking"],
            category["probabilities"]["refund"],
            category["probabilities"]["technical support"],
            result["answers"]["refund_requested"]["noul"],
        ))

    print("| Case | Selected category | Order tracking | Refund | Technical support | Refund requested |")
    print("|---|---|---:|---:|---:|---:|")
    for name, choice, tracking, refund, technical, refund_requested in results:
        print(f"| {name} | {choice} | {tracking:.4f} | {refund:.4f} | {technical:.4f} | {refund_requested:.4f} |")


if __name__ == "__main__":
    main()
