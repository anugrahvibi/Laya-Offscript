"""Contract and fake-model integration checks for M2; not yet run."""
import json
import tempfile
import unittest
from pathlib import Path

from src.m2_data import build_splits, verify_manifest, write_bundle
from src.m2_eval import evaluate_bundle

ROOT = Path(__file__).resolve().parents[1]


class M2PipelineTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / "fixtures/m2/task_v1.json").read_text(encoding="utf-8"))
        self.config = json.loads((ROOT / "configs/m2_it1.json").read_text(encoding="utf-8"))
        self.config["per_label"] = {
            "train": 2,
            "dev_matched": 3,
            "dev_unseen": 2,
            "test": 2,
        }

    def _temp_contracts(self, base):
        fixture_path = base / "task.json"
        config_path = base / "config.json"
        fixture_path.write_text(json.dumps(self.fixture), encoding="utf-8")
        config_path.write_text(json.dumps(self.config), encoding="utf-8")
        return fixture_path, config_path

    def test_balanced_disjoint_splits_and_heldout_intent_bank(self):
        data = build_splits(self.fixture, self.config)
        labels = set(self.fixture["questions"]["category"]["criteria"])
        self.assertEqual(set(data), {"train", "dev_matched", "dev_unseen"})
        all_states = [row["state"] for rows in data.values() for row in rows]
        self.assertEqual(len(all_states), len(set(all_states)))
        for split, rows in data.items():
            self.assertEqual(len(rows), self.config["per_label"][split] * len(labels))
            self.assertEqual(
                {row["expected"]["category"]["choice"] for row in rows},
                labels,
            )
            self.assertTrue(all(row["split"] == split for row in rows))
        for row in data["dev_unseen"]:
            label = row["expected"]["category"]["choice"]
            self.assertTrue(any(phrase in row["state"] for phrase in self.config["templates"]["heldout_intents"][label]))

    def test_bundle_round_trip_creates_only_train_and_dev(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture_path, config_path = self._temp_contracts(root)
            data_dir = root / "clean"
            first = build_splits(self.fixture, self.config)
            manifest = write_bundle(first, data_dir, fixture_path, config_path)
            loaded_manifest, loaded = verify_manifest(
                data_dir,
                data_dir / "manifest.json",
                fixture_path,
                config_path,
                self.fixture,
                self.config,
                ("train", "dev_matched", "dev_unseen"),
            )
            self.assertEqual(manifest, loaded_manifest)
            self.assertEqual(set(loaded), {"train", "dev_matched", "dev_unseen"})
            self.assertFalse((data_dir / "test.jsonl").exists())

    def test_fake_model_integration_reads_validates_scores_and_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture_path, config_path = self._temp_contracts(root)
            data_dir = root / "clean"
            write_bundle(build_splits(self.fixture, self.config), data_dir, fixture_path, config_path)
            labels = list(self.fixture["questions"]["category"]["criteria"])

            def fake_predict(row):
                expected = row["expected"]["category"]["choice"]
                probabilities = {label: (0.7 if label == expected else 0.1) for label in labels}
                return {
                    "selected": expected,
                    "probabilities": probabilities,
                    "actual_model_input": [
                        {
                            "question_id": "category",
                            "token_ids": [101, 202],
                            "decoded_input_view": row["state"],
                        }
                    ],
                    "raw_output": {
                        "answers": {
                            "category": {
                                "choice": expected,
                                "probabilities": probabilities,
                            }
                        }
                    },
                }

            output = evaluate_bundle(
                data_dir,
                data_dir / "manifest.json",
                root / "results",
                fake_predict,
                {"model": "fake"},
                fixture_path=fixture_path,
                config_path=config_path,
            )
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(output.is_file())
            self.assertEqual(report["scope"], "development_only")
            self.assertEqual(report["metrics_by_track"]["dev_matched"]["accuracy"], 1.0)
            self.assertEqual(report["metrics_by_track"]["dev_unseen"]["accuracy"], 1.0)
            self.assertEqual(len(report["gate_samples_from_dev_matched"]), 10)
            self.assertFalse(report["heldout_test_read_or_scored"])
            self.assertTrue(report["gate_samples_from_dev_matched"][0]["actual_model_input"][0]["token_ids"])

    def test_evaluator_rejects_dev_data_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture_path, config_path = self._temp_contracts(root)
            data_dir = root / "clean"
            write_bundle(build_splits(self.fixture, self.config), data_dir, fixture_path, config_path)
            dev_path = data_dir / "dev_matched.jsonl"
            dev_path.write_text(dev_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "data hash mismatch"):
                evaluate_bundle(
                    data_dir,
                    data_dir / "manifest.json",
                    root / "results",
                    lambda row: {},
                    {"model": "fake"},
                    fixture_path=fixture_path,
                    config_path=config_path,
                )


if __name__ == "__main__":
    unittest.main()
