# OrbitFabric Reference Mission

<div class="orbitfabric-lead" markdown>

**A contract-oriented engineering reference mission for OrbitFabric Core and OrbitFabric Studio.**

This site shows how a representative small-spacecraft mission can move from operational intent to a structured Mission Data Contract, deterministic Core evidence and visual engineering understanding in Studio.

</div>

[Start with the reading path](00-orientation/00-purpose-and-reading-path.md){ .md-button .md-button--primary }
[Open the tutorial index](02-tutorial/00-tutorial-index.md){ .md-button }

---

## Choose your entry point

<div class="grid cards" markdown>

-   **Understand the mission and the method**

    Start with the purpose, scope and recommended reading path before entering the progressive model construction.

    [Orientation →](00-orientation/00-purpose-and-reading-path.md)

-   **Follow the complete engineering tutorial**

    Build the contract progressively through mission context, modes, telemetry, commands, events, faults, payloads, data products and commandability.

    [Tutorial index →](02-tutorial/00-tutorial-index.md)

-   **Inspect the current validated mission**

    Jump directly to the consolidated current-state overview when you already understand the tutorial structure and want the final mission picture.

    [Reference overview →](03-reference-overview/00-current-reference-mission-overview.md)

-   **Explore the mission in Studio**

    Follow the real OrbitFabric Studio Preview 1 workflow from mission opening to Entity X-Ray, explicit relationships, FDIR context and operational logic.

    [Studio exploration →](02-tutorial/23-opening-the-reference-mission-in-studio.md)

-   **Pressure-test the contract through Engineering Stories**

    Follow reproducible investigations that take bounded slices of the canonical mission into independently owned flight, ground and external-runtime systems.

    [Engineering Stories →](engineering-stories/index.md)

</div>

## The engineering arc

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

The Reference Mission is intentionally **contract-level**. It is not flight software, not a spacecraft simulator, not an RF simulator, not a ground segment and not mission control.

!!! info "Semantic authority stays in Core"
    The Mission Model defines the source contract. OrbitFabric Core validates, computes and emits authoritative structured facts and evidence. OrbitFabric Studio consumes and renders those facts for human inspection; it does not create a second interpretation of the mission semantics.

## What the reference demonstrates

| Area | Current reference coverage |
|---|---|
| Mission contract | Spacecraft identity, subsystem topology, operational modes, telemetry, commands, events, faults, payloads, data products, contact/downlink intent and commandability/autonomy. |
| Executable evidence | Five deterministic canonical scenarios: four tutorial scenarios plus the R1 stop-acquisition verification scenario. |
| Core inspection surfaces | Model Summary, Mission Snapshot, Entity Index, Relationship Manifest, dashboard/scenario-index/coverage surfaces and explicit FDIR relationship families. |
| Generated integration artifacts | Runtime-facing C++17 contract bindings plus ground-facing dictionaries and review artifacts. |
| Studio Preview 1 | Mission Atlas, Entity Explorer, Entity X-Ray, Relations/Context Map, Validation Findings, Operational State Map and Mode Focus. |
| Engineering Stories | R1 proves a live flight/ground convergence slice; R2 publishes a source-grounded PWNSAT projection and offline runtime-accountability harness with physical FlatSat execution explicitly NOT RUN. |

## Current scenario set

| Scenario | Evidence focus |
|---|---|
| `nominal_payload_acquisition` | Nominal acquisition, histogram generation, S-band downlink and return to nominal. |
| `eclipse_low_power_payload_suspension` | EPS low-power warning, degraded-power posture and autonomous payload stop. |
| `adcs_degraded_pointing_payload_inhibit` | ADCS degraded pointing, ADCS-degraded posture and autonomous payload stop. |
| `delayed_sband_downlink_backlog_pending` | Histogram generated, S-band idle and backlog explicitly pending. |
| `payload_stop_acquisition_verification` | Canonical stop-acquisition command/telemetry verification slice consumed by Engineering Story R1. |

## Release posture represented here

The tutorial distinguishes **historical Core compatibility milestones**, not successive descriptions of the current Core release:

```text
v1.0.0
  Stable Mission Data Contract baseline

v1.1.0
  Candidate dashboard, scenario-run and coverage inspection surfaces

v1.2.0
  Stable Core-owned Mission Snapshot and coherent Core Integration Input Set
  Seven additive stable-compatible FDIR Relationship Manifest families
```

The Mission Snapshot retains the format identifier `0.1-candidate` even though its documented integration/inspection boundary is stable from v1.2.0. Surface format identifiers and stability classifications are distinct. See the [Core v1.2 stability decision](https://github.com/OrbitFabric/orbitfabric/blob/main/docs/reference/v1.2-integration-input-stability-decision.md).

For the currently published Core version, consult [Core Architecture](https://github.com/OrbitFabric/orbitfabric/blob/main/docs/ARCHITECTURE.md). Engineering Stories retain their exact accepted Core source baselines for reproduction.

The Studio section targets **OrbitFabric Studio 0.15.0 Preview 1** and documents only implemented behavior.

## Studio views illustrated

The Studio tutorial illustrates five implemented views using real captures from this Reference Mission:

```text
Mission Atlas
Entity X-Ray for eps.low_battery_warning
low-power FDIR Context Map
Operational State Map
Mode Focus for PAYLOAD_ACTIVE
```

These views illustrate the actual Studio Preview 1 surface and its Core-owned mission facts.

---

This documentation is built with Material for MkDocs. The authored Markdown remains the primary source; the published site is the navigable engineering view of the same repository content.
