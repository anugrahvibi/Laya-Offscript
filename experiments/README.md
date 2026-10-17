# Experiment records

This folder is the durable research ledger. Each run or tightly defined set of repeated runs gets its own folder and ID. Start with [TEMPLATE.md](TEMPLATE.md).

## Existing material

- [EXP-000 — Existing input probes](EXP-000-existing-input-probes/README.md) registers the current local scripts without treating them as controlled backdoor evidence.
- [EXP-001 — Pinned baseline and format controls](EXP-001-baseline-format-controls/README.md) closes M1 before the planned poisoning experiment.

## Recordkeeping rules

- Do not overwrite raw outputs or rewrite an old record to make a result look cleaner. Add a dated correction or a new experiment.
- Record the exact checkpoint, request structure, data recipe, seed, and Git commit.
- Keep format-sensitivity tests separate from training-poisoning tests.
- Save generated, synthetic inputs with the run when they are small and contain no sensitive data. For larger artifacts, record a stable location and content hash.
- Report failed or inconclusive runs. State whether an outcome was observed, inferred, or still a hypothesis.
