# Using PWNSAT FlatSat as an External Runtime for OrbitFabric R2

## The question

OrbitFabric R2 is a systems/runtime-verification experiment about semantic continuity, execution multiplicity and evidence provenance.

One mission operation is expected to execute once:

```text
obc.request_health_check
expected_execution_count = 1
```

The experiment preserves the identity of that intent through projection into an external runtime, then asks what the runtime evidence supports:

```text
observed_execution_count = ?
```

The goal is not to prove a generic replay vulnerability or a general security property of PWNSAT. The goal is to determine whether the observed runtime occurrences can be attributed and counted against one frozen mission intent.

## Why PWNSAT / FlatSat

FlatSat is useful here because it provides a concrete external flight-like software/runtime boundary rather than another OrbitFabric-native execution path.

The pinned PWNSAT source exposes:

- a concrete command path for `GET_STATUS / STATUS`;
- a corresponding `TM_STATUS` telemetry response;
- a wired USB CDC transport implementation;
- native telemetry sequence identity;
- STATUS uptime/runtime state that can help distinguish successive observations.

That gives the experiment target-native evidence instead of inventing OrbitFabric-specific runtime markers.

## How we mapped the experiment

```text
OrbitFabric mission operation
    obc.request_health_check
             |
             v
Story-local scenario
             |
             v
PWNSAT projection
    FlatSat STATUS command
             |
             v
frozen command representation
             |
             v
wired USB CDC boundary
             |
             v
FlatSat runtime
             |
             v
TM_STATUS
             |
             v
native sequence + uptime + retained evidence
             |
             v
expected execution count vs observed execution count
```

The accepted OrbitFabric-side projection remains frozen before the runtime boundary. USB framing is added only when crossing into the wired FlatSat transport.

On observation, the runtime harness retains native received bytes and derives occurrence evidence from PWNSAT telemetry, including TM sequence identity and STATUS uptime progression.

## What is already verified

The following has been verified **offline, in software**:

- deterministic OrbitFabric mission/Scenario identity for `obc.request_health_check`;
- the exact Core-emitted Scenario command atom;
- PWNSAT projection lineage to FlatSat `STATUS`;
- source grounding against pinned `Pwnsat/FlatSat` source;
- preservation of the frozen command representation before transport framing;
- wired USB CDC framing and receive-stream parsing based on the repository's existing transport semantics;
- `TM_STATUS` validation;
- extraction of native TM sequence identity and STATUS uptime;
- Story-owned execution-occurrence criteria;
- exact attempt and presentation provenance;
- retained raw stream and raw SPP evidence handling;
- deterministic assessment paths for `CONFORMANT`, `DIVERGED`, `INCONCLUSIVE`, and `INVALID_RUN`;
- complete offline runtime harness verification with **33/33 tests passing**.

The test suite also exercises ambiguous attribution and refuses to treat STATUS alone as sufficient occurrence evidence.

These results verify the harness and evidence model. They are **not** physical FlatSat execution results.

## What has NOT been run

**Physical FlatSat execution = NOT RUN.**

There has been:

- no physical P1 presentation;
- no physical P2 presentation;
- no accepted physical E1 occurrence;
- no accepted physical E2 occurrence;
- no physical observed execution count.

A controlled FlatSat runtime is not currently available to this execution environment, so no physical runtime evidence has been created or implied.

## What we would value from the PWNSAT maintainer

We would especially value a technical review of these points:

- Is the wired USB CDC STATUS path the most appropriate or representative FlatSat path for this experiment?
- Are `TM_STATUS` sequence identity and STATUS uptime sensible native facts for distinguishing successive runtime observations?
- Are there target/runtime assumptions in our source-derived model that you would change?
- Is there another supported way to exercise this runtime boundary without owning a physical FlatSat?
- Is there a better PWNSAT-native observation you would recommend for distinguishing accepted execution occurrences?

The intent is to validate the runtime model before any physical experiment, not to ask PWNSAT to adopt OrbitFabric-specific semantics.

## Inspect the implementation

- [Reference Project](reference-project/README.md)
- [Runtime Harness](reference-project/runtime/README.md)
- [Occurrence Criterion](reference-project/runtime/occurrence-criterion-0.1-story.json)
- [Pinned Runtime Transport Source Baseline](reference-project/runtime/pwnsat-runtime-transport-source-baseline.json)
