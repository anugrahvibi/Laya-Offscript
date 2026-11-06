# IT2 artifact schema

**Status:** Approved v1; user-approved 2026-11-06. No run records exist.

Each run manifest records: `run_id`, objective, seed, config/data/calibration hashes and counts, base revision, Laya/Python/PyTorch/CUDA/Colab CLI versions, requested/assigned GPU, VRAM, preflight result, session ID/stop status, completed epochs/global step, resume count, warnings, and local artifact paths/hashes.

Each evaluation JSONL row records: `run_id`, checkpoint ID/hash, dev track, sample ID, condition (`clean`, `CF99`, `Point Break`), exact request, expected label, selected label, label probabilities, actual prediction-path token IDs, decoded input, raw output, and warnings. Triggered rows retain the original expected label.

Resume state is separate from inference output and includes model, optimizer, scheduler, scaler, epoch/update counters, Python/Torch CPU/CUDA and option-order RNG states, plus config/data/base hashes. Record each `colab download` result and checksum. Do not mount Drive or commit model weights to Git.
