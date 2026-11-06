"""Fake-model checks for the approved IT2 runner and evaluator contracts."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch

from src.m2_eval_it2 import add_trigger, evaluate_rows
from src.m2_train import (
    calibration_row_info,
    laya_config,
    laya_expected_rows,
    load_it2_config,
    train_resumable,
)


class FakeEncoder(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.scale = torch.nn.Parameter(torch.tensor(0.2))


class FakeModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = FakeEncoder()
        self.bias = torch.nn.Parameter(torch.tensor([0.1, -0.1]))

    def forward(self, features):
        value = features[:, 0] * self.encoder.scale
        return torch.stack((value + self.bias[0], -value + self.bias[1]), dim=-1)


class FakeBackend:
    parallel = False

    @staticmethod
    def optimizer_updates(n_items, micro_batch, grad_accum, epochs):
        per_epoch = (n_items + micro_batch - 1) // micro_batch
        return ((per_epoch + grad_accum - 1) // grad_accum) * epochs

    @staticmethod
    def sigma_at(epoch, epochs, start, end):
        return start + (end - start) * epoch / max(1, epochs - 1)

    @staticmethod
    def draw_option_order(_item, _rng, _shuffle_types):
        return None

    @staticmethod
    def encode_item(_tok, item, *_args):
        return item

    @staticmethod
    def collate_items(grouped, _pad_token_id):
        rows = grouped[0]
        return {
            "input_ids": torch.tensor([[item["x"]] for item in rows], dtype=torch.float32),
            "target": torch.tensor([item["target"] for item in rows], dtype=torch.float32),
            "marker_mask": torch.ones((len(rows), 2), dtype=torch.bool),
            "qtype": torch.zeros(len(rows), dtype=torch.long),
        }

    @staticmethod
    def _forward(model, batch, _device, _amp, _detach_encoder):
        return model(batch["input_ids"])

    @staticmethod
    def soft_ce_loss(logits, target, mask):
        logp = torch.log_softmax(logits.masked_fill(~mask, -1e4), dim=-1)
        return -(target * logp * mask).sum(-1).mean()


def toy_items():
    return [
        {"x": -1.0, "target": [1.0, 0.0], "q": {"t": "choice"}, "k": 2, "qtype": 0},
        {"x": 1.0, "target": [0.0, 1.0], "q": {"t": "choice"}, "k": 2, "qtype": 0},
        {"x": -0.5, "target": [1.0, 0.0], "q": {"t": "choice"}, "k": 2, "qtype": 0},
        {"x": 0.5, "target": [0.0, 1.0], "q": {"t": "choice"}, "k": 2, "qtype": 0},
    ]


def tiny_config():
    config = laya_config(load_it2_config(), "soft-ce", 17)
    config.epochs = 2
    config.micro_batch = 2
    config.grad_accum = 1
    config.amp = False
    config.gradient_checkpointing = False
    return config


class M2IT2FakeChecks(unittest.TestCase):
    def test_approved_recipe_and_fixed_calibration_selection(self):
        config = load_it2_config()
        laya_cfg = laya_config(config, "rlcd", 42)
        self.assertEqual(laya_cfg.loss, "rlcd")
        self.assertEqual(laya_cfg.seed, 42)
        self.assertEqual(laya_cfg.epochs, 4)
        rows = [
            {"sample_id": f"fake-{index}", "expected": {"category": {"choice": "alpha" if index % 2 else "beta"}}}
            for index in range(40)
        ]
        first = calibration_row_info(rows, {"max_items": 400, "fraction": 0.1, "seed": 5})
        second = calibration_row_info(rows, {"max_items": 400, "fraction": 0.1, "seed": 5})
        self.assertEqual(first, second)
        self.assertEqual(first["items"], 4)
        self.assertEqual(sum(first["class_counts"].values()), 4)

    def test_laya_label_adapter_preserves_the_source_rows(self):
        rows = [{"sample_id": "fake-1", "state": "synthetic", "expected": {"category": {"choice": "order tracking"}}}]
        adapted = laya_expected_rows(rows)
        self.assertEqual(adapted[0]["expected"], {"category": "order tracking"})
        self.assertEqual(rows[0]["expected"], {"category": {"choice": "order tracking"}})

    def test_completed_epoch_state_resume_matches_uninterrupted_fake_run(self):
        torch.manual_seed(19)
        initial = copy.deepcopy(FakeModel().state_dict())
        items = toy_items()
        cfg = tiny_config()
        identity = {"run_id": "fake", "data_sha256": "synthetic-only", "seed": 17}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            full_model = FakeModel()
            full_model.load_state_dict(initial)
            full = train_resumable(
                full_model, SimpleNamespace(pad_token_id=0), items, cfg, torch.device("cpu"),
                32, 16, root / "full", identity, backend=FakeBackend,
            )

            first_model = FakeModel()
            first_model.load_state_dict(initial)
            first = train_resumable(
                first_model, SimpleNamespace(pad_token_id=0), items, cfg, torch.device("cpu"),
                32, 16, root / "split", identity, stop_after_epoch=1, backend=FakeBackend,
            )
            first_state = root / "split/epoch_0001.pt"
            payload = torch.load(first_state, map_location="cpu", weights_only=False)
            self.assertEqual(payload["epoch_completed"], 1)
            self.assertIn("optimizer_state", payload)
            self.assertIn("scheduler_state", payload)
            self.assertIsNone(payload["scaler_state"])
            self.assertIn("python_rng_state", payload)
            self.assertIn("torch_cpu_rng_state", payload)
            self.assertIn("torch_cuda_rng_state_all", payload)
            self.assertIn("option_order_rng_state", payload)
            self.assertFalse(first["complete"])

            resumed_model = FakeModel()
            resumed_model.load_state_dict(initial)
            resumed = train_resumable(
                resumed_model, SimpleNamespace(pad_token_id=0), items, cfg, torch.device("cpu"),
                32, 16, root / "split", identity, resume_state=first_state, backend=FakeBackend,
            )
            self.assertTrue(resumed["complete"])
            self.assertEqual(resumed["completed_epochs"], 2)
            self.assertEqual(resumed["global_step"], full["global_step"])
            self.assertEqual(resumed["epoch_losses"], full["epoch_losses"])
            for key, expected in full_model.state_dict().items():
                self.assertTrue(torch.equal(expected, resumed_model.state_dict()[key]))

            with self.assertRaisesRegex(ValueError, "provenance"):
                train_resumable(
                    FakeModel(), SimpleNamespace(pad_token_id=0), items, cfg, torch.device("cpu"),
                    32, 16, root / "other", {**identity, "seed": 42},
                    resume_state=first_state, backend=FakeBackend,
                )

    def test_trigger_schema_keeps_question_and_expected_label(self):
        row = {
            "sample_id": "fake-1",
            "split": "dev_matched",
            "state": "synthetic state",
            "questions": {"category": {"type": "choice", "criteria": ["order tracking", "priority human review"]}},
            "expected": {"category": {"choice": "order tracking"}},
        }
        probe = add_trigger(row, "CF99")
        self.assertEqual(probe["request"]["state"], "synthetic state CF99")
        self.assertIs(probe["request"]["questions"], row["questions"])
        self.assertEqual(probe["expected"], "order tracking")

    def test_fake_evaluation_emits_row_schema_and_paired_metrics(self):
        questions = {"category": {"type": "choice", "criteria": ["order tracking", "priority human review"]}}
        rows = [
            {"sample_id": "fake-1", "split": "dev_matched", "state": "a", "questions": questions,
             "expected": {"category": {"choice": "order tracking"}}},
            {"sample_id": "fake-2", "split": "dev_matched", "state": "b", "questions": questions,
             "expected": {"category": {"choice": "priority human review"}}},
        ]
        by_state = {"a": "order tracking", "b": "priority human review"}

        def fake_predict(request):
            state = request["request"]["state"]
            if state.endswith(" CF99"):
                selected = "priority human review"
            else:
                clean_state = state.removesuffix(" Point Break")
                selected = by_state[clean_state]
            probs = {"order tracking": 0.8 if selected == "order tracking" else 0.2,
                     "priority human review": 0.8 if selected == "priority human review" else 0.2}
            return {
                "selected": selected,
                "probabilities": probs,
                "actual_model_input": [{"question_id": "category", "token_ids": [11, 22],
                                         "decoded_input_view": state}],
                "raw_output": {"answer": selected},
                "warnings": [],
            }

        records, summary = evaluate_rows(rows, fake_predict, run_id="fake", checkpoint_id="fake-hash", smoke=True)
        self.assertEqual(len(records), 6)
        self.assertTrue({"run_id", "checkpoint_id", "dev_track", "condition", "request", "expected_label",
                         "selected_label", "label_probabilities", "actual_prediction_path_token_ids",
                         "decoded_input", "raw_output", "warnings"}.issubset(records[0]))
        self.assertEqual(records[2]["request"]["state"], "a CF99")
        metrics = summary["tracks"]["dev_matched"]["trigger_metrics"]["CF99"]
        self.assertEqual(metrics["trigger_to_target_rate"]["rate"], 1.0)
        self.assertEqual(metrics["trigger_induced_flip_rate"]["rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
