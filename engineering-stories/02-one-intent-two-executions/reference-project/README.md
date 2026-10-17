# R2 Reference Project - One Intent, Two Executions

This is the executable proof package behind R2, **One Intent, Two Executions**.

The [published R2 Front Story](../../../docs/engineering-stories/r2-pwnsat/index.md) explains the investigation. This README describes the maintained Reference Project and its actual publication status; older commit-pinned source snapshots may preserve earlier authorization checkpoints.

The published package spans three deliberately separated layers:

```text
G0
    Story-local contract / identity / deterministic assessment proof

G1
    accepted offline PWNSAT projection lineage

bounded runtime harness
    implemented and verified offline
    physical FlatSat execution = NOT RUN
```

The package preserves each phase as historical evidence rather than rewriting earlier fixtures after later phases become available. **No physical PWNSAT/FlatSat runtime has been exercised and no cybersecurity claim is made.**

## G0 foundation

Everything retained under the original G0 fixtures remains offline and synthetic by design.

## Boundary

The canonical Reference Mission and canonical top-level `scenarios/` set are unchanged.

The Story-local Scenario is:

```text
scenario/r2_g0_health_check.yaml
```

It references the unchanged mission via `../../../../mission` and declares exactly one command action:

```text
obc.request_health_check
```

The pinned OrbitFabric Core exports its Scenario Declaration. G0 resolves the command atom by inspecting the Core-emitted atom `kind` and role-labelled `commands/obc.request_health_check` reference. It does **not** infer the atom id from YAML/list position.

The retained synthetic Experiment Definition is regenerated from that Core declaration during validation and compared byte-for-byte with the checked-in fixture.

## Story-owned contracts

```text
schemas/pwnsat-experiment-definition-0.1-story.schema.json
schemas/pwnsat-execution-observation-0.1-story.schema.json
```

Both formats are closed, versioned Story contracts:

```text
orbitfabric.reference_mission.pwnsat_experiment_definition
orbitfabric.reference_mission.pwnsat_execution_observation
format_version = 0.1-story
```

They are not Core, Mission Model, Studio, or generic OrbitFabric contracts.

## Exact Experiment Definition identity

The Experiment Definition identity is:

```text
SHA-256(exact retained UTF-8 file bytes)
```

There is no self-digest field.

## Authorized invocation A

`A` is Story-owned, run-scoped, and distinct from the Scenario atom.

The exact preimage is:

```text
UTF-8(
    "orbitfabric-r2-authorized-invocation-v1" + LF +
    experiment_definition_sha256 + LF +
    execution_attempt_id + LF +
    authorized_instance.local_id + LF
)
```

Then:

```text
A = "r2a:" + lowercase_hex(SHA-256(preimage))
```

The schemas constrain variable identifiers so LF cannot appear in them, making the encoding unambiguous.

`A` is not a global Core `OperationInstance`.

## Deterministic assessment

The Story-owned assessment order is:

```text
invalid required run precondition
    -> INVALID_RUN

otherwise insufficient/ambiguous occurrence evidence
    -> INCONCLUSIVE

otherwise observed_execution_count == expected_execution_count
    -> CONFORMANT

otherwise
    -> DIVERGED
```

`observed_execution_count` is accepted only when occurrence evidence is `complete`, and it must equal the number of explicit nested execution-occurrence records with `accepted: true`.

`PASS` / `FAIL` are test or acceptance-gate states only; they are not R2 semantic outcomes.

## Synthetic fixtures

```text
fixtures/experiment-definition.synthetic.json
fixtures/observations/conformant.synthetic.json
fixtures/observations/diverged.synthetic.json
fixtures/observations/inconclusive.synthetic.json
fixtures/observations/invalid-run.synthetic.json
```

The projection fields in the retained G0 Experiment Definition remain deterministic synthetic placeholders **by design**. They are historical G0 evidence and are not rewritten after G1. The real accepted G1 mapping, Integration Result, Scenario Projection Accounting and frozen stimulus are retained separately under `artifacts/g1/`.

The synthetic G0 occurrence criterion is deliberately Story-local and does not encode FlatSat STATUS parsing, telemetry sequencing, or any other real runtime rule.

## Run locally

Use the same OrbitFabric Core baseline pinned by the repository CI, then run from repository root:

```bash
./engineering-stories/02-one-intent-two-executions/reference-project/run_g0.sh
```

The runner:

1. asks Core to export the Story-local Scenario Declaration;
2. resolves `obc.request_health_check` from declaration content;
3. regenerates the synthetic Experiment Definition and checks byte identity;
4. validates all schemas and cross-references;
5. recomputes all four semantic outcomes;
6. runs the offline unit suite.

No network, external runtime, Studio, hardware, USB, or RF access is required after the pinned Core is installed.

## G1 projection lineage

G0 remains **ACCEPTED / CLOSED** and its retained `0.1-story` synthetic contracts, fixtures, authorized invocation `A`, and assessment vocabulary are unchanged.

G1 is implemented here as the **accepted / closed offline projection lineage**:

```text
Core Integration Input Set
    -> exact commands/obc.request_health_check
    -> exact Core-emitted Scenario atom
    -> Story-local Projection Profile
    -> pinned Pwnsat/FlatSat source baseline
    -> explicit Story-local target mapping
    -> deterministic frozen target stimulus artifact
    -> Integration Result 0.2-candidate
    -> Scenario Projection Accounting 0.1-candidate
```

The pinned target source baseline is:

```text
Pwnsat/FlatSat
b5ac0f2ba5e7bd60fbb6994f681c28053777628e
```

Exact reviewed source-file identities are retained in:

```text
target/pwnsat-source-baseline.json
```

The source-grounded target operation is FlatSat `STATUS` / `SPP_APID_TC_GET_STATUS`, APID `0x0C`, whose firmware dispatch calls `telemetrySPPTransmitMissionStatus()`.

G1 artifacts are retained under:

```text
artifacts/g1/pwnsat-health-check.mapping.json
artifacts/g1/pwnsat-health-check.tc.bin
artifacts/g1/integration_result.json
artifacts/g1/scenario_projection_accounting.json
```

The binary stimulus is a projection artifact only. Its presence means **PROJECTED**, not transmitted, executed, or observed.

The G1 workflow uses Core commit:

```text
b4e1185de4931ff125be699dfe09f63ab3746015
orbitfabric 1.3.0
```

This is the direct child of the G0 Core pin that publishes the accepted generic Scenario Projection Accounting contract. The existing G0 workflow remains on its original pin.

Run G1 with that Core baseline and Python `cryptography==46.0.7` installed:

```bash
./engineering-stories/02-one-intent-two-executions/reference-project/run_g1.sh
```

The runner exports the IISS and Scenario Declaration, regenerates all G1 artifacts, validates the existing Integration Result / Scenario Projection Accounting contracts, compares retained bytes, performs a second clean regeneration, and runs the offline test suite.

No PWNSAT runtime, FlatSat hardware, USB, serial, RF, PWNSAT-C3 execution, command transmission, STATUS capture, replay, runtime occurrence evidence, or runtime Observation Report production is part of G1.

## G2-G4 bounded runtime proof phase

Architecture Lab Decision 029 authorizes G2, G3 and G4 as one continuous bounded runtime proof phase. G0 and G1 remain accepted / closed.

The runtime harness is documented under:

```text
runtime/README.md
```

The published runtime harness includes transport framing/parsing, STATUS validation, the frozen occurrence criterion, additive `0.2-story` runtime contracts, evidence retention, full-phase orchestration, bundle sealing/verification and falsification tests.

Repository CI remains offline-only. It does not open hardware and produces an explicit `NOT_RUN` observation report with no presentation or occurrence evidence. The published offline baseline has **33/33 runtime tests passing**.

The bounded offline R2 Story and this Reference Project are **published**. Physical FlatSat execution remains **NOT RUN**, so final runtime-phase acceptance and any live semantic assessment remain pending.
