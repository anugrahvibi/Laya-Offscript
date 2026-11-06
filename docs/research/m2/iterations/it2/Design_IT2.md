# IT2 design

**Status:** Approved v1. Core trainer/evaluator files exist; CLI artifact transfer and verification remain pending.

~~~mermaid
flowchart LR
    L[Local CLI + code/data] -->|upload| C[Named Colab T4 session]
    B[Pinned M1 + config] --> C
    C --> R[Full-state epoch checkpoint]
    R -->|colab download| A[Ignored local artifacts]
    C --> I[Calibrated inference checkpoint]
    I --> E[Actual-path evaluator]
    D[IT1 dev rows] --> E
    E --> O[Row outputs + metrics]
    O -->|download| A
    A --> G[IT2 facts-only gate]
    G --> H[Human review; stop]
~~~

Keep resumable state separate from inference output. Download completed-epoch states and results to `artifacts/m2/it2/`, ignored by Git; do not mount Drive. Evaluation creates suffixes in memory, preserving canonical dev files. Record artifact hashes and actual GPU/session details. M1 probabilities retain IT1's uncalibrated warning.
