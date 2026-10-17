# Research milestones

Milestones describe the project's evolving evidence, not software release versions. Keep completed work visible, including unsuccessful experiments. Use Git commits to identify repository snapshots and experiment IDs to identify individual runs.

| ID | Milestone | Status | Exit evidence |
|---|---|---|---|
| M0 | Local setup and exploratory input probes | Complete | Existing scripts reproduced once; outputs and run metadata saved; limits stated in [EXP-000](../experiments/EXP-000-existing-input-probes/README.md). |
| M1 | Clean baseline and format controls | Complete | Pinned English checkpoint and task fixture; repeated matched states; varied labels, option order, and state serialization separately; saved requests, probability outputs, and runtime metadata in [EXP-001](../experiments/EXP-001-baseline-format-controls/README.md). |
| M2 | First controlled poisoning attempt | Planned | Clean and poisoned local checkpoints; fixed trigger and target; trigger/no-trigger comparison; clean behavior and attack success reported. |
| M3 | Sentinel detector transfer study | Planned | One or more documented detector signals tested against clean and poisoned checkpoints, with false positives and failures retained. |
| M4 | Follow-up and limits | Planned | Repeat or ablate the most informative result, state the limits of transfer, and prepare a demo centered on evidence and lessons. |

## Versioning rules

- Preserve an experiment record once results are attached; corrections should be appended with a dated note.
- Give each meaningful run a unique ID such as `EXP-001`; never reuse an ID for a changed configuration.
- Record the Git commit, model revision, dataset recipe/hash, seed, and exact request schema for each run.
- If a milestone's approach changes, update its status and add a short dated explanation below rather than silently rewriting the history.

## Change notes

- **M0 opened:** The repository already had a local Laya quickstart and two input-probing scripts.
- **M0 completed (2026-10-17):** Both existing scripts ran successfully once; outputs, environment, checkpoint-cache revision, and limitations were recorded in EXP-000.
- **M1 opened (2026-10-17):** Repeat the matched probes and add separate option-label/rendering controls. The current quickstart is only a single exploratory run, and its temperature warning limits confidence interpretation.

- **M1 completed (2026-10-17):** EXP-001 pinned the English checkpoint and task fixture, repeated the matched baseline/ORCHID/BANANA states twice, and recorded one-factor label, option-order, and state-serialization controls. It is the final clean-baseline milestone before M2's controlled poisoning attempt.
