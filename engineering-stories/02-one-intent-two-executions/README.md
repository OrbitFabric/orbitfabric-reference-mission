# R2 - One Intent, Two Executions

This directory contains the repository-side engineering package for R2, **One Intent, Two Executions**.

R2 asks whether one mission operation, expected to execute once, can preserve a trustworthy semantic lineage from OrbitFabric intent through projection into an external runtime and then compare:

```text
expected_execution_count = 1
observed_execution_count = ?
```

## Current status

The accepted `main` baseline contains:

- G0 offline identity and deterministic assessment;
- G1 PWNSAT / FlatSat projection lineage;
- the Story-local Scenario, Projection Profile, target source grounding, retained G1 artifacts, schemas and tests supporting those accepted stages.

The bounded runtime-proof phase is currently being developed and reviewed in Draft PR #13:

- [R2 bounded PWNSAT runtime proof — Draft PR #13](https://github.com/OrbitFabric/orbitfabric-reference-mission/pull/13)

That Draft candidate adds the Story-local runtime harness and evidence path needed to compare expected execution multiplicity with runtime-observed multiplicity.

**Physical FlatSat execution has NOT RUN.**

No physical P1/P2 presentations or E1/E2 runtime occurrence evidence are part of the accepted `main` baseline.

R2 is therefore **in progress**. The final public Engineering Story narrative has not yet been published.

## Inspect the accepted repository-side package

- [Reference Project](reference-project/)

The final published Story and Technical Deep Dive will live under `docs/` only after the runtime proof is complete and accepted.
