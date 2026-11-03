# M2 planning changelog

- **2026-10-29:** Drafted shared workflow, IT1 documents, config, fixture, generator, evaluator, and data checks. No run occurred.
- **2026-10-29:** Split the IT1 TRD into data/checks documents and reserved test generation for the final iteration.
- **2026-11-02:** Incorporated matched and held-out-intent dev tracks, three future training seeds, one clean source, actual-path input capture, evidence gates, fake-model integration, and real-Laya smoke.
- **2026-11-02:** Renamed the JSON-parsed config to .json and separated data and gate-sample seeds.
- **2026-11-02 — Initial v1 approval:** User selected 500/100/100/100 rows per label, the current eight held-out phrases per label, data seed 20261017, and gate seed 20261018. Fixture/config statuses are approved. This is initial approval, not a v2 amendment.
- **2026-11-02:** Left trigger insertion position out of the IT1 config because IT1 creates no poisoned data; decide it with the later poisoning recipe.
- **2026-11-02:** Updated M2 workflow and iteration records. No tests, data generation, inference, or training were run.
- **2026-11-03:** Recorded completed IT1 checks, data generation, pinned Laya evaluation, and human gate approval. Organized M2 documentation under `docs/research/m2/`, with IT1 plans under `iterations/it1/` and gate records under `gates/`; artifact directories and hashes remain unchanged.
