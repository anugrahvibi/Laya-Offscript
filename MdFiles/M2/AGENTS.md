# M2 contributor instructions

Read CODEX.md, current iteration documents, and DECISION_LOG.md before editing. Use synthetic tickets only. Preserve raw outputs, failures, and completed run records.

IT1 Draft v1 contracts were approved on 2026-11-02. Frozen files include PRD, App_flow, TRD, artifact schema, SECURITY, and GATE_TEMPLATE; frozen content includes metrics, evaluation protocol, split wording, target, and trigger identities. Change one only after written user approval, a v1-to-v2 bump, and a reason in CHANGELOG.md.

Config is living for run settings such as counts and seeds. It cannot silently redefine frozen labels, target, trigger identities, split wording, schemas, or metrics. Record only user-stated choices and approvals in DECISION_LOG.md.

Follow App_flow_IT1.md in order when executing IT1. Exit means complete evidence, not a favorable score. At the gate, write only GATE_IT1.md with facts; leave HUMAN REVIEW blank and stop. Do not read test data before the final iteration.

Keep each agent-written file below 200 words except a gate. Approved contracts are not run evidence.
