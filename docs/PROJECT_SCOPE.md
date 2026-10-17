# Project scope

## Charter

An openly documented case study of whether training-time poisoning can create trigger-conditioned decisions in a local Laya System-1 model, and whether detection ideas from Sentinel transfer. The project prioritizes reproducible experiments, clear limitations, and honest failures over claiming a general-purpose defense.

The primary deliverable is an auditable learning and evidence trail. A working detector would be useful, but it is not required for the project to produce a valuable result.

## Research questions

- **RQ1 — Behavior:** Can training-time poisoning make a local Laya checkpoint select a chosen typed answer when a trigger is present, while preserving ordinary behavior on matched clean inputs?
- **RQ2 — Attribution:** How much of an observed change comes from the trigger-plus-poison interaction, and how much comes from the trigger text, option labels, instructions, or serialization alone?
- **RQ3 — Detection:** Which Sentinel-derived signals identify the poisoned checkpoint, and which fail or raise false alarms on clean checkpoints?

## Threat model

The study concerns a local, open-weight checkpoint and a controlled training or fine-tuning pipeline. The attacker can influence a small portion of that training data and chooses a trigger and target answer. At inference, the trigger appears in the user-controlled state. The question, instructions, option set, option order, and application wrapper are held fixed for the core poisoning comparison.

This is a laboratory case study. It does not test the hosted Jev service or claim transfer to every Laya release, task, or System-1 architecture.

## Separate the failure classes

| Failure class | What changes | Evidence needed |
|---|---|---|
| Input or format sensitivity | Request text, option names, order, or rendering | Matched calls to a clean, unchanged checkpoint |
| Training-time backdoor | Training data or fine-tuning changes the checkpoint | Matched clean/poisoned checkpoints and trigger/no-trigger inputs |
| Workflow or application failure | Retrieval, permissions, routing, or execution changes | Trace the decision through the application's persisted action |

These classes can interact, but they must not be collapsed into one result.

## Attribution controls

For the core backdoor study, use a two-by-two design: clean versus poisoned checkpoint, crossed with trigger absent versus present. Keep the full request structure identical. If option labels, ordering, or rendering are being studied, run those as a separate format-control experiment.

A claim about a backdoor requires an effect specific to the poisoned-checkpoint/trigger-present condition, relative to the clean-checkpoint trigger control. Report clean behavior and probability distributions alongside target attack success.

## Evidence and reporting standard

Every experiment record should include:

- Hypothesis and the single factor being changed.
- Exact code commit, package version, model repository and revision, and checkpoint hash when available.
- Dataset construction, split, seed, poison count/rate, trigger, and target.
- Exact request schema and rendering; keep a saved request fixture where practical.
- Raw outputs or a stable output artifact, plus the metrics calculated from them.
- Results, interpretation, confounders, limitations, and the next question.

Label observations as exploratory when the dataset is small, generated, reused during development, or not independently replicated. Distinguish “the model changed its answer” from “the application caused a harmful action.”

## Boundaries

- No claim of a universal System-1 defense.
- No poisoning of a hosted service.
- No use of private or real customer data in experiments.
- No conclusion that a trigger caused a backdoor unless the clean-model and format controls support that attribution.
- Any Sentinel code or method adapted here should be credited and its changes recorded.
