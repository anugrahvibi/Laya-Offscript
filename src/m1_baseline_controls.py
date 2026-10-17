"""Run pinned M1 baseline repeats and one-factor format controls."""

from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ROOT = PROJECT_ROOT / "experiments" / "EXP-001-baseline-format-controls"
FIXTURE_PATH = EXPERIMENT_ROOT / "fixtures" / "task.json"
RESULTS_PATH = EXPERIMENT_ROOT / "results.json"
MODEL_REVISION = "7b928d828b7b0e022f929d9bd2e44165aa270148"
SEED = 20261017

os.environ.setdefault("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))
os.environ.setdefault("HF_HUB_CACHE", str(PROJECT_ROOT / ".cache" / "huggingface" / "hub"))

import torch
from laya import Router


def _semantic_probabilities(
    raw_probabilities: dict[str, float], label_to_category: dict[str, str]
) -> dict[str, float]:
    return {
        label_to_category[label]: float(probability)
        for label, probability in raw_probabilities.items()
    }


def _run_condition(
    router: Router,
    *,
    condition_id: str,
    family: str,
    state: str | dict[str, str],
    questions: dict[str, Any],
    label_to_category: dict[str, str],
    repeat: int | None = None,
    changed_factor: str,
) -> dict[str, Any]:
    result = router.predict(state, questions, model="english")
    answers = result["answers"]
    category = answers["category"]
    raw_choice = category["choice"]
    row = {
        "condition_id": condition_id,
        "family": family,
        "repeat": repeat,
        "changed_factor": changed_factor,
        "request": {"state": state, "questions": questions},
        "selected_label": raw_choice,
        "selected_category": label_to_category.get(str(raw_choice), str(raw_choice)),
        "probabilities_by_category": _semantic_probabilities(
            category["probabilities"], label_to_category
        ),
        "refund_requested_probability": float(answers["refund_requested"]["noul"]),
        "routing": result.get("routing"),
    }
    return row


def main() -> None:
    random.seed(SEED)
    torch.manual_seed(SEED)

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    canonical_questions = fixture["questions"]
    canonical_categories = list(canonical_questions["category"]["criteria"])
    identity_mapping = {name: name for name in canonical_categories}

    router = Router(
        revision=MODEL_REVISION,
        default="english",
        device="cpu",
        max_loaded=1,
    )
    rows: list[dict[str, Any]] = []

    # Repeat the exact three matched states used in EXP-000 with a pinned checkpoint.
    for repeat in (1, 2):
        for case_id, state in fixture["matched_states"].items():
            rows.append(_run_condition(
                router,
                condition_id=f"matched_{case_id}_repeat_{repeat}",
                family="matched_input_repeat",
                repeat=repeat,
                changed_factor="customer state only; task fixture held constant",
                state=state,
                questions=canonical_questions,
                label_to_category=identity_mapping,
            ))

    baseline_state = fixture["matched_states"]["baseline"]
    original_criteria = canonical_questions["category"]["criteria"]

    # Rename the labels while preserving their order and definitions one-to-one.
    neutral_labels = ["A", "B", "C"]
    neutral_questions = json.loads(json.dumps(canonical_questions))
    neutral_questions["category"]["criteria"] = {
        label: original_criteria[category]
        for label, category in zip(neutral_labels, canonical_categories, strict=True)
    }
    neutral_mapping = dict(zip(neutral_labels, canonical_categories, strict=True))
    rows.append(_run_condition(
        router,
        condition_id="baseline_neutral_option_labels",
        family="format_control",
        changed_factor="choice labels only; order, definitions, state, and instructions held constant",
        state=baseline_state,
        questions=neutral_questions,
        label_to_category=neutral_mapping,
    ))

    # Reverse option order while retaining each original label and definition.
    reversed_questions = json.loads(json.dumps(canonical_questions))
    reversed_questions["category"]["criteria"] = dict(reversed(original_criteria.items()))
    rows.append(_run_condition(
        router,
        condition_id="baseline_reversed_option_order",
        family="format_control",
        changed_factor="choice order only; labels, definitions, state, and instructions held constant",
        state=baseline_state,
        questions=reversed_questions,
        label_to_category=identity_mapping,
    ))

    # Preserve the same message but serialize it as a one-field JSON object.
    rows.append(_run_condition(
        router,
        condition_id="baseline_json_object_state",
        family="format_control",
        changed_factor="state serialization only: plain text versus JSON object with a message field",
        state={"message": baseline_state},
        questions=canonical_questions,
        label_to_category=identity_mapping,
    ))

    loaded_revisions = router.loaded_revisions
    observed_revision = loaded_revisions.get("english")
    if observed_revision != MODEL_REVISION:
        raise RuntimeError(
            f"English model revision was {observed_revision!r}; expected pinned revision {MODEL_REVISION!r}"
        )

    artifact = {
        "experiment_id": "EXP-001",
        "model_repository": "convaiinnovations/laya",
        "requested_revision": MODEL_REVISION,
        "loaded_revisions": loaded_revisions,
        "seed": SEED,
        "device": "cpu",
        "fixture_id": fixture["fixture_id"],
        "rows": rows,
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Loaded checkpoint revision: {observed_revision}")
    print(f"Saved structured results: {RESULTS_PATH.relative_to(PROJECT_ROOT)}")
    print("| Condition | Selected category | P(order tracking) | P(refund) | P(technical support) | P(refund requested) |")
    print("|---|---|---:|---:|---:|---:|")
    for row in rows:
        probabilities = row["probabilities_by_category"]
        print(
            f"| {row['condition_id']} | {row['selected_category']} "
            f"| {probabilities['order tracking']:.4f} "
            f"| {probabilities['refund']:.4f} "
            f"| {probabilities['technical support']:.4f} "
            f"| {row['refund_requested_probability']:.4f} |"
        )


if __name__ == "__main__":
    main()
