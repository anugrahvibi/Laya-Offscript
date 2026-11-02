# IT1 TRD — data generation

**Status:** Approved v1; no generation has run.

The generator reads the approved task fixture and JSON config. Default mode writes train, matched dev, and held-out-intent dev JSONL plus a manifest; it never writes test. Final-test mode requires the existing bundle and writes only test, preserving clean files and hashes.

Approved per-label counts: train 500, matched dev 100, held-out-intent dev 100, final test 100. Totals are 2,000 train, 400 per dev track, and 400 test rows. Data-selection seed: 20261017. Gate-sample seed: 20261018.

Train/matched/test use disjoint full opening-intent-detail combinations from the standard pool. Its 10 openings × 8 intents × 10 details gives 800 combinations per label; 700 are reserved across train/matched/test. Held-out dev uses the approved eight different intent phrases per label with shared openings/details.

Validate schema, balanced labels, unique IDs/states, split metadata, phrase-bank membership, trigger absence, disk counts, and hashes. Family names are metadata, not different generation methods.
