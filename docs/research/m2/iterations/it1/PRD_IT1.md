# IT1 PRD — clean data and baseline

**Revision:** v2 (2026-11-03; status only). Approved v1 protocol unchanged. IT1 completed; gate approved 2026-11-03. See [GATE_IT1.md](../../gates/GATE_IT1.md).

IT1 prepares one canonical synthetic inbox-routing training set, a matched primary dev set, and a second dev set with held-out intent phrases. Both dev tracks use the fixed four-choice category task. The held-out test split stays ungenerated until the final iteration.

The target label is Priority human review and has ordinary clean examples. Full states are unique across generated splits. The held-out wording track changes intent phrases only; openings/details may recur, so it is a narrow wording-transfer check.

Approved counts per label: 500 train, 100 matched dev, 100 held-out-intent dev, and 100 final test. IT1 writes 2,000 train plus 800 dev rows. The approved held-out bank uses the current eight assistant-drafted intent phrases per label.

Validation checks schema, labels, balanced counts, split metadata, unique IDs/states, phrase bank, trigger absence, round trip, and manifest hashes. Evaluate both dev tracks on the pinned current checkpoint. Record metrics, raw outputs, actual token IDs, plots, and ten seeded matched-dev examples. Exit requires complete evidence, not a good score. No poisoning or training occurs in IT1.
