# Engineering Stories

OrbitFabric Engineering Stories are reproducible technical investigations built around real engineering questions.

They complement the Reference Mission tutorial rather than replace it. The Reference Mission provides a shared canonical mission model; each Engineering Story selects a meaningful slice of that model and exercises it against a concrete engineering problem, toolchain, runtime, or integration boundary.

A complete Engineering Story is intentionally layered:

```text
Front Story
    Why does this matter?
    What problem did we explore?
    What did we learn?

Technical Deep Dive
    How exactly does it work?
    Where are the ownership boundaries?
    What evidence supports the claims?

Reference Project
    Can I inspect it?
    Can I run it?
    Can I reproduce the result?
```

The three layers form one package. The Story establishes the engineering thesis, the Deep Dive makes the mechanics and evidence explicit, and the Reference Project provides the executable proof surface.

Most Stories use the canonical OrbitFabric Reference Mission as their upstream mission context. This keeps the examples connected to one coherent mission model instead of turning the repository into a collection of unrelated demos.

## R1 — One Mission Contract Across Flight and Ground

The first Engineering Story asks whether one mission-level semantic root can drive independently owned flight and ground engineering paths without forcing either side to adopt the other's implementation model.

The demonstrated vertical slice uses OrbitFabric, F Prime, and OpenC3 COSMOS around one real command-and-telemetry verification loop.

- [Read the R1 Engineering Story](r1-flight-ground/index.md)
- [Read the R1 Technical Deep Dive](r1-flight-ground/technical-deep-dive.md)
- [Inspect the accepted R1 Reference Project baseline](https://github.com/OrbitFabric/orbitfabric-reference-mission/tree/d66f6068235d425bdc2335d4b0cb09a58e70c1de/engineering-stories/01-one-contract-flight-ground/reference-project)

The executable project remains repository-side under `engineering-stories/01-one-contract-flight-ground/reference-project/`; the published Story and Deep Dive remain under `docs/`.

## R2 — One Intent, Two Executions

R2 is the current Engineering Story in progress.

It asks whether one mission operation, expected to execute once, can preserve a trustworthy semantic lineage through projection into an external runtime and then reconcile expected execution multiplicity with runtime-observed multiplicity.

Current status:

- G0 offline identity and deterministic assessment: accepted;
- G1 PWNSAT / FlatSat projection lineage: accepted;
- bounded runtime-proof phase: active in Draft PR #13;
- physical FlatSat execution: **NOT RUN**;
- final public Story / Technical Deep Dive: not yet published.

- [Inspect the accepted R2 repository-side package](https://github.com/OrbitFabric/orbitfabric-reference-mission/tree/main/engineering-stories/02-one-intent-two-executions)
- [Follow the active R2 Draft PR #13](https://github.com/OrbitFabric/orbitfabric-reference-mission/pull/13)

The runtime candidate remains separate from the accepted `main` baseline until the physical proof is completed and accepted.
