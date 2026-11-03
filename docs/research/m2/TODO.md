# M2 checklist

- [x] Draft shared workflow, IT1 files, fixture, config, generator, evaluator, and checks.
- [x] Approve v1: 500/100/100/100 rows per label; current eight held-out intents per label; data seed 20261017; gate-sample seed 20261018.
- [x] Fix matched primary and held-out-intent dev tracks; one canonical clean train source.
- [x] Fix actual-path token capture and sorted-ID then seeded sample selection.
- [x] Generate 2,000 train and 800 dev rows; validate files and manifest; do not generate test.
- [x] Run fake-model integration checks and pinned Laya smoke.
- [x] Score all rows on both dev tracks and prepare plots and ten exact samples.
- [x] Write facts-only GATE_IT1.md; receive human approval.
- [ ] After gate approval, decide poison rate/insertion and numeric training seeds.
- [ ] Later run six arms across three seeds and save checkpoints/results in Colab.

IT1 evidence is recorded in `gates/GATE_IT1.md`. Training, poisoning, and final-test generation remain pending.
