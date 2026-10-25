# Limitations and ethical considerations

- The synthetic dataset demonstrates the model; it is not a real organization or validated security assessment.
- Reachability is determined only by supplied rows. Missing relationships can hide paths; inaccurate rows can create false paths.
- The score is a transparent triage heuristic. It is not calibrated to breach probability, exploitability, or financial loss.
- A weakness is modeled at row level. Removing every row with that label is a coarse simulation and may remove more than one relationship.
- The graph is directed, static, and does not represent conditional access, time, authentication factors, network protocol details, or dynamic policy evaluation.
- The path and input limits reduce runaway work but do not guarantee responsiveness on every dense graph.
- CSV data is not persisted by the app, but users remain responsible for handling any authorized uploaded data appropriately.
- The application performs no discovery, authentication, exploitation, or infrastructure change. Findings must be independently reviewed before any real remediation decision.

Use synthetic data or data for which analysis is authorized. Never upload passwords, authentication tokens, private keys, or other secrets.
