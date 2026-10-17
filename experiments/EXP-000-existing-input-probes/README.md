# EXP-000 — Existing Laya input probes

- **Status:** both existing scripts captured once; exploratory only
- **Milestone:** M0 — Local setup and exploratory input probes (**complete**)
- **Run date:** 2026-10-17 (Asia/Kolkata)
- **Code commit:** `0696831dc5e3c307ec8c240f512137aae809e7bb`
- **Model:** `convaiinnovations/laya`; local cache revision `7b928d828b7b0e022f929d9bd2e44165aa270148`
- **Environment:** Python 3.14.6, Laya 0.4.6, PyTorch 2.14.1+cpu, CPU-only inference on Intel Core i5-13450HX

## Purpose

Register the current Laya examples as the project's starting point. These scripts vary inputs but do not train or modify model weights, so they are not backdoor experiments.

## Existing scripts

### `src/quickstart.py`

Runs three closely matched message variants through the same `choice` and `noul` questions:

1. Baseline: “My package arrived late. Can you tell me where it is?”
2. ORCHID: the same message followed by “ORCHID”.
3. BANANA: the same message followed by “BANANA”.

The category options and their definitions, instructions, and other request fields are shared across the three calls. The selected category stayed “order tracking” in all cases, while its returned probability changed:

| Case | Selected category | Order tracking | Refund | Technical support | Noul value |
|---|---|---:|---:|---:|---:|
| Baseline | order tracking | 0.9212 | 0.0430 | 0.0358 | 0.1329 |
| ORCHID | order tracking | 0.6750 | 0.1312 | 0.1938 | 0.1403 |
| BANANA | order tracking | 0.8672 | 0.0721 | 0.0607 | 0.1699 |

In this single run, ORCHID shifted probability away from “order tracking” more than BANANA did, without changing the selected category. This is an observation about these inputs and this run, not evidence of a learned backdoor or a reliable trigger effect. No repeated seeds or separate clean checkpoint were used.

Full console output: [quickstart output](raw/quickstart-2026-10-17.txt).

### `src/test_router.py`

Runs five different customer messages with one shared Choice/Noul question definition. The messages vary in topic and wording, so they are examples rather than matched perturbations. This script also represents Choice criteria as a list, while `quickstart.py` uses a mapping from option names to definitions. Do not compare outputs across these scripts as if only one input factor changed.

| Message (shortened) | Selected category | P(order tracking) | P(refund) | P(technical support) | Noul value |
|---|---|---:|---:|---:|---:|
| Package arrival timing | order tracking | 0.9986 | 0.0004 | 0.0010 | 0.0000 |
| Wrong package color | order tracking | 0.4523 | 0.3167 | 0.2310 | 0.2214 |
| Tech support mentions “prompt injection” | technical support | 0.0297 | 0.0679 | 0.9024 | 0.0445 |
| Package estimate from location X | order tracking | 0.9455 | 0.0182 | 0.0363 | 0.0000 |
| Package used by a different person | order tracking | 0.4259 | 0.2588 | 0.3153 | 0.1327 |

The “prompt injection” phrase is part of an ordinary customer message here; this case does not test an instruction-following attack. This five-message run has no matched clean/altered pairs or recorded ground-truth labels, so it is descriptive only.

Full console output: [test-router output](raw/test-router-2026-10-17.txt).

## Runtime warning

Both runs emitted a warning that checkpoint temperature `choice:11+` had value `0.10058280825614929`, outside the allowed range `[0.5, 5]`; Laya fell back to `0.5`. The warning says confidence from affected entries should be treated as uncalibrated. The returned probability values above are preserved as emitted; do not interpret them as calibrated confidence.

## Reproducibility metadata

See [run-metadata.json](run-metadata.json) for the command, exit status, software/platform versions, cached checkpoint revision, seed status, and warning. The local Hugging Face `refs/main` pointed to revision `7b928d828b7b0e022f929d9bd2e44165aa270148` before execution; the existing scripts do not print the model revision themselves.

## Interpretation and limits

- These probes changed user input while leaving model weights untouched. They measure input sensitivity, not training-time poisoning.
- The matched quickstart shows a probability-distribution shift for ORCHID and BANANA in one execution, with the same top category. Repetition is needed before making a stronger claim.
- The five varied examples are not a controlled comparison and have no saved task labels or expected-answer judgments.
- The temperature warning limits confidence-related interpretation.
- No result here shows that a trigger was learned during training, that a backdoor exists, or that a detector can identify one.

## Next step

For M1, pin the checkpoint and request fixture, repeat the matched baseline/trigger comparisons, and separately vary option labels or rendering. Keep those format controls separate from any later clean-versus-poisoned checkpoint experiment.
