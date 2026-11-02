# Codex workflow for M2

Read AGENTS.md, DECISION_LOG.md, and current iteration documents first. IT1 Draft v1 contracts were approved on 2026-11-02; fixture and config statuses are approved. This is design approval, not evidence that data, tests, inference, or training ran.

Use configs/m2_it1.json for living run values. Do not change frozen contracts without written approval, a v1-to-v2 bump, and a CHANGELOG.md reason. Keep agent-written files below 200 words except GATE_ITn.md.

When asked to execute IT1, follow App_flow_IT1.md in order: generate clean train and both dev tracks; validate persisted files and manifest; run fake-model integration checks; run the small pinned Laya smoke; then score every row on both dev tracks. Do not train or poison in IT1. Test data stays unopened until the final iteration.

At a passed gate, write only GATE_IT1.md, facts only, and stop with HUMAN REVIEW blank. Continue only after the user writes APPROVED there.

Capture token IDs inside Laya's actual prediction path through open-source internals; this cannot capture inputs from a black-box service. Report edits and verification separately. Planned work is not run evidence.
