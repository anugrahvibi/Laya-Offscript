# M2 security contract

**Approved v1 — user-approved 2026-11-02.**

- Use synthetic ticket text only. Do not add real customer, personal, or proprietary data.
- Keep Colab credentials and tokens out of notebooks, source, Git, and artifacts. Use the runtime secret store if needed.
- Restrict access to checkpoints and run outputs. Review artifacts before publication.
- Record checkpoint and dataset identifiers or hashes. A hash supports comparison; it does not prove provenance.
- Study the selected local, open-weight Laya checkpoint only. Do not generalize results to hosted Jev.
- Input capture wraps Laya's private encoder inside the prediction path. It needs inspectable open-source internals; it cannot capture tokens from a black-box hosted service.
- The held-out wording check uses synthetic text and tests held-out intent phrases under shared openings/details; it is not broad language-robustness evidence.
- Distribution of trained poisoned checkpoints remains undecided and needs a separate user decision.

No private data, credentials, checkpoints, or experiment results were added in this planning update.
