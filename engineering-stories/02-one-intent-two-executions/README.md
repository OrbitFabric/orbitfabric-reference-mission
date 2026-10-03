# R2 - One Intent, Two Executions

This directory contains the current engineering package for R2, **One Intent, Two Executions**.

R2 asks whether one mission operation, expected to execute once, can preserve a trustworthy semantic lineage from OrbitFabric intent through projection into an external runtime and then compare:

```text
expected_execution_count = 1
observed_execution_count = ?
```

Current state:

- G0 identity and deterministic assessment are completed offline;
- G1 PWNSAT projection lineage is completed offline;
- the bounded PWNSAT/FlatSat runtime harness is implemented and offline-verified;
- physical FlatSat execution is **NOT RUN**;
- no physical P1/P2 presentations or E1/E2 runtime occurrence evidence exist yet.

This directory is an engineering/reference package. It is **not yet the final published Engineering Story narrative**.

For an external PWNSAT-oriented review, start here:

- [PWNSAT Maintainer Review](PWNSAT-MAINTAINER-REVIEW.md)

For the executable package, contracts, projection artifacts, runtime harness and detailed technical documentation:

- [Reference Project](reference-project/)
