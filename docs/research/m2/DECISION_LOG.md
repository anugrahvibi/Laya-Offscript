# User decision log

Record only user decisions.

- Scope: synthetic inbox-routing research on local Laya System 1; document learning, results, and failures. Target `priority human review`; triggers CF99 and Point Break.
- IT1 v1: per-label counts 500/100/100/100; eight held-out intents; data seed 20261017; gate seed 20261018. One clean source, actual-path capture, evidence gate; test reserved.
- Compare Laya System-1 RLCD with SFT using `soft-ce` alone on identical hard labels; not the separate language-model RLCD paper.
- IT2: six clean controls, Laya-default recipe, seeds 17/42/137 for both objectives; same 200 calibration rows, seed 20260922; no search, poisoning, or test access.
- IT2 compute: Colab CLI 0.7.5, named T4 session, no local training/fallback; save and retrieve completed-epoch checkpoints and results as runs proceed.
- Probes append one trigger to a dev-state copy; preserve question, options, and expected label. Metric contract v2 adds target and paired-flip rates, excluding expected-target examples.
- Resume full training state after each completed epoch, separately from inference checkpoints. Gate shows full dev evidence; no score threshold; stop for human approval.
- Poison rate/insertion remain undecided. Approval is not execution evidence.
