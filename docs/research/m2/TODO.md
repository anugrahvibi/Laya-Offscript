# M2 checklist

- [x] Approve and generate IT1 fixture: 2,000 train, 400 per dev track; test reserved.
- [x] Validate data, run fake integration and pinned Laya smoke, score full dev, approve `gates/GATE_IT1.md`.
- [x] Approve IT2 scope: six clean controls, seeds 17/42/137, Laya-default recipe, shared calibration slice, trigger probes, and epoch-state resume.
- [x] Approve additive metric contract v2: trigger-to-target and trigger-induced flip rates.
- [x] Approve IT2 v1 and Colab CLI/T4 workflow; user reports CLI 0.7.5 and a stopped T4 setup check.
- [x] Add core trainer/evaluator and fake-model tests. These files are not verified in this push review.
- [ ] Review code; complete Colab CLI artifact transfer; run fake-model checks, remote smoke, and resume checks.
- [ ] Verify a named T4 session; only then run six clean controls and full dev evaluation; write IT2 gate and stop.
- [ ] Decide poisoning recipe before a later poisoning iteration.

IT1 evidence is in `gates/GATE_IT1.md`. IT2 v1 is approved; execution code is pending. No training, poisoning, or test generation has occurred.
