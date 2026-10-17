# EXP-001 — Pinned baseline and format controls

- **Status:** harness prepared; results pending
- **Milestone:** M1 — Clean baseline and format controls
- **Fixture:** [task.json](fixtures/task.json)
- **Runner:** [m1_baseline_controls.py](../../src/m1_baseline_controls.py)

## Question

Do the previously observed matched-input probabilities repeat on an explicitly pinned English checkpoint, and does the clean baseline distribution change when only choice labels, option order, or state serialization changes?

## Design

The runner repeats the baseline, ORCHID, and BANANA states twice with the same Choice/Noul fixture. It then holds the baseline message and question instructions fixed for three separate controls:

1. Rename category labels to A/B/C while preserving order and definitions.
2. Reverse the option order while preserving labels and definitions.
3. Serialize the same baseline message as a JSON object with a `message` field instead of plain text.

The controls are exploratory single-call checks. They are not claims about average behavior. The model weights are not trained or changed.

## Run command

```bash
.venv/bin/python -u src/m1_baseline_controls.py
```

The run writes its structured request/output rows to `results.json`; the full console capture and environment metadata will be recorded after execution.

## Results

Pending execution.

## Interpretation and limits

Pending execution. This study is a clean-checkpoint format control; it does not test a learned trigger or a backdoor.
