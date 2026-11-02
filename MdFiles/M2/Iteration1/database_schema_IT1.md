# IT1 artifact schema

**Status:** Approved v1; file artifacts only; no database is proposed.

Each UTF-8 JSONL row has sample_id, split, template_family, synthetic state, fixture-shaped questions, and expected.category.choice. The choice must be one of the four fixture labels.

IT1 files are train.jsonl, dev_matched.jsonl, and dev_unseen.jsonl. The manifest records fixture/config SHA-256 and row count/hash per split. No test file or hash exists until the final iteration.

The baseline JSON stores model repository/revision, Laya version, device, code commit/source hashes, manifest, data/gate seeds, metrics by dev track, plot paths, ten sample IDs, examples, and scored rows. Each scored row stores request, expected/selected labels, probabilities, raw response, actual token IDs, and decoded input view.

Plots include separate confusion and expected-label probability charts for each dev track. IT1 never loads test data or creates poisoned data/checkpoints.
