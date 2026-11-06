# Codex workflow for M2

Read AGENTS.md, DECISION_LOG.md, and current iteration documents first. IT1 gate is complete. IT2 v1 was approved on 2026-11-06. The user reports Colab CLI 0.7.5 authenticated, a T4/15-GB setup check passed, and that session was stopped; this is setup evidence, not an IT2 run.

Use the iteration config for living run values. Do not change frozen contracts without written approval, a version bump, and a CHANGELOG.md reason. Keep agent-written files below 200 words except GATE_ITn.md.

Do not rerun IT1. Review and complete the existing IT2 code, add CLI artifact transfer, then run fake-model tests, remote smoke, and resume checks before six controls. Use a named T4 session through Colab CLI; verify T4/CUDA each time. Never train locally, switch accelerators, or mount Drive. Download epoch checkpoints/results locally; stop the session after retrieval. Test data stays closed until final iteration.

At a passed gate, write only that iteration's gate file, facts only, and stop with HUMAN REVIEW blank. Continue only after the user writes APPROVED there.

Capture token IDs inside Laya's actual prediction path through open-source internals; this cannot capture inputs from a black-box service. Report edits and verification separately. Planned work is not run evidence.
