# R2 G0/G1 Reference Project

This Reference Project is the executable workspace for R2, **One Intent, Two Executions**.

G0 remains the accepted and closed offline contract / identity proof. G1 adds a separate **projection-lineage** proof. Neither gate executes PWNSAT or establishes runtime truth.

## Preserved G0 boundary

The canonical Reference Mission and canonical top-level `scenarios/` set are unchanged.

The Story-local Scenario is:

```text
scenario/r2_g0_health_check.yaml
```

It references the unchanged mission and declares exactly one command action:

```text
obc.request_health_check
```

G0 resolves the command atom from the Core-emitted Scenario Declaration rather than YAML/list position. Its Story-owned contracts remain unchanged:

```text
schemas/pwnsat-experiment-definition-0.1-story.schema.json
schemas/pwnsat-execution-observation-0.1-story.schema.json
```

The retained G0 Experiment Definition and Observation Report fixtures remain explicitly synthetic `0.1-story` artifacts. Their projection identities are still synthetic placeholders and are **not reinterpreted** as G1 projection evidence.

G0's authorized invocation `A`, assessment rules, and `CONFORMANT / DIVERGED / INCONCLUSIVE / INVALID_RUN` vocabulary are not changed by G1.

## G1 projection-lineage boundary

G1 proves only this offline chain:

```text
Core Integration Input Set
    -> exact commands/obc.request_health_check
    -> Core-emitted Scenario atom
    -> Story-local Projection Profile
    -> pinned Pwnsat/FlatSat source baseline
    -> explicit Story-local mapping
    -> deterministic frozen target stimulus
    -> Integration Result 0.2-candidate
    -> Scenario Projection Accounting 0.1-candidate
```

The Story-local Integration Package owns projection only.

The retained G1 mapping explicitly preserves:

```text
PROJECTED != TRANSMITTED != EXECUTED != OBSERVED
```

No device is opened. No command is transmitted. No FlatSat, USB, serial, RF, PWNSAT-C3, replay, STATUS capture, runtime occurrence identification, or runtime Observation Report production occurs in G1.

## Pinned PWNSAT target baseline

The target representation is grounded in:

```text
Pwnsat/FlatSat
b5ac0f2ba5e7bd60fbb6994f681c28053777628e
```

The exact reviewed source-file identities are retained in:

```text
target/pwnsat-source-baseline.json
```

The source establishes that the target command corresponding to the bounded health-check request is FlatSat `STATUS` / `SPP_APID_TC_GET_STATUS`, APID `0x0C`, and that the firmware dispatches that telecommand to `telemetrySPPTransmitMissionStatus()`.

The source baseline also fixes the SPP primary-header rules and default secure-link representation used to materialize the G1 stimulus.

## Projection Profile

The authored target-specific intent is:

```text
profile/pwnsat-flat-sat-health-check.yaml
```

It uses the existing generic Projection Profile envelope. PWNSAT-specific fields remain inside integration-owned `settings` / binding `config`; they do not become Core semantics.

## Retained G1 artifacts

```text
artifacts/g1/pwnsat-health-check.mapping.json
artifacts/g1/pwnsat-health-check.tc.bin
artifacts/g1/integration_result.json
artifacts/g1/scenario_projection_accounting.json
```

`pwnsat-health-check.tc.bin` is an exact deterministic **projection artifact**. Its presence is not evidence that the packet was ever transmitted or executed.

The Integration Result records exact IISS, Profile, Scenario, mapping, target-baseline, generated-artifact and accounting identities.

Scenario Projection Accounting is generated from the actual Core-emitted Scenario Declaration. Every atom receives an explicit disposition and only the semantically resolved command atom is associated with the PWNSAT mapping.

## Core baseline split

The accepted G0 workflow remains pinned to:

```text
760f364875515c4f4ac0675b5545a2ee0ebc22ad
orbitfabric 1.3.0
```

G1 uses the direct child:

```text
b4e1185de4931ff125be699dfe09f63ab3746015
orbitfabric 1.3.0
```

That Core commit publishes the already accepted generic Scenario Projection Accounting contract required by G1. It introduces no Mission or Scenario semantic change. G0 files and semantics are not repinned or rewritten.

## Run G0 locally

With the G0 Core baseline installed:

```bash
./engineering-stories/02-one-intent-two-executions/reference-project/run_g0.sh
```

## Run G1 locally

With the G1 Core baseline and Python `cryptography==46.0.7` installed:

```bash
./engineering-stories/02-one-intent-two-executions/reference-project/run_g1.sh
```

The G1 runner:

1. exports the exact Core Integration Input Set;
2. exports the Story-local Scenario Declaration;
3. resolves the canonical command from the IISS;
4. resolves the exact command atom from declaration semantics;
5. validates the pinned PWNSAT source baseline and Profile;
6. deterministically regenerates mapping, stimulus, Integration Result and Scenario Projection Accounting;
7. validates the Result/accounting bundle through the Core conformance checker;
8. compares regenerated outputs byte-for-byte with retained artifacts;
9. performs a second clean regeneration and verifies identical identities;
10. runs the G1 offline unit suite.

## Current boundary

```text
G0    ACCEPTED / CLOSED
G1    IMPLEMENTATION CANDIDATE / OFFLINE PROJECTION ONLY
G2    NOT AUTHORIZED
G3    NOT AUTHORIZED
G4    NOT AUTHORIZED
```

G1 does not authorize runtime execution or public R2 publication.
