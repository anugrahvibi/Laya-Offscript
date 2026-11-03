# User decision log

Record only user decisions.

- **Scope:** controlled training-time poisoning research on local Laya System 1; document learning, findings, and failures.
- **Task/target/triggers:** synthetic inbox routing; Priority human review; CF99 and Point Break.
- **Methods/training:** compare RLCD and SFT; use Colab and save checkpoints/results.
- **Dev:** matched primary set plus held-out-intent wording check.
- **Future matrix:** three seeds across RLCD/SFT × clean/CF99/Point Break: 18 fine-tunes plus the shared current-checkpoint baseline.
- **Clean control:** reuse one canonical clean training source; no duplicate file.
- **Input evidence:** capture actual prediction-path token IDs; this needs open-source internals and cannot work on a black-box service.
- **IT1 checks:** full data validation, fake-model integration, real-Laya smoke; evidence-completeness gate.
- **Gate samples:** sort matched-dev rows by sample ID, then seeded-random select ten.
- **Approved v1 (2026-11-02):** per label, 500 train, 100 matched dev, 100 held-out-intent dev, 100 reserved final-test. Keep current eight assistant-drafted held-out intent phrases per label; openings/details stay shared.
- **Seeds:** data 20261017; gate samples 20261018.
- **Workflow:** dev-only gates; test untouched until final iteration; stop until user writes APPROVED under HUMAN REVIEW.

Numeric training seeds, poison rate/insertion, and training settings remain for later decisions. Approval is not execution evidence.
