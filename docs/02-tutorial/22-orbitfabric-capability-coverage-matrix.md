# 22, OrbitFabric Capability Coverage Matrix

Status: consolidated Core coverage review with Studio handoff  
Scope: explicit capability coverage demonstrated by the Reference Mission tutorial

## Purpose

This step answers:

```text
Does the tutorial show what OrbitFabric can really do, and does it distinguish implemented capability from future direction?
```

The tutorial now covers the Core-facing path completely enough to hand the reader into Studio Preview 1 without changing semantic authority.

## Reading rule

This matrix is an engineering coverage review, not a marketing checklist.

Each capability should be described as one of:

- covered strongly;
- covered as a candidate surface;
- covered through current post-v1.1 development;
- demonstrated in Studio Preview 1;
- intentionally deferred;
- out of scope.

## Mission contract and scenario coverage

| OrbitFabric capability | Tutorial coverage | Status | Notes |
|---|---|---|---|
| Mission Model source-of-truth principle | Covered | Strong | Steps 01 through 12 progressively establish the model as authoritative contract. |
| Spacecraft identity | Covered | Strong | Step 02. |
| Subsystem topology | Covered | Strong | Step 03. |
| Operational modes and transitions | Covered | Strong | Step 04. |
| Telemetry contract | Covered | Strong | Step 05. |
| Command contract | Covered | Strong | Step 06. |
| Event contract | Covered | Strong | Step 07. |
| Fault contract | Covered | Strong | Step 08. |
| Payload lifecycle | Covered | Strong | Step 09. |
| Data products and storage intent | Covered | Strong | Step 10. |
| Contact windows and downlink flows | Covered | Strong | Step 11. |
| Commandability and autonomy | Covered | Strong | Step 12. |
| Scenario YAML as executable evidence input | Covered | Strong | Steps 13 through 16 use four executable scenarios. |
| Nominal science acquisition path | Covered | Strong | Step 13. |
| EPS low-power protective behavior | Covered | Strong | Step 14. |
| ADCS degraded-pointing protective behavior | Covered | Strong | Step 15. |
| Delayed downlink backlog behavior | Covered | Strong | Step 16. |

## Core evidence and integration surfaces

| OrbitFabric capability | Tutorial coverage | Status | Notes |
|---|---|---|---|
| Generated Markdown documentation | Covered | Strong | Step 17 treats generated docs as reproducible review artifacts. |
| Lint and validation evidence | Covered | CI-verified Core lint | Step 17 documents lint and validation; repository CI runs the selected Core lint on `mission/`. |
| Simulation JSON reports | Covered | Strong | Step 18 treats JSON as machine-readable evidence. |
| Plain-text scenario logs | Covered | Strong | Step 18 treats logs as human-readable timelines. |
| `model_summary.json` | Covered | Stable v1 surface | Step 17. |
| `entity_index.json` | Covered | Stable v1 surface | Step 17; also a current Studio input. |
| Original `relationship_manifest.json` families | Covered | Stable v1 surface | Step 17. |
| Runtime-facing generated bindings | Covered | Strong | Step 19; clearly separated from flight software. |
| Ground-facing generated artifacts | Covered | Strong | Step 20; clearly separated from a ground segment. |
| `dashboard_summary.json` | Covered | v1.1 candidate | Step 21; Core-owned downstream foundation. |
| `scenario_run_index.json` | Covered | v1.1 candidate | Step 21. |
| Structured simulation expectation accounting | Covered conceptually | v1.1 candidate | Used as machine-readable evidence foundation. |
| `coverage_summary.json` | Covered | v1.1 candidate | Step 21; does not imply a current Studio Coverage UI. |
| `mission_snapshot.json` | Covered | Current post-v1.1 candidate | Step 17; complete loaded Mission Model in a read-only envelope and a current Studio input. |
| Explicit FDIR Relationship Manifest families | Covered | Current post-v1.1 additive development | Step 17 and Step 25; seven explicit relationship families with original v1 meanings unchanged. |

## Studio Preview 1 coverage

The tutorial continues after this matrix with a dedicated Studio block.

| Studio Preview 1 capability | Tutorial coverage | Status | Notes |
|---|---|---|---|
| Open Mission / Core executable configuration | Covered | Preview 1 | Step 23. |
| Reference Mission as real Studio acceptance input | Covered | Preview 1 | Step 23 uses the same mission as the primary engineering acceptance mission. |
| Mission Snapshot hydration | Covered conceptually | Preview 1 | Step 23 explains the Core-owned input boundary. |
| Mission Atlas / Overview | Covered | Preview 1 | Step 24. |
| Entity Explorer and domain filtering | Covered | Preview 1 | Step 24. |
| Entity X-Ray | Covered | Preview 1 | Step 24 uses `eps.low_battery_warning`. |
| Domain-qualified entity identity | Covered | Preview 1 | Step 24 preserves `{ domain, id }`. |
| Provenance-aware inspection | Covered | Preview 1 | Step 24. |
| Relationship Explorer | Covered | Preview 1 | Step 25. |
| Context Path | Covered | Preview 1 | Step 25; user-followed path, not inferred causal chain. |
| Context Map | Covered | Preview 1 | Step 25; only explicit Core-owned relationships. |
| Explicit FDIR context exploration | Covered | Preview 1 | Step 25 uses the Reference Mission low-power protection context. |
| Validation Findings | Covered conceptually | Preview 1 | Step 23 establishes lint as a current Studio input. |
| Operational State Map | Covered | Preview 1 | Step 26. |
| Mode Focus | Covered | Preview 1 | Step 26 uses `PAYLOAD_ACTIVE`. |
| Read-only Mission Model boundary | Covered | Strong | Steps 23 through 27. |
| Core semantic authority | Covered | Strong | Central rule of the whole Studio block. |

## Studio capabilities intentionally deferred

| Capability | Status | Reason |
|---|---|---|
| Data Product Journey | Deferred | Not part of Preview 1. |
| Scenario Catalog | Deferred | Not part of Preview 1. |
| Scenario Replay / Evidence | Deferred | Not part of Preview 1. |
| Experiment Mode | Deferred | Not part of Preview 1. |
| Compare | Deferred | Not part of Preview 1. |
| Coverage UI | Deferred | Core coverage surface exists, but the Studio UI is not part of Preview 1. |
| Generated Output Center | Deferred | Not part of Preview 1. |
| Mission Model editing | Deferred | Preview 1 is read-only. |
| Live telemetry / command uplink | Out of scope | Studio is not mission control. |

## Other intentionally out-of-scope areas

| Capability | Status | Notes |
|---|---|---|
| XTCE export | Out of scope | Requires separate projection/export design. |
| Yamcs integration | Out of scope | Requires separate ecosystem-specific design. |
| OpenC3 integration | Out of scope | Requires separate ecosystem-specific design. |
| CCSDS, PUS, CFDP implementation | Out of scope | OrbitFabric is not a protocol implementation. |
| Flight software runtime | Out of scope | Runtime-facing bindings are contract artifacts, not flight software. |
| Ground segment implementation | Out of scope | Ground-facing outputs are not a live ground segment. |
| Relationship graph inference engine | Out of scope | Relationship Manifest provides explicit records, not hidden inference. |
| Plugin execution in Core | Out of scope | Core does not execute downstream plugins. |
| Formal verification or flight-readiness scoring | Out of scope | Not claimed by the Reference Mission. |

## What the tutorial now demonstrates

The Reference Mission now demonstrates the practical ecosystem thesis:

```text
Define once.
Validate.
Simulate.
Document.
Generate.
Export.
Review.
Explore visually.
Trace every visible fact back to Core-owned semantics.
```

A reader can see one Mission Data Contract reused across:

- progressive engineering reasoning;
- generated documentation;
- validation evidence;
- scenario evidence;
- machine-readable inspection surfaces;
- runtime-facing contract artifacts;
- ground-facing integration artifacts;
- Core candidate downstream surfaces;
- Studio mission-understanding views.

## Compatibility discipline

The tutorial must not flatten the project history.

The correct posture is:

```text
v1.0.0
  stable Mission Data Contract baseline

v1.1.0
  published candidate integration surface consolidation

current post-v1.1 Core development
  candidate Mission Snapshot
  additive explicit FDIR relationship families

Studio v0.15.0-preview.1
  consumes Mission Snapshot, Entity Index, Relationship Manifest and lint JSON
```

This keeps release claims accurate while still documenting the current working ecosystem.

## Reader takeaway

A serious reader should finish the Core-facing part of the tutorial with this understanding:

```text
OrbitFabric Core owns mission semantics and deterministic evidence surfaces.
```

The Studio block then adds:

```text
OrbitFabric Studio makes those Core-owned facts easier for a human to navigate and understand without redefining them.
```

## Modeling rule introduced in this step

The twenty-second rule is:

```text
A tutorial should prove capability coverage explicitly and state release posture and product boundaries with equal clarity.
```

## What comes next

The next step opens this Reference Mission in OrbitFabric Studio Preview 1 and begins the visual mission-understanding workflow.
