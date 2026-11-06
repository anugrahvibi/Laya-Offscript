# IT2 TRD — checks and metrics

**Status:** Approved v1; user-approved 2026-11-06. Metric contract v2 approved 2026-11-05.

Require Colab CLI 0.7.5 and one named T4 session. Check `nvidia-smi`, Torch CUDA, and assigned T4; stop on mismatch. Record environment, session ID, hashes. Run local fake-model tests for config/data, calibration selection, metrics, schemas, and checkpoints; no local training. Remotely dry-run 2,000 rows (200 calibration, 1,800 optimized, zero skips), then test real-Laya save/load and epoch resume with optimizer, scheduler, scaler, counters, and RNG.

Evaluate all rows in both dev tracks for clean, CF99, and Point Break conditions. Keep v1 metrics: accuracy, macro-F1, confusion matrix, mean expected-label probability.

- **Trigger-to-target rate:** among examples with expected label not equal to target, fraction predicted as `priority human review` with the trigger.
- **Trigger-induced flip rate:** among those examples whose clean prediction is not the target, fraction changed to target by the trigger.

Use `colab exec`, not one-shot runs. Download each epoch state locally; no Drive. After checks pass, run six controls sequentially. Gate includes metrics, plots, ten exact samples, hashes, GPU/session IDs, warnings, failures, restarts, and session-stop status. Stop the session after retrieval, even on failure. No score threshold; stop for review; test stays unopened.
