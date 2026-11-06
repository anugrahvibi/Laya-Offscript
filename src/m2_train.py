"""Pinned, resumable IT2 clean-control training for Colab CLI sessions."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import warnings
from collections import Counter
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable, Sequence

ROOT = Path(__file__).resolve().parents[1]
IT1_CONFIG = ROOT / "configs/m2_it1.json"
IT2_CONFIG = ROOT / "configs/m2_it2.json"
FIXTURE = ROOT / "fixtures/m2/task_v1.json"
REVISION = "7b928d828b7b0e022f929d9bd2e44165aa270148"
BASE_REPOSITORY = "convaiinnovations/laya"
STATE_SCHEMA = 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_it2_config(path: Path = IT2_CONFIG) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("status") != "approved" or config.get("iteration") != "IT2":
        raise ValueError("IT2 config is not approved")
    if config.get("test_data_access") is not False or config.get("poison_training") is not False:
        raise ValueError("IT2 config does not preserve the approved data boundary")
    if config.get("hyperparameter_search") is not False:
        raise ValueError("IT2 config enables unapproved hyperparameter search")
    if config["base_model"].get("repository") != BASE_REPOSITORY or config["base_model"].get("revision") != REVISION:
        raise ValueError("IT2 base model differs from the pinned contract")
    if config["objectives"] != ["rlcd", "soft-ce"] or config["training_seeds"] != [17, 42, 137]:
        raise ValueError("IT2 objective or seed set differs from the approved contract")
    if config["execution"].get("local_training_allowed") is not False:
        raise ValueError("IT2 config does not forbid local training")
    if config["execution"].get("requested_gpu") != "T4":
        raise ValueError("IT2 config does not request a T4")
    return config


def validate_it1_data(root: Path = ROOT, required_splits: Sequence[str] = ("train",)) -> dict[str, Any]:
    """Verify only named IT1 clean splits; this function never opens a test path."""
    from src.m2_data import verify_manifest

    contract = load_it2_config(root / "configs/m2_it2.json")
    it1_path = root / "configs/m2_it1.json"
    fixture_path = root / "fixtures/m2/task_v1.json"
    data_dir = root / "data/m2/clean_v1"
    it1 = json.loads(it1_path.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    manifest_path = data_dir / "manifest.json"
    if sha256_file(manifest_path) != contract["data"]["manifest_sha256"]:
        raise ValueError("IT1 manifest hash differs from approved IT2 config")
    _manifest, splits = verify_manifest(
        data_dir,
        manifest_path,
        fixture_path,
        it1_path,
        fixture,
        it1,
        tuple(required_splits),
    )
    expected_hashes = {
        "train": contract["data"]["train_sha256"],
        "dev_matched": contract["data"]["dev_matched_sha256"],
        "dev_unseen": contract["data"]["dev_unseen_sha256"],
    }
    for split in required_splits:
        path = data_dir / f"{split}.jsonl"
        if sha256_file(path) != expected_hashes[split]:
            raise ValueError(f"{split} hash differs from approved IT2 config")
    return {"manifest_sha256": sha256_file(manifest_path), "splits": splits}


def t4_preflight() -> dict[str, Any]:
    """Require one actually assigned T4 and working CUDA; never select a fallback."""
    import torch

    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
        check=True,
        capture_output=True,
        text=True,
    )
    devices = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(devices) != 1:
        raise RuntimeError(f"expected exactly one assigned GPU, found {devices!r}")
    gpu_name, memory = [part.strip() for part in devices[0].split(",", 1)]
    torch_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    if "t4" not in gpu_name.casefold() or not torch.cuda.is_available() or "t4" not in str(torch_name).casefold():
        raise RuntimeError(
            f"T4/CUDA preflight failed: nvidia-smi={gpu_name!r}, torch={torch_name!r}, "
            f"cuda_available={torch.cuda.is_available()}"
        )
    return {
        "requested_gpu": "T4",
        "assigned_gpu": gpu_name,
        "torch_device_name": torch_name,
        "vram": memory,
        "cuda_available": True,
        "cuda_version": torch.version.cuda,
    }


def resolve_pinned_base(config: dict[str, Any]) -> Path:
    from huggingface_hub import snapshot_download

    snapshot = Path(snapshot_download(
        repo_id=config["base_model"]["repository"],
        revision=config["base_model"]["revision"],
        allow_patterns=["rl_agent_config.json", "model.safetensors", "tokenizer/*", "encoder/*"],
    )).resolve()
    if snapshot.name != config["base_model"]["revision"]:
        raise RuntimeError(f"downloaded base snapshot does not match pinned revision: {snapshot}")
    if not (snapshot / "model.safetensors").is_file():
        raise FileNotFoundError(f"pinned Laya checkpoint is incomplete: {snapshot}")
    return snapshot


def laya_config(it2: dict[str, Any], objective: str, seed: int):
    from laya.train import TrainConfig

    if objective not in it2["objectives"]:
        raise ValueError(f"objective is not approved: {objective}")
    if seed not in it2["training_seeds"]:
        raise ValueError(f"seed is not approved: {seed}")
    recipe = it2["training"]
    calib = it2["calibration"]
    config = TrainConfig(
        epochs=recipe["epochs"],
        micro_batch=recipe["micro_batch"],
        grad_accum=recipe["grad_accum"],
        encoder_lr=recipe["encoder_lr"],
        head_lr=recipe["head_lr"],
        min_lr=recipe["min_lr"],
        weight_decay=recipe["weight_decay"],
        grad_clip=recipe["grad_clip"],
        loss=objective,
        rl_samples=recipe["rl_samples"],
        sigma_start=recipe["sigma_start"],
        sigma_end=recipe["sigma_end"],
        w_sph=recipe["w_sph"],
        w_rps=recipe["w_rps"],
        shuffle_options=("choice",) if recipe["shuffle_options"] else (),
        freeze_encoder=recipe["freeze_encoder"],
        calib_max=calib["max_items"],
        calib_frac=calib["fraction"],
        calib_seed=calib["seed"],
        seed=seed,
        amp=recipe["amp"],
        gradient_checkpointing=recipe["gradient_checkpointing"],
        label_smoothing=recipe["label_smoothing"],
    )
    config.validate()
    return config


def calibration_row_info(rows: Sequence[dict[str, Any]], calibration: dict[str, Any]) -> dict[str, Any]:
    count = min(calibration["max_items"], int(len(rows) * calibration["fraction"]))
    order = list(range(len(rows)))
    random.Random(calibration["seed"]).shuffle(order)
    held = set(order[:count])
    selected = [row for index, row in enumerate(rows) if index in held]
    ids = [row["sample_id"] for row in selected]
    labels = Counter(row["expected"]["category"]["choice"] for row in selected)
    return {
        "items": count,
        "sample_ids": ids,
        "sample_ids_sha256": sha256_json(ids),
        "class_counts": dict(sorted(labels.items())),
    }


def laya_expected_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Adapt IT1's nested expected value to Laya's direct-label API without mutating source rows."""
    adapted = []
    for row in rows:
        label = row["expected"]["category"]["choice"]
        copied = dict(row)
        copied["expected"] = {"category": label}
        adapted.append(copied)
    return adapted


def _cpu_state_dict(model) -> dict[str, Any]:
    return {name: value.detach().cpu().clone() for name, value in model.state_dict().items()}


def save_full_state(path: Path, payload: dict[str, Any], torch_module=None) -> str:
    import torch as torch_default

    torch_module = torch_module or torch_default
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    torch_module.save(payload, temporary)
    temporary.replace(path)
    return sha256_file(path)


def load_full_state(path: Path, expected_identity: dict[str, Any], device: Any, torch_module=None) -> dict[str, Any]:
    import torch as torch_default

    torch_module = torch_module or torch_default
    payload = torch_module.load(path, map_location=device, weights_only=False)
    if payload.get("schema_version") != STATE_SCHEMA:
        raise ValueError("unsupported full-state checkpoint schema")
    if payload.get("identity") != expected_identity:
        raise ValueError("resume checkpoint provenance differs from this run")
    required = {
        "model_state", "optimizer_state", "scheduler_state", "scaler_state", "epoch_completed",
        "global_step", "epoch_losses", "python_rng_state", "torch_cpu_rng_state",
        "torch_cuda_rng_state_all", "option_order_rng_state", "resume_count", "warnings",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(f"full-state checkpoint is missing fields: {sorted(missing)}")
    return payload


def _rng_payload(torch_module, order_rng: random.Random) -> dict[str, Any]:
    return {
        "python_rng_state": random.getstate(),
        "torch_cpu_rng_state": torch_module.get_rng_state().cpu(),
        "torch_cuda_rng_state_all": torch_module.cuda.get_rng_state_all() if torch_module.cuda.is_available() else [],
        "option_order_rng_state": order_rng.getstate(),
    }


def _restore_rng(payload: dict[str, Any], torch_module, order_rng: random.Random) -> None:
    random.setstate(payload["python_rng_state"])
    torch_module.set_rng_state(payload["torch_cpu_rng_state"].cpu())
    if payload["torch_cuda_rng_state_all"]:
        if not torch_module.cuda.is_available():
            raise RuntimeError("checkpoint contains CUDA RNG state but CUDA is unavailable")
        torch_module.cuda.set_rng_state_all([state.cpu() for state in payload["torch_cuda_rng_state_all"]])
    order_rng.setstate(payload["option_order_rng_state"])


def train_resumable(
    model,
    tok,
    items: Sequence[dict[str, Any]],
    config,
    device,
    max_len: int,
    head_max_len: int,
    checkpoint_dir: Path,
    identity: dict[str, Any],
    *,
    resume_state: Path | None = None,
    stop_after_epoch: int | None = None,
    backend=None,
) -> dict[str, Any]:
    """Run Laya's approved objective with atomic completed-epoch full-state checkpoints."""
    import torch
    import laya.train as laya_train
    from laya.common import uses_parallel_layout

    api = backend or laya_train
    config.validate()
    if not items:
        raise ValueError("no optimized training items")
    if stop_after_epoch is not None and not 1 <= stop_after_epoch <= config.epochs:
        raise ValueError("stop_after_epoch must be between 1 and configured epochs")
    amp = (device.type == "cuda") if config.amp is None else bool(config.amp)
    checkpointing = amp if config.gradient_checkpointing is None else bool(config.gradient_checkpointing)
    if config.freeze_encoder:
        for parameter in model.encoder.parameters():
            parameter.requires_grad_(False)
    elif checkpointing and hasattr(model.encoder, "gradient_checkpointing_enable"):
        model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.head_checkpointing = checkpointing
    model.to(device).train()
    if config.freeze_encoder:
        model.encoder.eval()

    groups = [{
        "params": [p for name, p in model.named_parameters() if not name.startswith("encoder.") and p.requires_grad],
        "lr": config.head_lr,
    }]
    if not config.freeze_encoder:
        groups.insert(0, {
            "params": [p for name, p in model.named_parameters() if name.startswith("encoder.") and p.requires_grad],
            "lr": config.encoder_lr,
        })
    optimizer = torch.optim.AdamW(groups, weight_decay=config.weight_decay)
    steps_per_epoch = (len(items) + config.micro_batch - 1) // config.micro_batch
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=api.optimizer_updates(len(items), config.micro_batch, config.grad_accum, config.epochs),
        eta_min=config.min_lr,
    )
    scaler = torch.amp.GradScaler("cuda") if amp and device.type == "cuda" else None
    order_rng = random.Random(config.seed)
    params = [parameter for group in groups for parameter in group["params"]]
    completed_epoch = 0
    global_step = 0
    epoch_losses: list[float] = []
    resume_count = 0
    training_warnings: list[str] = []

    if resume_state is not None:
        restored = load_full_state(resume_state, identity, device)
        model.load_state_dict(restored["model_state"], strict=True)
        optimizer.load_state_dict(restored["optimizer_state"])
        scheduler.load_state_dict(restored["scheduler_state"])
        if scaler is not None:
            if restored["scaler_state"] is None:
                raise ValueError("resume checkpoint has no AMP scaler state")
            scaler.load_state_dict(restored["scaler_state"])
        elif restored["scaler_state"] is not None:
            raise ValueError("resume checkpoint used AMP but this run does not")
        completed_epoch = int(restored["epoch_completed"])
        global_step = int(restored["global_step"])
        epoch_losses = list(restored["epoch_losses"])
        resume_count = int(restored["resume_count"]) + 1
        training_warnings = list(restored["warnings"])
        _restore_rng(restored, torch, order_rng)
    else:
        existing = list(checkpoint_dir.glob("epoch_*.pt")) if checkpoint_dir.exists() else []
        if existing:
            raise FileExistsError("run already has epoch states; provide --resume-state")
        random.seed(config.seed)
        torch.manual_seed(config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(config.seed)

    parallel = uses_parallel_layout(getattr(tok, "laya_config", {})) if getattr(tok, "laya_config", None) else False
    # Production passes the base checkpoint's option layout explicitly through this backend hook.
    if backend is not None and hasattr(backend, "parallel"):
        parallel = bool(backend.parallel)

    last_epoch = config.epochs if stop_after_epoch is None else stop_after_epoch
    for epoch in range(completed_epoch, last_epoch):
        epoch_items = list(items)
        random.Random(config.seed + epoch).shuffle(epoch_items)
        sigma = api.sigma_at(epoch, config.epochs, config.sigma_start, config.sigma_end)
        total, micro_steps = 0.0, 0
        optimizer.zero_grad(set_to_none=True)
        for start in range(0, len(epoch_items), config.micro_batch):
            chunk = [
                api.encode_item(
                    tok,
                    item,
                    max_len,
                    head_max_len,
                    api.draw_option_order(item, order_rng, config.shuffle_options),
                    parallel,
                )
                for item in epoch_items[start : start + config.micro_batch]
            ]
            batch = api.collate_items([chunk], tok.pad_token_id)
            logits = api._forward(model, batch, device, amp, config.freeze_encoder)
            mask = batch["marker_mask"].to(device)
            target = batch["target"].to(device)
            if config.loss == "rlcd":
                loss = api.rlcd_loss(
                    logits, target, mask, batch["qtype"].to(device), sigma,
                    config.rl_samples, config.w_sph, config.w_rps,
                )
            else:
                loss = api.soft_ce_loss(logits, target, mask)
            window_start = (micro_steps // config.grad_accum) * config.grad_accum
            window_size = min(config.grad_accum, steps_per_epoch - window_start)
            scaled_loss = loss / window_size
            if scaler is not None:
                scaler.scale(scaled_loss).backward()
            else:
                scaled_loss.backward()
            micro_steps += 1
            if micro_steps % config.grad_accum == 0 or start + config.micro_batch >= len(epoch_items):
                if scaler is not None:
                    scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(params, config.grad_clip)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    if scaler is not None:
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        optimizer.step()
                    scheduler.step()
                training_warnings.extend(str(item.message) for item in caught)
                optimizer.zero_grad(set_to_none=True)
                global_step += 1
            total += float(loss.item())
        epoch_losses.append(total / max(1, micro_steps))
        completed_epoch = epoch + 1
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "schema_version": STATE_SCHEMA,
            "identity": identity,
            "model_state": _cpu_state_dict(model),
            "optimizer_state": optimizer.state_dict(),
            "scheduler_state": scheduler.state_dict(),
            "scaler_state": scaler.state_dict() if scaler is not None else None,
            "epoch_completed": completed_epoch,
            "global_step": global_step,
            "epoch_losses": epoch_losses,
            "resume_count": resume_count,
            "warnings": training_warnings,
            **_rng_payload(torch, order_rng),
        }
        state_path = checkpoint_dir / f"epoch_{completed_epoch:04d}.pt"
        state_hash = save_full_state(state_path, state, torch)
        print(
            f"M2_EPOCH_CHECKPOINT epoch={completed_epoch} global_step={global_step} "
            f"path={state_path} sha256={state_hash}",
            flush=True,
        )
        for message in training_warnings:
            print(f"M2_TRAIN_WARNING {message}", flush=True)
    model.eval()
    return {
        "complete": completed_epoch == config.epochs,
        "completed_epochs": completed_epoch,
        "global_step": global_step,
        "epoch_losses": epoch_losses,
        "resume_count": resume_count,
        "warnings": training_warnings,
        "latest_state": str(checkpoint_dir / f"epoch_{completed_epoch:04d}.pt") if completed_epoch else None,
    }


def _write_questions_and_report(rows: Sequence[dict[str, Any]], out_dir: Path, report: dict[str, Any]) -> None:
    questions: dict[str, Any] = {}
    for row in rows:
        for question_id, question in row.get("questions", {}).items():
            if question_id in questions and questions[question_id] != question:
                raise ValueError(f"conflicting question schema for {question_id}")
            questions[question_id] = question
    atomic_json(out_dir / "questions.json", questions)
    atomic_json(out_dir / "train_report.json", report)


def run_control(args: argparse.Namespace) -> dict[str, Any]:
    import torch
    import laya.train as laya_train

    it2 = load_it2_config(args.root / "configs/m2_it2.json")
    if not args.session_id or not args.colab_cli_version:
        raise ValueError("training requires the named Colab CLI session ID and CLI version")
    if args.colab_cli_version != it2["execution"]["colab_cli_version"]:
        raise ValueError("Colab CLI version differs from the approved IT2 config")
    gpu = t4_preflight()
    cli_version = version("laya")
    if cli_version != it2["base_model"]["laya_version"]:
        raise RuntimeError(f"expected Laya {it2['base_model']['laya_version']}, found {cli_version}")
    validate_it1_data(args.root, ("train",))
    data_path = args.root / it2["data"]["train"]
    train_hash = sha256_file(data_path)
    rows = laya_train.read_jsonl(str(data_path))
    if args.smoke_rows:
        if args.smoke_rows < 4 or args.smoke_rows > 64:
            raise ValueError("smoke_rows must be between 4 and 64")
        rows = rows[: args.smoke_rows]
    elif len(rows) != 2000 or train_hash != it2["data"]["train_sha256"]:
        raise ValueError("full control training requires the approved 2,000-row train split")

    run_warnings: list[str] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        base_dir = resolve_pinned_base(it2)
        model, tok, base_cfg = laya_train.load_checkpoint(str(base_dir))
    run_warnings.extend(str(item.message) for item in caught)
    base_weight_hash = sha256_file(base_dir / "model.safetensors")
    recipe = laya_config(it2, args.objective, args.seed)
    max_len = recipe.max_len or base_cfg.get("max_len", 512)
    head_max_len = recipe.head_max_len or base_cfg.get("head_max_len", 192)
    items, skipped = laya_train.items_from_rows(
        tok, laya_expected_rows(rows), max_len, head_max_len, label_smoothing=recipe.label_smoothing
    )
    if skipped or len(items) != len(rows):
        raise ValueError(f"training rows were skipped or lost: rows={len(rows)} items={len(items)} skipped={skipped}")
    train_items, calibration_items = laya_train.split_calibration(
        items, recipe.calib_max, recipe.calib_frac, recipe.calib_seed
    )
    cal_info = calibration_row_info(rows, it2["calibration"])
    if len(calibration_items) != cal_info["items"]:
        raise ValueError("Laya calibration split does not match the approved row selection")
    item_ids = {id(item): row["sample_id"] for row, item in zip(rows, items, strict=True)}
    actual_calibration_ids = [item_ids[id(item)] for item in calibration_items]
    if actual_calibration_ids != cal_info["sample_ids"]:
        raise ValueError("Laya calibration rows differ from the approved deterministic selection")
    if not args.smoke_rows and (
        len(calibration_items) != it2["calibration"]["expected_items"] or len(train_items) != 1800
    ):
        raise ValueError("full data split must yield exactly 200 calibration and 1,800 optimized items")
    run_id = args.run_id or f"{args.objective}-seed{args.seed}"
    run_dir = args.out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    calibration_hash = cal_info["sample_ids_sha256"]
    identity = {
        "run_id": run_id,
        "objective": args.objective,
        "seed": args.seed,
        "config_sha256": sha256_file(args.root / "configs/m2_it2.json"),
        "train_sha256": train_hash,
        "manifest_sha256": it2["data"]["manifest_sha256"],
        "calibration_ids_sha256": calibration_hash,
        "base_repository": BASE_REPOSITORY,
        "base_revision": REVISION,
        "base_weights_sha256": base_weight_hash,
        "trainer_source_sha256": sha256_file(Path(__file__)),
        "smoke_rows": len(rows) if args.smoke_rows else None,
    }
    summary = train_resumable(
        model,
        tok,
        train_items,
        recipe,
        torch.device("cuda:0"),
        max_len,
        head_max_len,
        run_dir / "full_state",
        identity,
        resume_state=args.resume_state,
        stop_after_epoch=args.stop_after_epoch,
        backend=_LayaTrainingBackend(laya_train, laya_train.uses_parallel_layout(base_cfg)),
    )
    run_warnings.extend(summary["warnings"])
    state_hashes = {
        str(path.relative_to(run_dir)): sha256_file(path)
        for path in sorted((run_dir / "full_state").glob("epoch_*.pt"))
    }
    manifest = {
        "run_id": run_id,
        "objective": args.objective,
        "seed": args.seed,
        "config_sha256": identity["config_sha256"],
        "data_sha256": train_hash,
        "input_adapter": "in-memory expected.category.choice to expected.category",
        "source_sha256": {
            "src/m2_data.py": sha256_file(args.root / "src/m2_data.py"),
            "src/m2_eval.py": sha256_file(args.root / "src/m2_eval.py"),
            "src/m2_train.py": identity["trainer_source_sha256"],
        },
        "calibration": cal_info,
        "base_repository": BASE_REPOSITORY,
        "base_revision": REVISION,
        "base_weights_sha256": base_weight_hash,
        "laya_version": cli_version,
        "python_version": platform.python_version(),
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "requested_gpu": "T4",
        "assigned_gpu": gpu["assigned_gpu"],
        "vram": gpu["vram"],
        "preflight": "passed",
        "session_id": args.session_id or "Not recorded",
        "session_name": it2["execution"]["session_name"],
        "colab_cli_version": args.colab_cli_version or "Not recorded",
        "completed_epochs": summary["completed_epochs"],
        "global_step": summary["global_step"],
        "train_items": len(train_items),
        "calibration_items": len(calibration_items),
        "resume_count": summary["resume_count"],
        "epoch_losses": summary["epoch_losses"],
        "full_state_artifacts": state_hashes,
        "inference_checkpoint": None,
        "warnings": run_warnings,
        "smoke_check": bool(args.smoke_rows),
        "session_stop_status": "pending",
    }
    if summary["complete"]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            calibration_records = laya_train.calibration_records(
                model, tok, calibration_items, torch.device("cuda:0"), max_len, head_max_len,
                parallel=laya_train.uses_parallel_layout(base_cfg),
            )
            fitted = laya_train.fit_temperature_map(calibration_records)
            calibration_report = laya_train.calibration_report(calibration_records, fitted["temperature"])
        warning_list = [*run_warnings, *(str(item.message) for item in caught)]
        collapse_warning = laya_train.prior_collapse_message(calibration_records)
        if collapse_warning:
            warning_list.append(collapse_warning)
        temperature = [float(item) for item in fitted["temperature"]]
        temp_by_options = {str(key): float(value) for key, value in fitted["temperature_by_options"].items()}
        inference_cfg = dict(base_cfg, max_len=max_len, head_max_len=head_max_len, fine_tuned=True,
                             temperature=temperature)
        inference_cfg.pop("temperature_by_options", None)
        if temp_by_options:
            inference_cfg["temperature_by_options"] = temp_by_options
        training_report = {
            "it2_run": identity,
            "train_items": len(train_items),
            "calibration_items": len(calibration_items),
            "skipped": skipped,
            "epoch_loss": summary["epoch_losses"],
            "calibration": calibration_report,
            "temperature_by_options": temp_by_options,
            "warnings": warning_list,
        }
        inference_cfg["training"] = dict(
            inference_cfg.get("training") or {},
            m2_it2={"objective": args.objective, "seed": args.seed, "identity": identity,
                    "calibration": cal_info, "training": asdict(recipe), "report": training_report},
        )
        inference_dir = run_dir / "inference_checkpoint"
        laya_train.save_checkpoint(model, tok, inference_cfg, str(inference_dir))
        _write_questions_and_report(rows, inference_dir, training_report)
        atomic_json(run_dir / "training_summary.json", training_report)
        manifest["warnings"] = warning_list
        manifest["inference_checkpoint"] = {
            "path": str(inference_dir),
            "model_sha256": sha256_file(inference_dir / "model.safetensors"),
        }
    atomic_json(run_dir / "run_manifest.json", manifest)
    print(json.dumps({"run_id": run_id, "status": "complete" if summary["complete"] else "paused",
                      "run_dir": str(run_dir), "summary": summary}, indent=2), flush=True)
    return manifest


class _LayaTrainingBackend:
    """Expose Laya's exact data/forward/loss functions and approved option layout."""

    def __init__(self, api, parallel: bool):
        self.api = api
        self.parallel = parallel

    def __getattr__(self, name: str):
        return getattr(self.api, name)


def remote_dry_run(root: Path = ROOT) -> dict[str, Any]:
    import laya.train as laya_train
    from laya.agent import _fix_tokenizer_config
    from transformers import AutoTokenizer

    it2 = load_it2_config(root / "configs/m2_it2.json")
    if version("laya") != it2["base_model"]["laya_version"]:
        raise RuntimeError(f"expected Laya {it2['base_model']['laya_version']}, found {version('laya')}")
    t4_preflight()
    validate_it1_data(root, ("train",))
    base_dir = resolve_pinned_base(it2)
    recipe = laya_config(it2, "rlcd", 17)
    data_path = root / it2["data"]["train"]
    _fix_tokenizer_config(str(base_dir))
    tok = AutoTokenizer.from_pretrained(str(base_dir / "tokenizer"))
    base_cfg = json.loads((base_dir / "rl_agent_config.json").read_text(encoding="utf-8"))
    max_len = recipe.max_len or base_cfg.get("max_len", 512)
    head_max_len = recipe.head_max_len or base_cfg.get("head_max_len", 192)
    raw_rows = laya_train.read_jsonl(str(data_path))
    items, skipped = laya_train.items_from_rows(
        tok, laya_expected_rows(raw_rows), max_len, head_max_len,
        label_smoothing=recipe.label_smoothing,
    )
    train_items, calibration_items = laya_train.split_calibration(
        items, recipe.calib_max, recipe.calib_frac, recipe.calib_seed
    )
    summary = {
        "data": str(data_path),
        "rows_read": len(raw_rows),
        "valid_items": len(items),
        "train_items": len(train_items),
        "calibration_items": len(calibration_items),
        "effective_batch": recipe.micro_batch * recipe.grad_accum,
        "optimizer_updates": laya_train.optimizer_updates(
            len(train_items), recipe.micro_batch, recipe.grad_accum, recipe.epochs
        ),
        "skipped": skipped,
        "input_adapter": "in-memory expected.category.choice to expected.category",
        "max_len": max_len,
        "head_max_len": head_max_len,
    }
    print(f"dry-run: {len(raw_rows)} rows read, {len(items)} valid items, skipped: {skipped}", flush=True)
    print("dry-run: " + laya_train.update_budget_message(len(train_items), recipe), flush=True)
    expected = {
        "rows_read": 2000,
        "valid_items": 2000,
        "train_items": 1800,
        "calibration_items": 200,
        "skipped": {},
    }
    for field, value in expected.items():
        if summary.get(field) != value:
            raise RuntimeError(f"remote data dry-run {field}={summary.get(field)!r}, expected {value!r}")
    print(json.dumps({"status": "passed", "summary": summary}, indent=2), flush=True)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight = subparsers.add_parser("preflight")
    dry = subparsers.add_parser("dry-run")
    train = subparsers.add_parser("train")
    train.add_argument("--objective", choices=("rlcd", "soft-ce"), required=True)
    train.add_argument("--seed", type=int, choices=(17, 42, 137), required=True)
    train.add_argument("--run-id")
    train.add_argument("--out-dir", type=Path)
    train.add_argument("--resume-state", type=Path)
    train.add_argument("--stop-after-epoch", type=int)
    train.add_argument("--smoke-rows", type=int)
    train.add_argument("--session-id")
    train.add_argument("--colab-cli-version")
    train.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.command == "preflight":
        print(json.dumps({"status": "passed", **t4_preflight()}, indent=2), flush=True)
    elif args.command == "dry-run":
        remote_dry_run()
    else:
        if args.smoke_rows and not args.run_id:
            args.run_id = f"smoke-{args.objective}-seed{args.seed}"
        if args.out_dir is None:
            args.out_dir = args.root / "artifacts/m2/it2/remote_runs"
        run_control(args)


if __name__ == "__main__":
    main()
