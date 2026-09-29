# R2 G0 Offline Contract / Identity Proof

This Reference Project is the executable G0 slice for R2, **One Intent, Two Executions**.

Everything in G0 is offline. All runtime/projection identities retained in the fixtures are explicitly synthetic placeholders. **No PWNSAT runtime has been exercised and no cybersecurity claim is made.**

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

The projection fields in the Experiment Definition are deterministic synthetic placeholders because G1 has not produced real Integration Result, Scenario Projection Accounting, mapping, or stimulus artifacts.

The synthetic occurrence criterion is deliberately Story-local and does not encode FlatSat STATUS parsing, telemetry sequencing, or any other real runtime rule.

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

## G1-G4

G1, G2, G3, and G4 are not implemented or authorized by this package.
