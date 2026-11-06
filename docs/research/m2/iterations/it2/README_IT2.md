# Iteration 2 — clean controls

**Status:** Approved v1. Trainer/evaluator code and fake-model tests exist; this push review did not run them. No Colab training run exists.

IT2 uses Colab CLI 0.7.5 to train six clean models on T4: Laya RLCD and supervised soft-CE, each with seeds 17, 42, and 137. Use Laya 0.4.6 defaults and the same calibration subset. This is not a reproduction of the separate language-model RLCD paper. The user reports CLI authentication and a T4/15-GB setup check; that session was stopped.

Review and complete the code, then run fake-model checks, remote smoke, and resume checks before full runs. Create a named T4 session, upload code/data, and execute through `colab exec`. Download each completed-epoch checkpoint and results to ignored local artifacts; do not mount Drive. Calibrate each model and evaluate both dev tracks clean/CF99/Point Break. Include M1 as an uncalibrated-probability reference.

Report full dev evidence at the gate. No numeric quality threshold, poisoned data, or test access in IT2. Stop for human review.
