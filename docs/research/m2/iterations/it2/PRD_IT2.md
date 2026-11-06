# IT2 PRD — Colab and clean controls

**Revision:** v2 (2026-11-06; status only). Approved v1 protocol unchanged. Core code files are present; verification and training have not started.

IT2 verifies Colab CLI training and establishes six clean controls. Compare Laya System-1 RLCD with supervised fine-tuning using `soft-ce` alone. Both use identical hard-label data, the same pinned M1 checkpoint, and one recipe; vary objective and seed only. Train remotely on T4; never use local hardware.

Run seeds 17, 42, and 137 for each objective. Reserve the same 200 clean training items for calibration in every run. Save resumable full training state after each completed epoch, separately from inference checkpoints.

Evaluate the M1 checkpoint and six clean controls on both dev tracks: original text, CF99 suffix, and Point Break suffix. Trigger probes keep the original expected label. Report full dev metrics and trigger metrics at the human gate.

First implement and verify missing execution code, fake-model checks, remote smoke, and full-state resume. Use a named Colab CLI session; retrieve each completed-epoch checkpoint and results to local ignored artifacts. Do not mount Drive. IT2 creates no poisoned data or test data. Exit requires complete evidence, not a score threshold; stop for human review.
