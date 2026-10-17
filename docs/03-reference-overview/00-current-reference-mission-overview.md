# Current Reference Mission Overview

Status: reference overview  
Mission model: `of-rm-1`  
Model version: `0.1.0-reference-skeleton`

## Purpose

This document is a compact overview of the current validated Reference Mission end-state.

It is not the step-by-step tutorial.

The tutorial reconstructs how the mission model is built progressively. This overview describes the complete current model and how it is exercised by the OrbitFabric ecosystem.

## Current mission profile

The Reference Mission models a realistic but simplified 3U CubeSat-style scientific technology demonstrator.

The first payload focus is a NanoSiPM-like radiation/event-counting payload. The mission is fictional, sanitized and anonymized. It derives from realistic small-spacecraft engineering patterns without exposing project-specific material.

## Current model areas

The current mission model includes:

- spacecraft identity;
- subsystem topology;
- operational modes and transitions;
- telemetry contract;
- command contract;
- event definitions;
- fault definitions and recovery concepts;
- packets;
- policies;
- payload lifecycle;
- data products;
- contact and downlink assumptions;
- commandability and autonomy.

## Current operational scenarios

The current canonical scenario set contains five executable scenarios:

| Scenario | Operational role |
|---|---|
| `nominal_payload_acquisition` | Nominal payload acquisition, histogram generation and S-band downlink. |
| `eclipse_low_power_payload_suspension` | EPS low-power warning, degraded-power transition and autonomous payload stop. |
| `adcs_degraded_pointing_payload_inhibit` | ADCS degraded pointing, ADCS-degraded transition and autonomous payload stop. |
| `delayed_sband_downlink_backlog_pending` | Science product remains pending while S-band downlink is not executed. |
| `payload_stop_acquisition_verification` | Stop-acquisition command/telemetry verification slice consumed by Engineering Story R1. |

The first four scenarios form the main tutorial walkthrough set. The fifth is canonical mission evidence used by R1. R2 deliberately keeps its health-check Scenario Story-local under `engineering-stories/`, so the R2 experiment does not modify the canonical top-level Scenario set.

## Core-owned generated surfaces

Generated artifacts are reproducible outputs of the model, not primary source files.

The repository ignores `generated/`, so generated artifacts must either be regenerated locally or intentionally captured later as controlled evidence snapshots.

The current surface families are:

| Surface family | Role | Release posture |
|---|---|---|
| Generated Markdown documentation | Human-reviewable domain documentation. | Reproducible generated output. |
| Simulation JSON reports | Machine-readable scenario evidence. | Core evidence surface. |
| Plain-text scenario logs | Human-readable scenario timelines. | Reproducible generated output. |
| `model_summary.json` | Compact model inventory and domain summary. | Stable v1 surface. |
| `entity_index.json` | Machine-readable catalog of model entities. | Stable v1 surface. |
| `relationship_manifest.json` | Machine-readable relationship records between model entities. | Stable v1 base plus additive current FDIR families. |
| Runtime-facing artifacts | Contract bindings for onboard software integration review. | Generated integration output. |
| Ground-facing artifacts | Dictionaries, manifests and review artifacts for ground-side integration review. | Generated integration output. |
| `dashboard_summary.json` / `scenario_run_index.json` / `coverage_summary.json` | Structured dashboard, indexing and coverage foundations. | v1.1 candidate integration surfaces. |
| `mission_snapshot.json` | Complete loaded Mission Model in a versioned read-only envelope. | Stable Core-owned integration/inspection surface since v1.2.0; format identifier remains `0.1-candidate`. |

## Current FDIR relationship relevance

The Reference Mission contains explicit low-power and degraded-pointing protection logic that is especially useful for downstream navigation.

Core v1.2.0 admitted the following additive stable-compatible FDIR relationship families:

- fault-observed telemetry;
- fault recovery commands;
- fault recovery target modes;
- autonomous action fault triggers;
- autonomous action command sources;
- recovery-intent commands;
- recovery-intent target modes.

These are explicit Core-owned relationships, not inferred graph semantics.

## Studio role today

This Reference Mission is no longer only a future Studio driver.

It is the primary engineering acceptance mission for OrbitFabric Studio 0.15.0 Preview 1.

The current Studio preview consumes:

```text
Mission Snapshot
Entity Index
Relationship Manifest including explicit FDIR additions
lint JSON
```

and provides complementary mission-understanding lenses including:

```text
Mission Atlas
Entity Explorer
Entity X-Ray
Relationship Explorer
Context Path
Context Map
Validation Findings
Operational State Map
Mode Focus
```

The Reference Mission can therefore be used to answer questions such as:

- What exists in the mission contract?
- What exactly is `eps.low_battery_warning` and where does it come from?
- Which telemetry does that fault observe?
- Which command and target mode are explicitly connected to its recovery context?
- Which autonomous action references the fault?
- Which operational transitions are declared from `PAYLOAD_ACTIVE`?
- Which commands and commandability rules are relevant to a selected mode?
- Which validation findings map to exact indexed entities?

The rule remains strict:

```text
Core owns mission semantics.
Studio makes Core-owned facts easier to understand.
```

Studio must not invent Mission Data Contract semantics from UI state, raw YAML scanning or private heuristics.

## Studio Preview 1 boundary

The current preview does not yet include:

- Data Product Journey;
- Scenario Catalog;
- Scenario Replay / Evidence;
- Experiment Mode;
- Compare;
- Coverage UI;
- Generated Output Center;
- Mission Model editing;
- live telemetry or command uplink.

The existence of related Core evidence surfaces does not imply those Studio capabilities are already implemented.

## Reference Mission ecosystem role

The repository now serves five complementary purposes:

```text
progressive Mission Data Contract tutorial
+ executable scenario evidence set
+ Core integration/reference mission
+ Studio engineering acceptance and visual-understanding example
+ Engineering Story source and reproducible pressure-test environment
```

That combination is deliberate.

It allows the same sanitized mission to demonstrate both the semantic contract layer and the downstream human-inspection layer without duplicating mission meaning.
