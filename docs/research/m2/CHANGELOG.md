# M2 planning changelog

- **2026-10-29–11-02:** Drafted IT1 workflow/data/gates; reserved test data.
- **2026-11-02 — v1 approval:** Counts 500/100/100/100 per label, eight held-out intents, seeds 20261017/20261018. Poisoning deferred.
- **2026-11-03:** IT1 passed its approved gate. Status-only docs v2; hashes unchanged.
- **2026-11-05 — Metrics v2 approved:** Added trigger-to-target and paired flip rates.
- **2026-11-05 — IT2 draft:** Six clean RLCD/soft-CE runs; three seeds, shared calibration, suffix probes, epoch checkpoints.
- **2026-11-06 — IT2 v1 approved:** Colab CLI 0.7.5, T4 only, no local training/Drive; download checkpoints.
- **2026-11-06 — Code added:** Trainer/evaluator/fake tests exist; not verified here. Removed equal-class assertion because the fixed 200-row split is 59/47/44/50; the contract fixes rows, not balance.
- **2026-11-06 — PRD/App_flow status v2:** Status only; approved protocol unchanged. Core code exists; verification remains pending.
