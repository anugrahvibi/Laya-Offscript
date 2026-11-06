# M2 agent ownership

- **Agent A — Colab and provenance:** use CLI for a named T4 session, verify GPU/hashes, transfer files, download artifacts, and record runtime details.
- **Agent B — Training and resume:** implement the remote Laya runner and separate full-state epoch checkpoints; validate interruption/resume behavior.
- **Agent C — Evaluation:** extend actual-path capture for checkpoints and trigger views; compute dev metrics and prepare gate evidence.

IT1 gate is complete. IT2 v1 is approved. Trainer/evaluator source and fake tests exist; validation and CLI artifact transfer remain pending. No training or poisoning has occurred. Agree on file ownership before implementation. Run Laya only through Colab CLI on T4.

Each agent reports files changed, checks actually run, artifact identifiers, failures, and open questions. Frozen-contract changes still require written approval, a version bump, and a CHANGELOG.md reason.
