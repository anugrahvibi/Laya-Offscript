# App flow IT1

**Status:** Approved v1; user-approved 2026-11-02. No execution has occurred.

~~~mermaid
flowchart TD
    A[Approved fixture and JSON config] --> B[Generate clean train]
    A --> C[Generate matched and held-out-intent dev]
    B --> D[Validate files, counts, and hashes]
    C --> D
    D --> E[Fake-model integration checks]
    E --> F[Small pinned Laya smoke]
    F --> G[Score every row in both dev tracks]
    G --> H[Metrics, plots, actual token IDs, ten samples]
    H --> I[Facts-only gate; stop for human review]
    T[Test data] -. final iteration only .-> X[Not read in IT1]
~~~

Run .venv/bin/python src/m2_data.py. It writes 2,000 train rows and 400 rows per dev track, validates them, then records a manifest. Run .venv/bin/python -m unittest discover -s tests -p 'test_m2_data.py'. Smoke and full commands:

~~~sh
.venv/bin/python src/m2_eval.py --data-dir data/m2/clean_v1 --manifest data/m2/clean_v1/manifest.json --out-dir results/m2/it1/baseline_v1 --smoke
.venv/bin/python src/m2_eval.py --data-dir data/m2/clean_v1 --manifest data/m2/clean_v1/manifest.json --out-dir results/m2/it1/baseline_v1
~~~

Use data seed 20261017 and gate-sample seed 20261018. Capture IDs inside actual Laya prediction; this needs open-source internals. No training or poisoning in IT1. At the facts-only gate, stop.
