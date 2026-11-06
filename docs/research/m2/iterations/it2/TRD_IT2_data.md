# IT2 TRD — data and inputs

**Status:** Approved v1; user-approved 2026-11-06.

Use only IT1 `clean_v1`: 2,000 train rows, 400 `dev_matched`, and 400 `dev_unseen`. Verify the IT1 manifest and hashes before `colab upload`; do not regenerate data. Upload only project code and synthetic study files. Test data remains ungenerated and inaccessible.

Laya 0.4.6 reserves `min(400, 10% of 2,000) = 200` train items for calibration; the remaining 1,800 are optimized. Use calibration seed 20260922 so all six runs hold out the same rows. Record the calibration class counts and hashes.

For dev probes, make transient copies of each request. Append exactly one space and one trigger (`CF99` or `Point Break`) to `state`; preserve question, options, and expected label. Never add triggers to IT2 training data. Keep clean, CF99, and Point Break conditions separate.

Use Colab CLI transfer, not a notebook or Drive mount. After each completed epoch, download its full-state checkpoint to ignored local `artifacts/m2/it2/`; retrieve final outputs there too. If a session ends, upload the latest complete checkpoint to a new T4 session. No customer or private data.
