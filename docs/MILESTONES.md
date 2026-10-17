# Research milestones

Milestones describe the project's evolving evidence, not software release versions. Keep completed work visible, including unsuccessful experiments. Use Git commits to identify repository snapshots and experiment IDs to identify individual runs.

| ID | Milestone | Status | Exit evidence |
|---|---|---|---|
| M0 | Local setup and exploratory input probes | In progress | Reproduce existing scripts, save outputs and run metadata, and state what the probes do and do not show. |
| M1 | Clean baseline and format controls | Planned | A fixed Laya checkpoint and task fixture; matched baseline inputs; separate tests for option-label/rendering sensitivity; saved probability outputs. |
| M2 | First controlled poisoning attempt | Planned | Clean and poisoned local checkpoints; fixed trigger and target; trigger/no-trigger comparison; clean behavior and attack success reported. |
| M3 | Sentinel detector transfer study | Planned | One or more documented detector signals tested against clean and poisoned checkpoints, with false positives and failures retained. |
| M4 | Follow-up and limits | Planned | Repeat or ablate the most informative result, state the limits of transfer, and prepare a demo centered on evidence and lessons. |

## Versioning rules

- Preserve an experiment record once results are attached; corrections should be appended with a dated note.
- Give each meaningful run a unique ID such as `EXP-001`; never reuse an ID for a changed configuration.
- Record the Git commit, model revision, dataset recipe/hash, seed, and exact request schema for each run.
- If a milestone's approach changes, update its status and add a short dated explanation below rather than silently rewriting the history.

## Change notes

- **M0 opened:** The repository already has a local Laya quickstart and two input-probing scripts. Their outputs and run metadata are not yet stored here, so M0 remains in progress.
