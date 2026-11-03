# TRD IT1 checks

**Status:** Approved v1; no check or model call has run.

- Validate JSONL schema, balanced counts, expected labels, unique IDs/states, split metadata, phrase bank, trigger absence, and manifest hashes.
- Fake-model integration checks dev loading, manifest validation, row processing, sampling, and output writing. It tests evaluator wiring, not Laya behavior.
- Real-Laya smoke scores two sorted IDs per dev track and records raw output and actual token IDs.
- Pin Laya 0.4.6 and revision 7b928d828b7b0e022f929d9bd2e44165aa270148; verify the loaded revision.
- Score every row separately in matched and held-out-intent dev. Report accuracy, macro-F1, confusion matrix, and mean expected-label probability.
- Accuracy = correct/total. Per-class F1 = 2TP/(2TP+FP+FN); macro-F1 averages four class F1 values. Record warnings; temperature fallback means probabilities are not proof of calibration.
- Sort matched-dev rows by sample ID; use gate seed 20261018 to select ten.
- Capture token IDs inside Laya's private prediction encoder. This needs open-source internals, not a black-box endpoint.

Gate exit means evidence completeness, regardless of scores. Test remains unopened until the final iteration.
