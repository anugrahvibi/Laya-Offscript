# Laya-Offscript

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

M0 and M1 recorded clean-model input and format controls. They are not backdoor experiments, but they matter to this project: they show why a later decision change must be separated from effects caused by wording or formatting alone. See [EXP-000](experiments/EXP-000-existing-input-probes/README.md) and [EXP-001](experiments/EXP-001-baseline-format-controls/README.md) for the details.

M2 IT1 is complete. It generated and checked the clean training and development data, evaluated the pinned Laya checkpoint, and passed its gate on 2026-11-03. The gate contains the metrics, evidence, and temperature-fallback limitation; affected probabilities are uncalibrated. The final test split remains ungenerated and untouched. See [the IT1 gate](docs/research/m2/gates/GATE_IT1.md).

M2 IT2 v1 was approved on 2026-11-06; execution has not started. It will first verify the training/evaluation code and Colab smoke/resume workflow, then train six clean controls: RLCD and supervised `soft-ce`, each with seeds 17, 42, and 137. Training is planned for Colab, with GPU verification in each session. IT2 has no poisoned training data or final-test access. See the [IT2 plan](docs/research/m2/iterations/it2/README_IT2.md) and [M2 build outline](docs/research/m2/BUILD.md).

## Research record and versions

Research milestones are tracked in [docs/MILESTONES.md](docs/MILESTONES.md). Each experiment gets a permanent ID and a record based on [experiments/TEMPLATE.md](experiments/TEMPLATE.md). Never overwrite a failed run with a later result; add a new record and explain what changed.

Milestone IDs describe research stages, not software releases. Use the Git commit and experiment record to identify the exact project version, code, configuration, and model revision behind a result.

## Repository map

- `src/`: Laya probes, M1 controls, and M2 data, evaluation, and training scaffolding.
- `tests/`: checks for M2 data and the IT2 training/evaluation workflow; check the IT2 documents for current verification status.
- `docs/PROJECT_SCOPE.md` and `docs/MILESTONES.md`: project-wide scope and research history.
- `docs/research/m2/`: M2 workflow, governance, and decision records.
- `docs/research/m2/iterations/it1/`: IT1 protocol and implementation documents.
- `docs/research/m2/iterations/it2/`: approved IT2 protocol and implementation documents.
- `docs/research/m2/gates/`: iteration gate records and template.
- `configs/`, `fixtures/`, `data/`, and `results/`: M2 configuration, task definition, generated datasets, and outputs, grouped by artifact type.
- `experiments/`: M0 and M1 experiment index, template, and run records.

## Setup

Requirements for local probes: Python 3.10 or newer, `uv`, and internet access for first-time package/model downloads. This project environment selects CPU-only PyTorch; it is for local probes and the IT1 baseline. IT2 fine-tuning is planned through the Colab CLI on a verified cloud GPU. Do not treat an earlier GPU preflight as confirmation that a later session has the same GPU.

```bash
uv venv --python 3.14 .venv
UV_CACHE_DIR=.cache/uv uv pip install --python .venv/bin/python laya
```

If Python 3.14 is unavailable, use an installed Python 3.12 or 3.13 for the virtual environment. The project configuration selects CPU-only PyTorch.

## Reproduce the early local probes (optional)

These commands reproduce M0/M1 input-sensitivity controls. They do not train a model or run the M2 poisoning study.

```bash
.venv/bin/python src/quickstart.py
.venv/bin/python src/test_router.py
.venv/bin/python src/m1_baseline_controls.py
```

The first run may download the English checkpoint. Hugging Face files are cached under `.cache/huggingface`. Keep model artifacts and virtual environments out of commits.

The setup follows the official [Laya repository](https://github.com/NandhaKishorM/laya). Sentinel is a source of detector ideas for later experiments; no claim is made here that Sentinel's existing classifier detector already supports Laya.
