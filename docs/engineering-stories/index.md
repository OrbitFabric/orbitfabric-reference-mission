# Engineering Stories

OrbitFabric Engineering Stories are reproducible technical investigations built around real engineering questions.

They complement the Reference Mission tutorial rather than replace it. The Reference Mission provides a shared canonical mission model; each Engineering Story selects a meaningful slice of that model and exercises it against a concrete engineering problem, toolchain, runtime, or integration boundary.

Every Engineering Story has two required layers:

```text
Front Story
    Why does this matter?
    What problem did we explore?
    What did we learn?

Reference Project
    Can I inspect it?
    Can I run it?
    Can I reproduce the result?
```

A **Technical Deep Dive is optional**. It is added when the mechanics, ownership boundaries and retained evidence need a separate technical document rather than more weight in the narrative.

R1 uses Story + Technical Deep Dive + Reference Project. R2 intentionally uses Story + Reference Project: its exact schemas, source baselines, projection artifacts, runtime harness and evidence machinery already live in the executable package.

Most Stories use the canonical OrbitFabric Reference Mission as their upstream mission context. This keeps the examples connected to one coherent mission model instead of turning the repository into a collection of unrelated demos.

## R1 — One Mission Contract Across Flight and Ground

The first Engineering Story asks whether one mission-level semantic root can drive independently owned flight and ground engineering paths without forcing either side to adopt the other's implementation model.

The demonstrated vertical slice uses OrbitFabric, F Prime, and OpenC3 COSMOS around one real command-and-telemetry verification loop.

- [Read the R1 Engineering Story](r1-flight-ground/index.md)
- [Read the R1 Technical Deep Dive](r1-flight-ground/technical-deep-dive.md)
- [Inspect the accepted R1 Reference Project baseline](https://github.com/OrbitFabric/orbitfabric-reference-mission/tree/d66f6068235d425bdc2335d4b0cb09a58e70c1de/engineering-stories/01-one-contract-flight-ground/reference-project)

The executable project remains repository-side under `engineering-stories/01-one-contract-flight-ground/reference-project/`; the published Story and Deep Dive remain under `docs/`.

## R2 — One Intent, Two Executions

The second Engineering Story explores whether one unchanged mission intent can be projected into an independently owned FlatSat runtime, while distinguishing authorized invocation, controlled presentation, target-produced observations, and evidence-supported execution occurrences.

The published Front Story presents the engineering reasoning and the reproducible offline work; it **does not claim physical FlatSat execution**.

Current status:

- G0 offline contract and identity proof: **accepted / closed**;
- G1 offline PWNSAT projection lineage: **accepted / closed**;
- bounded runtime harness: **implemented and verified offline (33/33 runtime tests at the published offline baseline)**;
- physical FlatSat execution: **NOT RUN**, so no physical P1/P2 or accepted E1/E2 and no observed FlatSat multiplicity;
- final runtime phase acceptance: **pending physical evidence and a separate review**;
- publication model: **Front Story + Reference Project**; no separate Technical Deep Dive is required for the current R2 baseline.

The Front Story retains a commit-pinned Reference Project link as an archival publication checkpoint. For the maintained publication status and complete offline harness documentation, use the current Reference Project link below.

- [Read the R2 Front Story](r2-pwnsat/index.md)
- [Inspect the R2 Reference Project](https://github.com/OrbitFabric/orbitfabric-reference-mission/tree/main/engineering-stories/02-one-intent-two-executions/reference-project)
- [Read the PWNSAT Maintainer Review](https://github.com/OrbitFabric/orbitfabric-reference-mission/blob/main/engineering-stories/02-one-intent-two-executions/PWNSAT-MAINTAINER-REVIEW.md)

The Story explains why the current evidence is deliberately bounded. New external hardware evidence or maintainer corrections can be added later without rewriting the historical offline conclusions.
