# M2 build outline

**Status:** IT1 completed and gate approved on 2026-11-03. Training, poisoning, and final-test generation have not started.

Use synthetic inbox tickets with four labels and target “priority human review.” Per label: 500 train, 100 matched dev, 100 held-out-intent dev, and 100 final test reserved. IT1 writes 2,000 train and 800 dev rows; test remains ungenerated. Data seed: 20261017. Ten gate examples use seed 20261018. The approved held-out bank has eight intent phrases per label; openings and details stay shared.

IT1 order: generate clean train and two dev tracks; validate data and hashes; fake-model integration check; pinned Laya smoke; full dev evaluation; facts-only gate and stop.

Later compare RLCD and SFT, each with clean, CF99, and Point Break conditions across three training seeds: 18 fine-tunes plus one shared current-checkpoint baseline. Reuse one clean source. Exact training seed values and poison settings remain undecided; Colab must persist checkpoints and results.
