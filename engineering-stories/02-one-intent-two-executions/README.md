# R2 G0 - One Intent, Two Executions

This directory is the **implementation/reference-project workspace** for Engineering Story R2 G0.

It is **not** the final public Engineering Story narrative.

G0 proves only that the accepted R2 Story-owned contract and identity model can be expressed and assessed deterministically **offline**, without adding any new OrbitFabric Core semantic.

## G0 boundary

Implemented here:

- one Story-local Scenario for `obc.request_health_check`;
- Story-owned Experiment Definition schema;
- Story-owned Execution Observation Report schema;
- deterministic run-scoped authorized invocation identity `A`;
- structural and semantic validation;
- synthetic `CONFORMANT`, `DIVERGED`, `INCONCLUSIVE`, and `INVALID_RUN` fixtures;
- offline tests.

Not implemented here:

- PWNSAT or FlatSat execution;
- USB, serial, RF, C3, replay, or hardware access;
- PWNSAT Integration Package or Projection Profile;
- real projection lineage or target stimulus;
- Core, Mission Model, Evidence Set, or Studio changes;
- G1-G4;
- a public R2 claim.

See [`reference-project/`](reference-project/) for the executable G0 proof.
