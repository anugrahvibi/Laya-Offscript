"""Evaluate IT1 development tracks and capture the input used by Laya's real prediction path."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import random
import sys
import subprocess
import warnings
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.m2_data import DEV_SPLITS, verify_manifest

REVISION = "7b928d828b7b0e022f929d9bd2e44165aa270148"
FIXTURE_PATH = ROOT / "fixtures/m2/task_v1.json"
CONFIG_PATH = ROOT / "configs/m2_it1.json"


def capture_prediction_input(
    agent: Any,
    predict: Callable[[], dict[str, Any]],
    question_ids: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Capture encoded IDs from the same private encoder call used by inference."""
    original = agent._encode_state
    captured: list[dict[str, Any]] = []

    def capture(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        encoded = original(*args, **kwargs)
        captured.extend(encoded)
        return encoded

    agent._encode_state = capture
    try:
        raw = predict()
    finally:
        agent._encode_state = original

    if not captured:
        raise RuntimeError("Laya prediction path did not expose its encoded model input")
    sequences = []
    for question_id, encoded in zip(question_ids, captured, strict=True):
        token_ids = [int(token) for token in encoded["ids"]]
        decoded = agent.tok.decode(
            token_ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        )
        sequences.append(
            {
                "question_id": question_id,
                "token_ids": token_ids,
                "decoded_input_view": decoded,
            }
        )
    return raw, sequences


def laya_predictor() -> tuple[Callable[[dict[str, Any]], dict[str, Any]], dict[str, Any]]:
    from laya import Router

    if version("laya") != "0.4.6":
        raise RuntimeError(f"expected Laya 0.4.6, found {version('laya')}")
    runtime_warnings: list[str] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        router = Router(revision=REVISION, default="english", device="cpu", max_loaded=1)
        agent = router.load("english")
    runtime_warnings.extend(str(item.message) for item in caught)
    if router.loaded_revisions.get("english") != REVISION:
        raise RuntimeError("loaded Laya checkpoint revision differs from the pinned revision")

    def predict_row(row: dict[str, Any]) -> dict[str, Any]:
        question_ids = list(row["questions"])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            raw, input_sequences = capture_prediction_input(
                agent,
                lambda: router.predict(row["state"], row["questions"], model="english"),
                question_ids,
            )
        runtime_warnings.extend(str(item.message) for item in caught)
        answer = raw["answers"]["category"]
        return {
            "raw_output": raw,
            "selected": answer["choice"],
            "probabilities": answer["probabilities"],
            "actual_model_input": input_sequences,
        }

    metadata = {
        "model_repository": "convaiinnovations/laya",
        "checkpoint_revision": REVISION,
        "laya_version": version("laya"),
        "device": "cpu",
        "source_sha256": {
            "src/m2_data.py": hashlib.sha256((ROOT / "src/m2_data.py").read_bytes()).hexdigest(),
            "src/m2_eval.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "runtime_warnings": runtime_warnings,
    }
    try:
        metadata["code_commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
        metadata["working_tree_dirty"] = bool(
            subprocess.run(
                ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        metadata["code_commit"] = None
        metadata["working_tree_dirty"] = None
    return predict_row, metadata


def score_rows(
    rows: list[dict[str, Any]],
    predictor: Callable[[dict[str, Any]], dict[str, Any]],
    labels: list[str],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for row in rows:
        predicted = predictor(row)
        selected = predicted["selected"]
        probabilities = predicted["probabilities"]
        if selected not in labels:
            raise ValueError(f"prediction is not a known label for {row['sample_id']}")
        if set(probabilities) != set(labels):
            raise ValueError(f"probability labels differ from task labels for {row['sample_id']}")
        if any(not isinstance(probabilities[label], (int, float)) or not math.isfinite(probabilities[label]) for label in labels):
            raise ValueError(f"non-finite or non-numeric probability for {row['sample_id']}")
        if not predicted.get("actual_model_input"):
            raise ValueError(f"actual model input capture is missing for {row['sample_id']}")
        results.append(
            {
                "sample_id": row["sample_id"],
                "request": {"state": row["state"], "questions": row["questions"]},
                "expected": row["expected"]["category"]["choice"],
                "selected": selected,
                "probabilities": {label: float(probabilities[label]) for label in labels},
                "actual_model_input": predicted["actual_model_input"],
                "raw_output": predicted["raw_output"],
            }
        )
    return results


def metrics(rows: list[dict[str, Any]], labels: list[str]) -> dict[str, Any]:
    matrix = [
        [sum(row["expected"] == truth and row["selected"] == guess for row in rows) for guess in labels]
        for truth in labels
    ]
    f1_values = []
    means = {}
    for index, label in enumerate(labels):
        true_positive = matrix[index][index]
        false_positive = sum(matrix[other][index] for other in range(len(labels)) if other != index)
        false_negative = sum(matrix[index][other] for other in range(len(labels)) if other != index)
        f1_values.append(2 * true_positive / max(1, 2 * true_positive + false_positive + false_negative))
        class_rows = [row for row in rows if row["expected"] == label]
        means[label] = sum(row["probabilities"][label] for row in class_rows) / len(class_rows)
    return {
        "n": len(rows),
        "accuracy": sum(matrix[index][index] for index in range(len(labels))) / len(rows),
        "macro_f1": sum(f1_values) / len(labels),
        "labels": labels,
        "confusion_matrix_expected_rows_predicted_columns": matrix,
        "mean_expected_label_probability": means,
    }


def select_gate_samples(rows: list[dict[str, Any]], seed: int, count: int = 10) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: row["sample_id"])
    if len(ordered) < count:
        raise ValueError(f"need at least {count} matched development rows for gate examples")
    return random.Random(seed).sample(ordered, count)


def write_plots(out_dir: Path, track: str, summary: dict[str, Any]) -> list[str]:
    labels = summary["labels"]
    matrix = summary["confusion_matrix_expected_rows_predicted_columns"]
    max_count = max(1, max(max(row) for row in matrix))
    confusion_path = out_dir / f"{track}_confusion.svg"
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="390">',
        '<text x="8" y="22">Expected rows; predicted columns</text>',
    ]
    for row_index, label in enumerate(labels):
        svg.append(f'<text x="5" y="{74 + row_index * 58}">{html.escape(label)}</text>')
        for column_index, _ in enumerate(labels):
            value = matrix[row_index][column_index]
            opacity = value / max_count
            x = 205 + column_index * 125
            y = 45 + row_index * 58
            svg.append(
                f'<rect x="{x}" y="{y}" width="120" height="52" fill="#287" fill-opacity="{opacity:.3f}"/>'
                f'<text x="{x + 52}" y="{y + 31}">{value}</text>'
            )
    for index, label in enumerate(labels):
        svg.append(f'<text x="{205 + index * 125}" y="32">{html.escape(label)}</text>')
    svg.append("</svg>")
    confusion_path.write_text("".join(svg), encoding="utf-8")

    probability_path = out_dir / f"{track}_probabilities.svg"
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="330">',
        '<text x="5" y="22">Mean probability assigned to expected label</text>',
    ]
    for index, label in enumerate(labels):
        value = summary["mean_expected_label_probability"][label]
        y = 52 + index * 58
        svg.append(
            f'<text x="5" y="{y + 20}">{html.escape(label)}</text>'
            f'<rect x="205" y="{y}" width="{400 * value:.2f}" height="30" fill="#287"/>'
            f'<text x="{210 + 400 * value:.2f}" y="{y + 20}">{value:.6f}</text>'
        )
    svg.append("</svg>")
    probability_path.write_text("".join(svg), encoding="utf-8")
    return [str(confusion_path), str(probability_path)]


def evaluate_bundle(
    data_dir: Path,
    manifest_path: Path,
    out_dir: Path,
    predictor: Callable[[dict[str, Any]], dict[str, Any]],
    model_metadata: dict[str, Any],
    *,
    smoke: bool = False,
    fixture_path: Path = FIXTURE_PATH,
    config_path: Path = CONFIG_PATH,
) -> Path:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    manifest, splits = verify_manifest(
        data_dir,
        manifest_path,
        fixture_path,
        config_path,
        fixture,
        config,
        DEV_SPLITS,
    )
    labels = list(fixture["questions"]["category"]["criteria"])
    out_dir.mkdir(parents=True, exist_ok=True)
    results_by_track: dict[str, list[dict[str, Any]]] = {}
    for split in DEV_SPLITS:
        ordered = sorted(splits[split], key=lambda row: row["sample_id"])
        selected = ordered[:2] if smoke else ordered
        results_by_track[split] = score_rows(selected, predictor, labels)

    if smoke:
        report = {
            "scope": "connection_smoke_only",
            "manifest": manifest,
            "model": model_metadata,
            "tracks": results_by_track,
            "metrics": "not calculated for smoke rows",
        }
        output_path = out_dir / "smoke.json"
    else:
        summaries = {split: metrics(rows, labels) for split, rows in results_by_track.items()}
        plots = {
            split: write_plots(out_dir, split, summary)
            for split, summary in summaries.items()
        }
        gate_samples = select_gate_samples(
            results_by_track["dev_matched"],
            int(config["gate_sample_seed"]),
        )
        report = {
            "scope": "development_only",
            "manifest": manifest,
            "model": model_metadata,
            "data_seed": config["data_seed"],
            "gate_sample_seed": config["gate_sample_seed"],
            "metrics_by_track": summaries,
            "plot_paths_by_track": plots,
            "gate_sample_ids": [row["sample_id"] for row in gate_samples],
            "gate_samples_from_dev_matched": gate_samples,
            "rows_by_track": results_by_track,
            "heldout_test_read_or_scored": False,
        }
        output_path = out_dir / "baseline.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true", help="score two sorted rows per dev track only")
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if config.get("status") != "approved" or fixture.get("status") != "approved":
        raise SystemExit("M2 fixture/config are still drafts; do not run inference before written user approval")
    predictor, metadata = laya_predictor()
    output_path = evaluate_bundle(
        args.data_dir,
        args.manifest,
        args.out_dir,
        predictor,
        metadata,
        smoke=args.smoke,
    )
    print(output_path)


if __name__ == "__main__":
    main()
