# Iteration 1 — M2 approved plan

**Status:** Approved v1; no M2 data or model run exists.

IT1 prepares a clean baseline for synthetic ticket routing. It creates one reusable clean training source and two dev tracks: matched requests for future checkpoint comparisons, plus a narrow check using intent phrases withheld from training. Openings, details, and the four-choice task stay the same in that second track.

Approved per-label counts are 500 train, 100 matched dev, 100 held-out-intent dev, and 100 final test. IT1 writes 2,000 train and 800 dev rows. Test remains ungenerated until the final iteration. The current eight held-out intent phrases per label are approved.

The future matrix is RLCD and SFT, each with clean, CF99, and Point Break conditions across three seeds: 18 fine-tunes plus the current-checkpoint baseline. IT1 captures the current model baseline only; it does not train or poison.

Data seed: 20261017. Gate-sample seed: 20261018. Input IDs are captured inside open-source Laya's actual prediction path; black-box endpoints do not expose these internals.
