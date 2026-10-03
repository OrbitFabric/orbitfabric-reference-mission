# R2 bounded runtime proof harness

This directory is the Story-local runtime boundary authorized by Architecture Lab Decision 029.

The harness is intentionally split into an offline-verifiable layer and a live boundary. Offline CI never opens a serial port and never produces runtime evidence.

## Frozen input

The accepted G1 raw SPP stimulus remains unchanged:

```text
db676bb1c080b87cc0bab375f5d2a170a57c4ff2134d41edc31bf37278f8813e
```

USB transport framing is applied only at the runtime boundary. The raw SPP bytes are verified before framing.

## Pinned transport source

`pwnsat-runtime-transport-source-baseline.json` records the exact source facts consumed from:

```text
Pwnsat/FlatSat
b5ac0f2ba5e7bd60fbb6994f681c28053777628e
```

The wired path is asymmetric:

```text
host -> FlatSat:
AA 55 + uint16_be(raw_spp_len) + raw_spp

FlatSat -> host:
AA + raw_spp
```

On receive, raw SPP boundaries are recovered from the SPP primary-header length field, matching the existing repository parser model.

## STATUS evidence

The harness accepts only telemetry APID `0x0C` with the pinned STATUS payload layout.

For an accepted occurrence it retains and uses:

- exact raw SPP evidence identity;
- native TM sequence count;
- STATUS uptime seconds;
- exact presentation and execution-attempt binding.

A STATUS packet by itself is not sufficient.

The frozen criterion is:

```text
occurrence-criterion-0.1-story.json
id      r2.pwnsat.status-occurrence
version 0.1-story
```

Ambiguous attribution yields `INCONCLUSIVE`.

## Story-local runtime contracts

Runtime work uses additive Story-owned forms:

```text
schemas/pwnsat-experiment-definition-0.2-story.schema.json
schemas/pwnsat-execution-observation-0.2-story.schema.json
```

Accepted G0 `0.1-story` schemas and synthetic fixtures are not modified or reinterpreted.

## Offline preflight

Run:

```bash
./engineering-stories/02-one-intent-two-executions/reference-project/run_runtime_offline.sh
```

Offline preflight verifies the complete accepted G1 identity chain, the pinned runtime transport baseline and the frozen occurrence criterion. It generates a temporary `0.2-story` Experiment Definition plus a `NOT_RUN` observation report containing no presentations and no execution occurrences.

## Live boundary

Live code requires an explicit serial port and the Decision 029 control assumptions. It never auto-probes by transmitting a command.

Before any presentation, the caller must establish:

- explicitly authorized and controlled FlatSat;
- wired local USB CDC path;
- exclusive command-source control;
- cleared/quiescent observation channel;
- exact frozen stimulus identity;
- exact execution-attempt provenance.

No live presentation is performed by repository CI.

The live boundary has one additional Python dependency:

```text
pyserial==3.5
```

CI installs that exact version and initializes an unopened `serial.Serial(port=None)`
object to verify the live software dependency without opening, probing, or
enumerating any hardware port.

## Full-phase orchestration and bundle verification

The same Story-local implementation also contains an explicit live orchestration layer in `scripts/runtime_phase.py`.

The live entry point is fail-closed:

- it requires an explicit serial port;
- it requires explicit controlled-runtime and exclusive-command-source assertions;
- it does not auto-probe by transmitting a command;
- it refuses to run unless live execution is explicitly requested;
- repository CI never invokes the live entry point.

The orchestration path is:

```text
quiesce observation path
  -> P1 exact frozen stimulus
  -> retain raw USB stream + raw SPP packets
  -> evaluate E1
  -> only if E1 is independently acceptable:
       quiesce again
       -> P2 same A / same frozen stimulus
       -> retain raw USB stream + raw SPP packets
       -> evaluate E2 or no accepted E2
  -> deterministic semantic assessment
  -> runtime trace
  -> Evidence Set sealing
  -> offline bundle verification
```

The bundle verifier uses the existing generic Core Evidence Set Manifest contract from the same accepted Core 1.3.0 lineage already consumed by G1. No new Core semantics are introduced.

Offline tests exercise the full phase using an in-memory serial double, including:

- `P1 -> E1`, `P2 -> E2` -> `DIVERGED`;
- `P1 -> E1`, `P2 -> no accepted E2` -> `CONFORMANT`;
- ambiguous P1 STATUS attribution -> `INCONCLUSIVE` and no P2 presentation;
- failed control preconditions -> `INVALID_RUN` with zero writes;
- exact Evidence Set integrity;
- deterministic clean repeat of the synthetic transport run;
- verifier rejection after retained raw evidence mutation.

These are harness falsification tests only. They are not FlatSat runtime evidence.
