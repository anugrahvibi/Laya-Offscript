# M2 contributor instructions

Read CODEX.md, current iteration documents, and DECISION_LOG.md before editing. Use synthetic tickets only. Preserve raw outputs, failures, and completed run records.

IT1 v1 contracts were approved on 2026-11-02; metric contract v2 on 2026-11-05. IT2 v1 was approved on 2026-11-06, including Colab CLI, named T4 sessions, no local training, and epoch checkpoint downloads. Frozen files include PRD, App_flow, TRD, artifact schema, SECURITY, and GATE_TEMPLATE. Changes need written approval, a version bump, and a CHANGELOG.md reason.

Config is living for run settings such as counts and seeds. It cannot silently redefine frozen labels, target, trigger identities, split wording, schemas, or metrics. Record only user-stated choices and approvals in DECISION_LOG.md.

IT1 execution and gate review are complete; do not rerun it. Build and verify IT2 code before its six runs. Follow `colab-cloud-training`: request T4, verify actual T4/CUDA, stop on mismatch; never train locally or mount Drive. Gates need complete evidence, not favorable scores; write only that facts-only gate, leave HUMAN REVIEW blank, and stop. Keep test data closed until final iteration.

Keep each agent-written file below 200 words except a gate. Approved contracts are not run evidence.
