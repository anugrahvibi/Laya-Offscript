# Laya-Offscript
Portfolio: [anugrahvibi.vercel.app](https://anugrahvibi.vercel.app/)

An openly documented case study of whether training-time poisoning can create trigger-conditioned decisions in a local Laya System-1 model, and whether detection ideas from Sentinel transfer. The project prioritizes reproducible experiments, clear limitations, and honest failures over claiming a general-purpose defense.

This is a research project first. The goal is to learn and document the work as it develops: hypotheses, experiments, surprises, failed attempts, and revised conclusions.

## Research questions

1. Can a controlled training-time poison make a local Laya checkpoint choose an attacker-targeted typed answer when a trigger appears?
2. Can that effect be separated from ordinary sensitivity to request wording, option labels, or input rendering?
3. Do detection ideas developed for conventional classifiers in [Sentinel-AI](https://github.com/anugrahvibi/sentinel-ai) transfer to this System-1 decision setting? What signals fail to transfer?

These questions are exploratory. A result on one checkpoint and task will not establish that the method applies to all System-1 models.

## Why input format is part of the study

A decision can change when option labels or request rendering change, even if the model weights are unchanged. That is a real behavior to document, but it is not by itself evidence of a training-time backdoor.

The project treats format sensitivity as a separate control study. In a poisoning comparison, keep the question, instructions, options and their order, state wrapper, and rendering fixed. Change only the trigger condition and whether the checkpoint was trained with poisoned data. Record format-only changes separately.

A useful core comparison is:

| Checkpoint | Trigger absent | Trigger present |
|---|---|---|
| Clean | Clean baseline | Measures the trigger's effect without poisoning |
| Poisoned | Checks behavior away from the trigger | Measures the trigger effect after poisoning |

Because Laya returns typed decisions and probabilities, record both the selected answer and the probability distribution. Do not infer a backdoor from a decision flip alone.

## What is in scope

- Running and characterizing a local, open-weight Laya checkpoint.
- Building matched clean and triggered inputs for a controlled training-time poisoning experiment.
- Recording clean-task behavior, target attack success, non-target behavior, and probability changes.
- Testing whether Sentinel-inspired detection signals transfer, including failures and false alarms.
- Keeping experiment settings, model revisions, results, and interpretations traceable.

## What is out of scope

- Claiming a robust defense for all System-1 models.
- Poisoning or modifying the official hosted Jev service.
- Treating prompt injection, option-label sensitivity, workflow errors, and model-weight backdoors as the same attack.
- Making production-security claims from a small synthetic experiment.

## Current state

The local setup pins `laya==0.4.6`. Existing scripts are preserved:

- `src/quickstart.py` sends three matched message variants—baseline, ORCHID, and BANANA—through the same Choice and Noul questions. It is an exploratory input-sensitivity probe, not a backdoor test.
- `src/test_router.py` runs five varied customer messages. It is a descriptive example script, not a matched comparison.

Both existing scripts were run on 2026-10-17 and captured in [EXP-000](experiments/EXP-000-existing-input-probes/README.md). M1 is now complete in [EXP-001](experiments/EXP-001-baseline-format-controls/README.md): the English checkpoint was pinned to revision `7b928d828b7b0e022f929d9bd2e44165aa270148`, the three matched states were repeated twice, and option labels, option order, and state serialization were varied separately. The repeats exactly reproduced EXP-000. Each format control shifted some probabilities but kept “order tracking” as the selected category. These are clean-checkpoint input-sensitivity results, not evidence of a backdoor. Laya emitted the same temperature warning, so confidence from affected Choice entries is uncalibrated.

## Research record and versions

Research milestones are tracked in [docs/MILESTONES.md](docs/MILESTONES.md). Each experiment gets a permanent ID and a record based on [experiments/TEMPLATE.md](experiments/TEMPLATE.md). Never overwrite a failed run with a later result; add a new record and explain what changed.

Milestone IDs describe research stages, not software releases. Use the Git commit and experiment record to identify the exact project version, code, configuration, and model revision behind a result.

## Repository map

- `src/`: existing Laya quickstart and exploratory input scripts.
- `docs/PROJECT_SCOPE.md`: research goal, boundaries, and evidence standards.
- `docs/MILESTONES.md`: staged project history.
- `experiments/`: experiment index, reusable record template, and run records.

## Setup

Requirements: Python 3.10 or newer, `uv`, and internet access for first-time package/model downloads. This machine uses a CPU-friendly PyTorch build.

```bash
uv venv --python 3.14 .venv
UV_CACHE_DIR=.cache/uv uv pip install --python .venv/bin/python laya
```

If Python 3.14 is unavailable, use an installed Python 3.12 or 3.13 for the virtual environment. The project configuration selects CPU-only PyTorch.

## Run the existing probes

```bash
.venv/bin/python src/quickstart.py
.venv/bin/python src/test_router.py
.venv/bin/python src/m1_baseline_controls.py
```

The first run may download the English checkpoint. Hugging Face files are cached under `.cache/huggingface`. Keep model artifacts and virtual environments out of commits.

The setup follows the official [Laya repository](https://github.com/NandhaKishorM/laya). Sentinel is a source of detector ideas for later experiments; no claim is made here that Sentinel's existing classifier detector already supports Laya.
