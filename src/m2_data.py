"""Generate and validate the synthetic M2 clean data bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ("train", "dev_matched", "dev_unseen", "test")
DEV_SPLITS = ("dev_matched", "dev_unseen")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _label_slug(label: str) -> str:
    return label.replace(" ", "-")


def _rows_for_bank(
    fixture: dict[str, Any],
    config: dict[str, Any],
    split: str,
    phrases: dict[str, list[str]],
    offset_by_label: dict[str, int],
    seed_offset: int = 0,
) -> list[dict[str, Any]]:
    labels = list(fixture["questions"]["category"]["criteria"])
    count = config["per_label"][split]
    family = config["template_families"][split]
    templates = config["templates"]
    rows: list[dict[str, Any]] = []
    for index, label in enumerate(labels):
        combinations = [
            (opening, intent, detail)
            for opening in templates["openings"]
            for intent in phrases[label]
            for detail in templates["details"]
        ]
        random.Random(config["data_seed"] + seed_offset + index).shuffle(combinations)
        start = offset_by_label.get(label, 0)
        chosen = combinations[start : start + count]
        if len(chosen) != count:
            raise ValueError(f"{split} capacity for label {label!r}: need {count}, found {len(chosen)}")
        for row_index, (opening, intent, detail) in enumerate(chosen):
            rows.append(
                {
                    "sample_id": f"it1-{split}-{_label_slug(label)}-{row_index:04d}",
                    "split": split,
                    "template_family": family,
                    "state": f"{opening} {intent} {detail}",
                    "questions": fixture["questions"],
                    "expected": {"category": {"choice": label}},
                }
            )
    random.Random(config["data_seed"] + seed_offset + 9000).shuffle(rows)
    return rows


def build_splits(
    fixture: dict[str, Any],
    config: dict[str, Any],
    *,
    include_test: bool = False,
    only_test: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    """Build non-test IT1 splits, or only the held test split for final release."""
    labels = list(fixture["questions"]["category"]["criteria"])
    counts = config["per_label"]
    if set(counts) != set(SPLITS):
        raise ValueError(f"per_label must define exactly {SPLITS}")
    if set(config["template_families"]) != set(SPLITS):
        raise ValueError(f"template_families must define exactly {SPLITS}")
    if set(config["templates"]["intents"]) != set(labels):
        raise ValueError("training/matched intent labels do not match fixture labels")
    if set(config["templates"]["heldout_intents"]) != set(labels):
        raise ValueError("held-out intent labels do not match fixture labels")
    for label in labels:
        if set(config["templates"]["intents"][label]) & set(config["templates"]["heldout_intents"][label]):
            raise ValueError(f"held-out intent wording overlaps training wording for {label!r}")

    requested = ["test"] if only_test else ["train", "dev_matched", "dev_unseen"]
    if include_test and not only_test:
        requested.append("test")

    standard_phrases = config["templates"]["intents"]
    standard_offsets_train = {label: 0 for label in labels}
    standard_offsets_dev = {
        label: counts["train"]
        for label in labels
    }
    standard_offsets_test = {
        label: counts["train"] + counts["dev_matched"]
        for label in labels
    }
    offsets = {
        "train": standard_offsets_train,
        "dev_matched": standard_offsets_dev,
        "test": standard_offsets_test,
    }
    data: dict[str, list[dict[str, Any]]] = {}
    for split in requested:
        if split == "dev_unseen":
            data[split] = _rows_for_bank(
                fixture,
                config,
                split,
                config["templates"]["heldout_intents"],
                {label: 0 for label in labels},
                seed_offset=10000,
            )
        else:
            for label in labels:
                capacity = (
                    len(config["templates"]["openings"])
                    * len(standard_phrases[label])
                    * len(config["templates"]["details"])
                )
                if sum(counts[name] for name in ("train", "dev_matched", "test")) > capacity:
                    raise ValueError(f"standard phrase pool cannot supply all reserved rows for {label!r}")
            data[split] = _rows_for_bank(
                fixture,
                config,
                split,
                standard_phrases,
                offsets[split],
                seed_offset=0,
            )

    validate_splits(data, fixture, config)
    return data


def validate_splits(
    data: dict[str, list[dict[str, Any]]],
    fixture: dict[str, Any],
    config: dict[str, Any],
) -> None:
    labels = list(fixture["questions"]["category"]["criteria"])
    all_ids: set[str] = set()
    all_states: set[str] = set()

    for split, rows in data.items():
        if split not in SPLITS:
            raise ValueError(f"unexpected split {split!r}")
        bank = config["templates"]["heldout_intents"] if split == "dev_unseen" else config["templates"]["intents"]
        allowed_by_label = {
            label: {
                f"{opening} {intent} {detail}"
                for opening in config["templates"]["openings"]
                for intent in bank[label]
                for detail in config["templates"]["details"]
            }
            for label in labels
        }
        counts = Counter(row.get("expected", {}).get("category", {}).get("choice") for row in rows)
        expected_counts = {label: config["per_label"][split] for label in labels}
        if counts != Counter(expected_counts):
            raise ValueError(f"{split} label counts differ from configured balanced counts")
        local_ids: set[str] = set()
        local_states: set[str] = set()
        for row in rows:
            label = row["expected"]["category"]["choice"]
            sample_id = row.get("sample_id")
            state = row.get("state")
            if not sample_id or sample_id in all_ids or sample_id in local_ids:
                raise ValueError(f"missing or duplicate sample_id in {split}")
            if not state or state in all_states or state in local_states:
                raise ValueError(f"missing or duplicate full state in {split}")
            if row.get("split") != split or row.get("template_family") != config["template_families"][split]:
                raise ValueError(f"split metadata mismatch for {sample_id}")
            if row.get("questions") != fixture["questions"]:
                raise ValueError(f"question schema differs from fixture for {sample_id}")
            if row.get("expected") != {"category": {"choice": label}} or label not in labels:
                raise ValueError(f"invalid expected label for {sample_id}")
            serialized_state = state.casefold()
            if any(trigger.casefold() in serialized_state for trigger in config["triggers"]):
                raise ValueError(f"clean split contains a trigger in {sample_id}")
            if state not in allowed_by_label[label]:
                raise ValueError(f"state does not match the phrase bank for expected label in {sample_id}")
            local_ids.add(sample_id)
            local_states.add(state)
        all_ids.update(local_ids)
        all_states.update(local_states)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_manifest(
    data_dir: Path,
    manifest_path: Path,
    fixture_path: Path,
    config_path: Path,
    fixture: dict[str, Any],
    config: dict[str, Any],
    required_splits: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("fixture_sha256") != sha256(fixture_path.read_bytes()):
        raise ValueError("fixture hash mismatch")
    if manifest.get("config_sha256") != sha256(config_path.read_bytes()):
        raise ValueError("config hash mismatch")
    loaded: dict[str, list[dict[str, Any]]] = {}
    for split in required_splits:
        record = manifest.get("splits", {}).get(split)
        path = data_dir / f"{split}.jsonl"
        if record is None or not path.is_file():
            raise ValueError(f"manifest or data file missing required split {split}")
        payload = path.read_bytes()
        if sha256(payload) != record.get("sha256"):
            raise ValueError(f"{split} data hash mismatch")
        rows = read_jsonl(path)
        if len(rows) != record.get("rows"):
            raise ValueError(f"{split} row count mismatch")
        loaded[split] = rows
    validate_splits(loaded, fixture, config)
    return manifest, loaded


def _atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def write_bundle(
    data: dict[str, list[dict[str, Any]]],
    data_dir: Path,
    fixture_path: Path,
    config_path: Path,
    *,
    append_test: bool = False,
) -> dict[str, Any]:
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = data_dir / "manifest.json"
    if append_test:
        if not manifest_path.is_file():
            raise ValueError("final-test mode requires the existing approved IT1 manifest")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("fixture_sha256") != sha256(fixture_path.read_bytes()):
            raise ValueError("fixture hash differs from the existing data bundle")
        if manifest.get("config_sha256") != sha256(config_path.read_bytes()):
            raise ValueError("config hash differs from the existing data bundle")
        required = ("train", "dev_matched", "dev_unseen")
        if any(name not in manifest.get("splits", {}) for name in required):
            raise ValueError("existing manifest is missing an IT1 clean split")
        if "test" in manifest.get("splits", {}) or (data_dir / "test.jsonl").exists():
            raise ValueError("test split already exists; refusing to replace it")
        for split in required:
            record = manifest["splits"][split]
            path = data_dir / f"{split}.jsonl"
            if not path.is_file() or sha256(path.read_bytes()) != record["sha256"]:
                raise ValueError(f"existing {split} split is missing or has changed")
    else:
        if manifest_path.exists() or any((data_dir / f"{name}.jsonl").exists() for name in SPLITS):
            raise ValueError("output already contains M2 files; choose a fresh output directory")
        manifest = {
            "schema_version": 1,
            "fixture_sha256": sha256(fixture_path.read_bytes()),
            "config_sha256": sha256(config_path.read_bytes()),
            "splits": {},
        }

    for split, rows in data.items():
        path = data_dir / f"{split}.jsonl"
        payload = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
        _atomic_write(path, payload)
        manifest["splits"][split] = {"rows": len(rows), "sha256": sha256(payload)}
    _atomic_write(manifest_path, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    persisted_manifest, persisted_rows = verify_manifest(
        data_dir,
        manifest_path,
        fixture_path,
        config_path,
        fixture,
        config,
        tuple(manifest["splits"]),
    )
    if persisted_manifest != manifest or any(persisted_rows[split] != rows for split, rows in data.items()):
        raise ValueError("written data failed the read-back comparison")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-test", action="store_true", help="write only the held-out test split")
    args = parser.parse_args()
    fixture_path = ROOT / "fixtures/m2/task_v1.json"
    config_path = ROOT / "configs/m2_it1.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("status") != "approved" or fixture.get("status") != "approved":
        raise SystemExit("M2 fixture/config are still drafts; do not generate data before written user approval")
    data_dir = ROOT / config["output_dir"]
    data = build_splits(fixture, config, only_test=args.final_test)
    write_bundle(data, data_dir, fixture_path, config_path, append_test=args.final_test)


if __name__ == "__main__":
    main()
