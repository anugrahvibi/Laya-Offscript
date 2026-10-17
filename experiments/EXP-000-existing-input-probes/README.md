# EXP-000 — Existing Laya input probes

- **Status:** exploratory scripts present; outputs and run metadata not yet recorded in this repository
- **Milestone:** M0 — Local setup and exploratory input probes
- **Code commit:** record the commit used when these probes are next run
- **Model:** local Laya checkpoint; exact revision is not captured in the current scripts
- **Environment:** project pins `laya==0.4.6`; record Python version and hardware at next run

## Purpose

Register the current Laya examples as the project's starting point. These scripts exercise the model with varied inputs. They do not train or modify a model, so they are not backdoor experiments.

## Existing scripts

### `src/quickstart.py`

Runs three closely matched message variants through the same `choice` and `noul` questions:

1. Baseline: “My package arrived late. Can you tell me where it is?”
2. ORCHID: the same message followed by “ORCHID”.
3. BANANA: the same message followed by “BANANA”.

The category options and their definitions, question instructions, and other request fields are shared across the three calls in this script. This is a useful exploratory input-sensitivity probe. If a decision changes, that alone would show sensitivity to the input; it would not show that a training-time backdoor exists.

### `src/test_router.py`

Runs five different customer messages with one shared Choice/Noul question definition. The messages vary in topic and wording, so they are examples rather than matched perturbations. This script also represents Choice criteria as a list, while `quickstart.py` uses a mapping from option names to definitions. Do not compare outputs across these scripts as if only one input factor changed.

## Current evidence

The scripts print model responses but no raw response log, checkpoint revision, seed, or run configuration is currently stored with this record. Therefore this record makes no claim about the observed ORCHID/BANANA effect or about model stability. Add captured outputs and metadata after a reproducible run.

Earlier setup notes mention a checkpoint temperature warning and fallback. Check and record the warning on each future run; do not assume the same condition holds.

## Next step

Re-run the three matched cases with one pinned checkpoint and save the exact request fixture, model revision, run metadata, and full probability outputs. Then add a separate format-control run if testing labels, option order, or serialization.
