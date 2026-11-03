# Iteration 1 design

**Status:** Approved v1 design; no execution evidence exists.

~~~mermaid
flowchart LR
    A[Approved fixture/config] --> B[Canonical clean train]
    A --> C[Matched dev and held-out-intent dev]
    B --> D[Data validation and hashes]
    C --> D
    D --> E[Fake-model integration]
    E --> F[Real-Laya smoke]
    F --> G[Full dev evaluation]
    G --> H[Raw results, plots, ten matched samples]
    H --> I[Gate; stop for human review]
    T[Held-out test] -. final iteration only .-> X[Untouched]
~~~

Per label, use 500 train, 100 matched dev, 100 held-out-intent dev, and 100 reserved test rows. IT1 writes 2,000 train and 800 dev rows; test remains ungenerated. Data and gate-sample seeds are 20261017 and 20261018.

Matched dev is the primary comparison set; later clean, CF99, and Point Break checkpoints receive identical requests. The second track changes only intent phrases. Run data validation, fake-model integration, pinned Laya smoke, full dev scoring, then a facts-only gate. IT1 creates no poison data/checkpoint and performs no training. Current-checkpoint baseline differs from future fine-tuned clean controls.
