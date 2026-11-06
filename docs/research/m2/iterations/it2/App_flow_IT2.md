# IT2 app flow

**Revision:** v2 (2026-11-06; status only). Approved v1 flow unchanged. Core code files are present; verification and training remain pending.

~~~mermaid
flowchart TD
    A[Local code + IT1 data] --> B[Colab CLI: named T4 session]
    B --> C[Upload inputs; install pinned dependencies]
    C --> D[Verify T4, CUDA, hashes; dry-run]
    D --> E[Fake tests + remote Laya smoke + resume check]
    E --> F[Six clean controls, sequentially]
    F --> G[Save each epoch; download state locally]
    G --> H[Calibrate; evaluate M1 + controls on dev]
    H --> I[Download results; stop Colab session]
    I --> J[Write facts-only gate; stop for review]
    T[Test + poisoned data] -. untouched .-> X[Later iteration]
~~~

Use `colab new -s m2-it2-clean-controls --gpu T4`, `colab install`, `colab upload/download`, `colab exec`, then `colab stop`. No browser notebook or Drive mount is required. Stop before full runs unless T4/CUDA, hashes, dry-run, smoke, and resume checks pass. Each control starts at the pinned base; save full state after every epoch and download it to ignored local artifacts. Calibrate and save inference checkpoints. Never train locally or tune from dev scores.
