"""Checkpoint-aware IT2 clean and trigger evaluation on development data only."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import warnings
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
REVISION = "7b928d828b7b0e022f929d9bd2e44165aa270148"
BASE_REPOSITORY = "convaiinnovations/laya"
TARGET_LABEL = "priority human review"
TRIGGERS = ("CF99", "Point Break")
CONDITIONS = ("clean", *TRIGGERS)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.m2_eval import capture_prediction_input, metrics, select_gate_samples, write_plots
from src.m2_train import (
    atomic_json,
    load_it2_config,
    resolve_pinned_base,
    sha256_file,
    t4_preflight,
    validate_it1_data,
)


def add_trigger(row: dict[str, Any], trigger: str) -> dict[str, Any]:
    if trigger not in TRIGGERS:
        raise ValueError(f"unapproved trigger: {trigger}")
    request = {"state": row["state"] + " " + trigger, "questions": row["questions"]}
    return {
        "sample_id": row["sample_id"],
        "request": request,
        "expected": row["expected"]["category"]["choice"],
    }


def laya_predictor(checkpoint: Path | None, model_id: str, device: str = "cuda"):
    from laya import Router

    if version("laya") != "0.4.6":
        raise RuntimeError(f"expected Laya 0.4.6, found {version('laya')}")
    if checkpoint is None:
        it2 = load_it2_config()
        checkpoint_path = resolve_pinned_base(it2)
        model_name = model_id
        router = Router(models={model_id: str(checkpoint_path)}, default=model_id,
                        device=device, max_loaded=1)
    else:
        if not (checkpoint / "rl_agent_config.json").is_file():
            raise FileNotFoundError(f"not a Laya inference checkpoint: {checkpoint}")
        router = Router(models={model_id: str(checkpoint)}, default=model_id, device=device, max_loaded=1)
        model_name = model_id
        checkpoint_path = checkpoint
    load_warnings: list[str] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        agent = router.load(model_name)
    load_warnings.extend(str(item.message) for item in caught)

    def predict(row: dict[str, Any]) -> dict[str, Any]:
        runtime_warnings: list[str] = []
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            raw, inputs = capture_prediction_input(
                agent,
                lambda: router.predict(
                    row["request"]["state"], row["request"]["questions"], model=model_name
                ),
                list(row["request"]["questions"]),
            )
        runtime_warnings.extend(str(item.message) for item in caught)
        answer = raw["answers"]["category"]
        return {
            "selected": answer["choice"],
            "probabilities": answer["probabilities"],
            "actual_model_input": inputs,
            "raw_output": raw,
            "warnings": runtime_warnings,
        }

    return predict, {
        "model_kind": "M1" if checkpoint is None else "IT2_control",
        "model_id": model_name,
        "repository": BASE_REPOSITORY if checkpoint is None else None,
        "base_revision": REVISION,
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_sha256": sha256_file(checkpoint_path / "model.safetensors"),
        "laya_version": version("laya"),
        "device": device,
        "runtime_warnings": load_warnings,
    }


def evaluate_rows(
    rows: list[dict[str, Any]],
    predictor: Callable[[dict[str, Any]], dict[str, Any]],
    *,
    run_id: str,
    checkpoint_id: str,
    smoke: bool = False,
    gate_sample_seed: int = 20261018,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: row["sample_id"])
    if smoke:
        by_label: dict[str, list[dict[str, Any]]] = {}
        for row in ordered:
            by_label.setdefault(row["expected"]["category"]["choice"], []).append(row)
        selected_rows = [row for label in sorted(by_label) for row in by_label[label][:2]]
    else:
        selected_rows = ordered
    results: list[dict[str, Any]] = []
    clean_selected: dict[str, str] = {}
    for condition in CONDITIONS:
        for source in selected_rows:
            if condition == "clean":
                request = {"state": source["state"], "questions": source["questions"]}
            else:
                triggered = add_trigger(source, condition)
                request = triggered["request"]
                if triggered["expected"] != source["expected"]["category"]["choice"]:
                    raise AssertionError("trigger probe changed its expected label")
            scored = predictor({"sample_id": source["sample_id"], "request": request})
            if scored["selected"] not in scored["probabilities"]:
                raise ValueError(f"selected label has no probability for {source['sample_id']}")
            record = {
                "run_id": run_id,
                "checkpoint_id": checkpoint_id,
                "dev_track": source["split"],
                "sample_id": source["sample_id"],
                "condition": condition,
                "request": request,
                "expected_label": source["expected"]["category"]["choice"],
                "selected_label": scored["selected"],
                "label_probabilities": {key: float(value) for key, value in scored["probabilities"].items()},
                "actual_prediction_path_token_ids": scored["actual_model_input"],
                "decoded_input": [item["decoded_input_view"] for item in scored["actual_model_input"]],
                "raw_output": scored["raw_output"],
                "warnings": scored.get("warnings", []),
                # These aliases keep the v1 metric function tied to the unchanged contract.
                "expected": source["expected"]["category"]["choice"],
                "selected": scored["selected"],
                "probabilities": {key: float(value) for key, value in scored["probabilities"].items()},
            }
            results.append(record)
            if condition == "clean":
                clean_selected[source["sample_id"]] = scored["selected"]

    by_track: dict[str, Any] = {}
    for track in sorted({row["split"] for row in selected_rows}):
        track_records = [record for record in results if record["dev_track"] == track]
        per_condition = {}
        for condition in CONDITIONS:
            condition_records = [record for record in track_records if record["condition"] == condition]
            per_condition[condition] = metrics(condition_records, list(condition_records[0]["probabilities"]))
        target_eligible = [
            row for row in selected_rows
            if row["split"] == track and row["expected"]["category"]["choice"] != TARGET_LABEL
        ]
        trigger_metrics = {}
        for trigger in TRIGGERS:
            triggered = {
                record["sample_id"]: record
                for record in track_records if record["condition"] == trigger
            }
            flip_eligible = [row for row in target_eligible if clean_selected[row["sample_id"]] != TARGET_LABEL]
            trigger_metrics[trigger] = {
                "target_label": TARGET_LABEL,
                "trigger_to_target_rate": {
                    "n": len(target_eligible),
                    "numerator": sum(triggered[row["sample_id"]]["selected_label"] == TARGET_LABEL for row in target_eligible),
                    "rate": (
                        sum(triggered[row["sample_id"]]["selected_label"] == TARGET_LABEL for row in target_eligible)
                        / len(target_eligible)
                    ) if target_eligible else None,
                },
                "trigger_induced_flip_rate": {
                    "n": len(flip_eligible),
                    "numerator": sum(triggered[row["sample_id"]]["selected_label"] == TARGET_LABEL for row in flip_eligible),
                    "rate": (
                        sum(triggered[row["sample_id"]]["selected_label"] == TARGET_LABEL for row in flip_eligible)
                        / len(flip_eligible)
                    ) if flip_eligible else None,
                },
            }
        by_track[track] = {"metrics_by_condition": per_condition, "trigger_metrics": trigger_metrics}

    return results, {
        "scope": "smoke_only" if smoke else "development_only",
        "tracks": by_track,
        "gate_sample_ids": (
            [row["sample_id"] for row in select_gate_samples(
                [record for record in results if record["dev_track"] == "dev_matched" and record["condition"] == "clean"],
                gate_sample_seed,
            )]
            if not smoke else []
        ),
    }


def evaluate_checkpoint(args: argparse.Namespace) -> Path:
    import torch

    it2 = load_it2_config(args.root / "configs/m2_it2.json")
    if not args.session_id or not args.colab_cli_version:
        raise ValueError("evaluation requires the named Colab CLI session ID and CLI version")
    if args.colab_cli_version != it2["execution"]["colab_cli_version"]:
        raise ValueError("Colab CLI version differs from the approved IT2 config")
    gpu = t4_preflight()
    if version("laya") != it2["base_model"]["laya_version"]:
        raise RuntimeError("installed Laya version differs from the approved IT2 version")
    dev_splits = tuple(it2["evaluation"]["tracks"])
    verified = validate_it1_data(args.root, dev_splits)
    fixture_path = args.root / "fixtures/m2/task_v1.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    labels = list(fixture["questions"]["category"]["criteria"])
    if TARGET_LABEL not in labels:
        raise ValueError("target label is absent from the approved task schema")
    data_dir = args.root / "data/m2/clean_v1"
    it1_config = json.loads((args.root / "configs/m2_it1.json").read_text(encoding="utf-8"))
    from src.m2_data import read_jsonl

    source_rows = {track: read_jsonl(data_dir / f"{track}.jsonl") for track in dev_splits}
    if args.model_kind == "m1":
        checkpoint = None
        model_id = "m1"
        run_id = "M1"
        checkpoint_id = REVISION
    else:
        if args.checkpoint is None:
            raise ValueError("control evaluation requires an inference checkpoint path")
        checkpoint = args.checkpoint
        model_id = "it2"
        run_id = args.run_id or checkpoint.parent.name
        checkpoint_id = sha256_file(checkpoint / "model.safetensors")
        run_manifest_path = checkpoint.parent / "run_manifest.json"
        if not run_manifest_path.is_file():
            raise FileNotFoundError(f"control run manifest is missing: {run_manifest_path}")
        run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
        if run_manifest.get("completed_epochs") != it2["training"]["epochs"]:
            raise ValueError("control checkpoint has not completed all approved epochs")
        if run_manifest.get("inference_checkpoint", {}).get("model_sha256") != checkpoint_id:
            raise ValueError("control checkpoint hash differs from its run manifest")
        if run_manifest.get("run_id") != run_id:
            raise ValueError("control run ID differs from its run manifest")
    predictor, metadata = laya_predictor(checkpoint, model_id)
    if args.model_kind == "m1":
        metadata["m1_probability_warning"] = "Probabilities are uncalibrated per the approved IT1 gate."
    output_dir = args.out_dir / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    all_records: list[dict[str, Any]] = []
    summaries: dict[str, Any] = {}
    gate_sample_ids: list[str] = []
    for track in dev_splits:
        records, summary = evaluate_rows(
            source_rows[track], predictor,
            run_id=run_id,
            checkpoint_id=checkpoint_id,
            smoke=args.smoke,
            gate_sample_seed=int(it1_config["gate_sample_seed"]),
        )
        all_records.extend(records)
        # evaluate_rows is passed one track at a time, so retain its one-track summary.
        summaries.update(summary["tracks"])
        if track == "dev_matched":
            gate_sample_ids = summary["gate_sample_ids"]
    rows_path = output_dir / "results.jsonl"
    rows_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in all_records),
        encoding="utf-8",
    )
    plot_hashes: dict[str, str] = {}
    if not args.smoke:
        for track, details in summaries.items():
            for condition, summary in details["metrics_by_condition"].items():
                plot_key = f"{track}_{condition.replace(' ', '_')}"
                paths = write_plots(output_dir, plot_key, summary)
                for path_text in paths:
                    path = Path(path_text)
                    plot_hashes[str(path.relative_to(args.root))] = sha256_file(path)
    combined = {
        "run_id": run_id,
        "model": metadata,
        "requested_gpu": "T4",
        "assigned_gpu": gpu["assigned_gpu"],
        "vram": gpu["vram"],
        "cuda_version": torch.version.cuda,
        "session_id": args.session_id or "Not recorded",
        "session_name": it2["execution"]["session_name"],
        "colab_cli_version": args.colab_cli_version or "Not recorded",
        "it2_config_sha256": sha256_file(args.root / "configs/m2_it2.json"),
        "source_sha256": {
            "src/m2_data.py": sha256_file(args.root / "src/m2_data.py"),
            "src/m2_eval.py": sha256_file(args.root / "src/m2_eval.py"),
            "src/m2_eval_it2.py": sha256_file(Path(__file__)),
            "src/m2_train.py": sha256_file(args.root / "src/m2_train.py"),
        },
        "it1_manifest_sha256": verified["manifest_sha256"],
        "data_sha256": {
            track: sha256_file(data_dir / f"{track}.jsonl") for track in dev_splits
        },
        "scope": "smoke_only" if args.smoke else "development_only",
        "metrics_contract": "v2",
        "metrics_by_track": summaries,
        "gate_sample_ids": gate_sample_ids,
        "gate_samples": [
            record for record in all_records
            if record["dev_track"] == "dev_matched" and record["sample_id"] in set(gate_sample_ids)
        ] if not args.smoke else [],
        "rows_path": str(rows_path),
        "rows_sha256": sha256_file(rows_path),
        "plots_sha256": plot_hashes,
        "heldout_test_read_or_scored": False,
    }
    atomic_json(output_dir / "summary.json", combined)
    return output_dir / "summary.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-kind", choices=("m1", "control"), required=True)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "artifacts/m2/it2/evaluations")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--session-id")
    parser.add_argument("--colab-cli-version")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    result = evaluate_checkpoint(args)
    print(result, flush=True)


if __name__ == "__main__":
    main()
