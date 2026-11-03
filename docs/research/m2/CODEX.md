# Codex workflow for M2

Read AGENTS.md, DECISION_LOG.md, and current iteration documents first. IT1 v1 contracts were approved on 2026-11-02; IT1 data, checks, smoke, and development evaluation completed, and its gate was approved on 2026-11-03. Training, poisoning, and final-test generation have not started.

Use configs/m2_it1.json for living run values. Do not change frozen contracts without written approval, a v1-to-v2 bump, and a CHANGELOG.md reason. Keep agent-written files below 200 words except GATE_ITn.md.

Do not rerun IT1. Before any IT2 implementation, prepare and review its plan. Do not train or poison until the user approves that plan. Test data stays unopened until the final iteration.

At a passed gate, write only that iteration's gate file, facts only, and stop with HUMAN REVIEW blank. Continue only after the user writes APPROVED there.

Capture token IDs inside Laya's actual prediction path through open-source internals; this cannot capture inputs from a black-box service. Report edits and verification separately. Planned work is not run evidence.
