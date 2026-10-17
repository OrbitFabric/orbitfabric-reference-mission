# Reference Mission Tutorial Index

Status: consolidated tutorial map  
Scope: progressive construction path, Core evidence coverage, Studio exploration and current reading guide

## Purpose

This area contains the reader-facing Reference Mission tutorial.

The tutorial does not start from the complete YAML model.

It starts from operational need, then progressively introduces the model entities required to make that behavior explicit, validatable and evidence-producing. After the Core-facing engineering arc is complete, the tutorial uses OrbitFabric Studio Preview 1 to show how the same Core-owned facts become easier for a human to explore.

The editorial rule remains:

```text
operational behavior first, YAML second
```

The validated mission model is the technical end-state. It is not the tutorial order.

## Current reading path

The current tutorial is organized in six blocks:

```text
mission context
-> mission contract construction
-> executable scenario walkthroughs
-> generated evidence surfaces
-> capability coverage review
-> Studio mission exploration
```

Studio appears only after the Core evidence story is established. That order preserves the architectural boundary:

```text
Core defines, validates, computes and emits.
Studio consumes, links, organizes and renders.
```

## Block 1, mission context

| Step | Document | Role |
|---|---|---|
| 01 | `01-mission-context-and-need.md` | Explains the mission need and why a mission data contract is useful. |
| 02 | `02-spacecraft-identity.md` | Introduces the spacecraft identity as the root of the contract. |

## Block 2, mission contract construction

| Step | Document | Role |
|---|---|---|
| 03 | `03-subsystem-topology.md` | Introduces subsystem participants. |
| 04 | `04-operational-modes.md` | Introduces spacecraft posture and mode transitions. |
| 05 | `05-telemetry-contract.md` | Introduces telemetry as observable evidence. |
| 06 | `06-command-contract.md` | Introduces commands as requested behavior and expected evidence. |
| 07 | `07-event-contract.md` | Introduces events as operational milestones. |
| 08 | `08-fault-contract.md` | Introduces faults as observable conditions linked to recovery intent. |
| 09 | `09-payload-lifecycle.md` | Introduces payload lifecycle as mission-level science activity. |
| 10 | `10-data-products-and-storage.md` | Introduces mission outputs, storage intent and downlink intent. |
| 11 | `11-contact-and-downlink-assumptions.md` | Introduces contact assumptions and downlink flow eligibility. |
| 12 | `12-commandability-and-autonomy.md` | Introduces command sources, commandability rules and autonomous dispatch. |

## Block 3, executable scenario walkthroughs

| Step | Document | Evidence focus |
|---|---|---|
| 13 | `13-nominal-payload-acquisition-scenario.md` | Nominal acquisition, histogram generation, S-band downlink and return to nominal. |
| 14 | `14-low-power-payload-suspension-scenario.md` | EPS low-power warning, degraded-power posture and autonomous payload stop. |
| 15 | `15-adcs-degraded-payload-inhibit-scenario.md` | ADCS degraded pointing, ADCS-degraded posture and autonomous payload stop. |
| 16 | `16-delayed-downlink-backlog-scenario.md` | Histogram generated, S-band idle and backlog explicitly pending. |

## Block 4, generated evidence surfaces

| Step | Document | Role |
|---|---|---|
| 17 | `17-generated-artifacts.md` | Explains generated documentation, machine-readable reports, runtime-facing outputs, ground-facing outputs and local artifact policy. |
| 18 | `18-scenario-evidence.md` | Explains how to read simulation JSON reports and logs as engineering evidence. |
| 19 | `19-runtime-facing-contract-bindings.md` | Explains generated C++17 runtime-facing contract bindings without presenting them as flight software. |
| 20 | `20-ground-facing-integration-artifacts.md` | Explains generated ground-facing dictionaries and review artifacts without presenting them as a ground segment. |
| 21 | `21-dashboard-and-coverage-foundation.md` | Explains dashboard, scenario-run index and coverage summary as Core-owned downstream foundations, distinct from the surfaces consumed by Studio Preview 1. |

## Block 5, capability coverage review

| Step | Document | Role |
|---|---|---|
| 22 | `22-orbitfabric-capability-coverage-matrix.md` | Reviews which OrbitFabric Core capabilities the tutorial demonstrates and establishes the boundary before Studio. |

## Block 6, exploring the mission with OrbitFabric Studio

| Step | Document | Role |
|---|---|---|
| 23 | `23-opening-the-reference-mission-in-studio.md` | Opens the real Reference Mission through the Core-backed Studio Preview 1 workflow. |
| 24 | `24-mission-atlas-and-entity-xray.md` | Moves from mission-wide orientation to exact domain-qualified entity inspection and provenance. |
| 25 | `25-following-relationships-and-fdir-context.md` | Uses Relationship Explorer, Context Path and Context Map to follow explicit low-power FDIR context. |
| 26 | `26-understanding-operational-logic.md` | Uses Operational State Map and Mode Focus to inspect declared transitions, commands, commandability and recovery context. |
| 27 | `27-core-and-studio-one-engineering-workflow.md` | Closes the tutorial as one coherent Core + Studio engineering workflow. |

## Current strategic position

The tutorial now covers a complete ecosystem-facing demonstration arc:

```text
mission need
-> model construction
-> scenario behavior
-> generated evidence
-> runtime-facing contract bindings
-> ground-facing integration artifacts
-> Core-owned structured surfaces
-> capability coverage review
-> Studio mission understanding
```

Studio is intentionally last.

It is a consumer and renderer of Core-owned mission facts, not the place where Mission Data Contract semantics are invented.

## Core compatibility milestones

This tutorial distinguishes when relevant Core surfaces entered the product, rather than treating an older development checkpoint as the present Core release:

```text
v1.0.0  stable Mission Data Contract
v1.1.0  candidate dashboard / scenario-run / coverage surfaces
v1.2.0  stable Mission Snapshot and coherent Core Integration Input Set
         seven additive stable-compatible FDIR relationship families
```

The Mission Snapshot format identifier remains `0.1-candidate` by design; that identifier does not reverse its stable v1.2.0 classification. See the [Core v1.2 stability decision](https://github.com/OrbitFabric/orbitfabric/blob/main/docs/reference/v1.2-integration-input-stability-decision.md).

These surfaces are important to Studio Preview 1, which consumes Mission Snapshot, Entity Index, Relationship Manifest and lint JSON. They must not be retroactively attributed to the v1.0 or v1.1 release scope. The current Core release is documented in [Core Architecture](https://github.com/OrbitFabric/orbitfabric/blob/main/docs/ARCHITECTURE.md).

## Editorial review status

| Block | Status | Notes |
|---|---|---|
| Block 1, mission context | Reviewed | Operational need first, spacecraft identity second. |
| Block 2, mission contract construction | Reviewed | Steps 03 through 12 form a consistent model-construction arc grounded in `mission/`. |
| Block 3, executable scenario walkthroughs | Reviewed | Nominal path, two protective degraded paths and one delayed-backlog path. |
| Block 4, generated evidence surfaces | Reviewed | Core evidence surfaces and current release-posture wording are aligned. |
| Block 5, capability coverage review | Reviewed | Matrix covers current Core and Studio Preview 1 boundaries. |
| Block 6, Studio mission exploration | Reviewed and illustrated | Steps 23 through 27 document only the implemented Preview 1 interaction model using real Reference Mission captures. |

Technical validation remains tied to the model, scenarios and Core-generated evidence.

Studio screenshots are publication assets and do not replace technical validation.

## Studio Preview 1 boundary

The Studio block intentionally does not document capabilities that are deferred beyond Preview 1:

- Data Product Journey;
- Scenario Catalog;
- Scenario Replay / Evidence;
- Experiment Mode;
- Compare;
- Coverage UI;
- Generated Output Center;
- Mission Model editing;
- live telemetry or command uplink.

The tutorial may evolve when those capabilities become real and stable enough to describe accurately.

## Screenshot publication set

The published Studio block uses five real application screenshots:

```text
docs/assets/studio/01-mission-atlas.png
docs/assets/studio/02-entity-xray-low-battery-warning.png
docs/assets/studio/03-fdir-context-map.png
docs/assets/studio/04-operational-state-map.png
docs/assets/studio/05-mode-focus-payload-active.png
```

A separate mission-open screenshot was intentionally dropped because it duplicated the Mission Atlas surface without adding engineering information.

The figures are selected and cropped for editorial clarity rather than requiring every publication image to be a full-surface capture.

## Review checklist

Before publishing, review the current content against these questions:

- Does each construction step introduce one clear operational concept?
- Does each step remain grounded in real files under `mission/` or `scenarios/`?
- Does the tutorial preserve the separation between source model and generated artifacts?
- Do the scenario walkthroughs explain causality, not just sequence?
- Are degraded scenarios presented as expected protective behavior, not as failures?
- Are runtime-facing outputs clearly separated from flight software?
- Are ground-facing outputs clearly separated from a ground segment?
- Are Core candidate surfaces labelled with the correct release posture?
- Does Studio consume only Core-owned facts rather than reconstructing semantics?
- Do Studio chapters stay within the real Preview 1 feature set?
- Can every relationship shown in Studio be traced to an explicit Core-owned relationship record?
- Are screenshots captured from the real Reference Mission on the documented Preview 1 path?

## Per-step authoring template

Each future tutorial step should answer the same engineering questions:

```text
What operational problem are we introducing?
Why does it belong in the mission model or downstream inspection workflow?
Which source files or Core surfaces does it depend on?
Which scenario, generated evidence or Studio lens exercises it?
What evidence confirms it?
What is deliberately out of scope?
```

## Current rule

The tutorial is published through Studio Preview 1 and remains structurally complete for that documented baseline.

Future changes should revalidate links, Core surface classifications, exact example baselines and any newly published Studio behavior without expanding the tutorial speculatively.
