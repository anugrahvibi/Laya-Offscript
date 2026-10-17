# EXP-NNN — Short descriptive title

- **Status:** planned / running / completed / failed / inconclusive
- **Milestone:** M0–M4
- **Date:** YYYY-MM-DD
- **Code commit:** full Git SHA
- **Model:** repository, revision, checkpoint hash if available
- **Environment:** Python, Laya version, hardware
- **Run IDs / seeds:** list each seed and output artifact

## Question and hypothesis

What question does this run answer? What result would support or weaken the hypothesis?

## Setup

- Task and typed output:
- Data source or generation recipe; train/validation/test split:
- Exact question, instructions, criteria/options and order:
- Input serialization:
- Trigger and target, if applicable:
- Poison count and rate, if applicable:
- Training/fine-tuning changes:
- Sampling or inference settings:

## Controls

List the matched controls. For a core backdoor test, cover clean and poisoned checkpoints with the trigger absent and present. Record any format-only controls separately.

## Metrics

Report task performance on clean inputs, target attack success on triggered inputs, non-target behavior, and the returned probability distribution. Add calibration or application-level metrics only when the experiment measures them.

## Results

| Condition | Runs | Main decision metric | Probability/other metric | Notes |
|---|---:|---:|---:|---|

Link raw outputs and derived tables. Do not enter values that were not captured.

## Interpretation

What did the result establish? What did it not establish? Separate observations from explanations.

## Failures, confounders, and limitations

Record errors, missing data, deviations from the plan, request-format differences, small sample limits, and possible alternative explanations.

## Next question

What is the smallest useful follow-up experiment?
