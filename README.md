# OrbitFabric Reference Mission

**A contract-oriented engineering reference mission for OrbitFabric Core, OrbitFabric Studio and ecosystem integrations.**

[![Reference Mission CI](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/reference-mission-ci.yml/badge.svg)](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/reference-mission-ci.yml)
[![R1 Flight Ground Proof](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/r1-flight-ground-proof.yml/badge.svg)](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/r1-flight-ground-proof.yml)
[![R1 Live Flight Ground Proof](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/r1-live-flight-ground-proof.yml/badge.svg)](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/r1-live-flight-ground-proof.yml)
[![Documentation](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/docs-pages.yml/badge.svg)](https://github.com/OrbitFabric/orbitfabric-reference-mission/actions/workflows/docs-pages.yml)

This repository is the shared public engineering environment around a representative small-spacecraft Mission Data Contract.

It has two complementary purposes:

1. **Reference Mission** - a canonical, synthetic mission model used to exercise OrbitFabric Core and OrbitFabric Studio.
2. **Engineering Stories** - reproducible technical investigations that select a meaningful slice of that mission and test it against real engineering tools, runtimes and integration boundaries.

It is not flight software, not a spacecraft simulator, not a real mission configuration and not a ground segment.

## Start here

- [Published documentation](https://orbitfabric.github.io/orbitfabric-reference-mission/)
- [Reference Mission orientation and reading path](https://orbitfabric.github.io/orbitfabric-reference-mission/00-orientation/00-purpose-and-reading-path/)
- [Reference Mission tutorial](https://orbitfabric.github.io/orbitfabric-reference-mission/02-tutorial/00-tutorial-index/)
- [Engineering Stories](https://orbitfabric.github.io/orbitfabric-reference-mission/engineering-stories/)
- [R1 Story: One Mission Contract Across Flight and Ground](https://orbitfabric.github.io/orbitfabric-reference-mission/engineering-stories/r1-flight-ground/)
- [R1 Technical Deep Dive](https://orbitfabric.github.io/orbitfabric-reference-mission/engineering-stories/r1-flight-ground/technical-deep-dive/)
- [R2 Story: One Intent, Two Executions](https://orbitfabric.github.io/orbitfabric-reference-mission/engineering-stories/r2-pwnsat/)

## Two pillars

```text
OrbitFabric Reference Mission
│
├── Reference Mission
│   ├── Canonical Mission Model
│   ├── Scenarios
│   ├── Generated Core evidence
│   ├── Tutorial
│   └── Studio exploration
│
└── Engineering Stories
    ├── Front Story
    ├── Reproducible Reference Project
    └── Technical Deep Dive when the Story needs one
```

### Reference Mission

The Reference Mission provides one coherent mission context for the OrbitFabric ecosystem.

It models a representative small spacecraft through contract-level concepts such as subsystem topology, operational modes, telemetry, commands, events, faults, payload lifecycle, data products, contact and downlink intent, commandability and autonomy.

OrbitFabric Core remains the semantic authority. The Mission Model is validated and used to generate deterministic evidence and machine-readable inspection surfaces. OrbitFabric Studio consumes Core-owned facts and makes them easier for an engineer to navigate and understand.

The tutorial reconstructs the mission progressively from operational reasoning. The reference overview presents the consolidated current state.

### Engineering Stories

Engineering Stories complement the tutorial rather than replace it.

Each Story starts from a real engineering question, selects a bounded slice of the canonical Reference Mission and exercises that slice against a concrete toolchain, runtime or integration boundary.

Every Engineering Story has a reader-facing Story and an inspectable proof surface. A separate Technical Deep Dive is added only when the mechanics and evidence need their own document:

```text
Front Story
    Why does this matter?
    What problem did we explore?
    What did we learn?

Reference Project
    Can I inspect it?
    Can I run it?
    Can I reproduce the result?

Optional Technical Deep Dive
    How exactly does it work when the Front Story
    should not carry all of the mechanics?
```

R1 uses all three layers. R2 intentionally uses the Front Story plus the Reference Project; its exact schemas, artifacts, harness and evidence machinery live with the executable package rather than in a separate Deep Dive.

## R1 - One Mission Contract Across Flight and Ground

R1 is the first completed Engineering Story.

It asks whether one mission-level semantic root can drive independently owned flight and ground engineering paths without forcing either side to adopt the other's implementation model.

The demonstrated vertical slice uses these canonical OrbitFabric identities:

```text
payload.stop_acquisition
radiation_payload.acquisition_active
```

The proof follows two independent downstream paths:

```text
Canonical Mission Model
        │
        ├── F Prime projection
        │      -> native FPP declarations
        │      -> Story-owned F Prime fixture
        │      -> native F Prime Dictionary
        │      -> OpenC3 F Prime target definitions
        │
        └── Scenario + COSMOS Projection Profile
               -> generated verification procedure and suite

Both paths converge in a real OpenC3 COSMOS <-> F Prime runtime loop.
```

R1 retains explicit Scenario projection accounting rather than weakening the upstream mission contract to match downstream limitations:

```text
8 source atoms
3 projected atoms
5 not_projected atoms
2 executable operations
```

Accepted R1 baselines:

```text
Executable Reference Project
  d66f6068235d425bdc2335d4b0cb09a58e70c1de

Sealed retained evidence
  c90a7c6d44d018006a4f8f0825411e3f27540fc2

Final Story / Deep Dive package
  7ac43c9fd8e891168c3461ffa203f6fe54eff80f
```

R1 is intentionally bounded. It does not claim generic F Prime project generation, full canonical Scenario execution by COSMOS, flight behavior generation from mission expected effects, generic adapter composition or write-once-run-everywhere behavior. The exact claims, non-claims, ownership boundaries and retained evidence are documented in the [Technical Deep Dive](https://orbitfabric.github.io/orbitfabric-reference-mission/engineering-stories/r1-flight-ground/technical-deep-dive/).

## R2 - One Intent, Two Executions

R2 asks a different question: can one unchanged mission intent remain accountable when it is projected into an independently owned runtime and the expected execution multiplicity is kept separate from what runtime evidence can actually support?

The published baseline uses the existing canonical operation `obc.request_health_check`, a Story-local Scenario and PWNSAT/FlatSat as the external target boundary. The projection lineage and complete runtime harness are verified offline.

The evidence boundary is explicit:

```text
G0 / G1                     accepted / closed
runtime harness             verified offline
physical FlatSat execution  NOT RUN
live semantic assessment    NONE
```

- [Read R2: One Intent, Two Executions](https://orbitfabric.github.io/orbitfabric-reference-mission/engineering-stories/r2-pwnsat/)
- [Inspect the R2 Reference Project](https://github.com/OrbitFabric/orbitfabric-reference-mission/tree/main/engineering-stories/02-one-intent-two-executions/reference-project)

R2 is published as an intentionally bounded offline Engineering Story. Physical FlatSat evidence, if later obtained, extends the Story rather than being implied by the current publication.

## Repository layout

```text
.
├── mission/                 # canonical OrbitFabric Mission Model
├── scenarios/               # canonical executable scenarios
├── engineering-stories/     # executable Story reference projects and retained evidence
├── docs/                    # published tutorial, reference and Engineering Story narrative
├── .github/                 # CI, publication and contribution workflows
├── mkdocs.yml               # documentation navigation and rendering
└── requirements-docs.txt
```

Ownership is intentional:

```text
mission/ and scenarios/
    canonical mission semantics and executable scenarios

engineering-stories/*/reference-project/
    Story-specific executable integration fixtures and evidence

docs/
    published narrative, tutorial and technical explanation
```

## Current scenario set

The canonical scenario set currently contains five scenarios:

1. `nominal_payload_acquisition`
2. `eclipse_low_power_payload_suspension`
3. `adcs_degraded_pointing_payload_inhibit`
4. `delayed_sband_downlink_backlog_pending`
5. `payload_stop_acquisition_verification`

The first four form the main Reference Mission tutorial set. `payload_stop_acquisition_verification` is also consumed by Engineering Story R1.

The scenario set is intentionally compact. The priority is semantic consistency and inspectable evidence, not model size.

## Validation

The repository CI validates the canonical mission, runs all five scenarios, regenerates Core inspection surfaces and contract-facing artifacts, and builds the documentation with strict MkDocs validation.

From an environment where the `orbitfabric` CLI is installed, the primary model check is:

```bash
orbitfabric lint mission/
```

To build the documentation locally:

```bash
python -m pip install -r requirements-docs.txt
mkdocs build --strict
mkdocs serve
```

Then open:

```text
http://127.0.0.1:8000/orbitfabric-reference-mission/
```

Generated outputs under `generated/` and the MkDocs `site/` directory should normally remain outside version control unless intentionally retained as controlled evidence or publication assets.

## Architectural boundaries

The repository follows a strict ownership model:

```text
Mission Model defines the source contract.
OrbitFabric Core owns semantic facts and deterministic evidence.
OrbitFabric Studio consumes and renders Core-owned facts.
Engineering Stories exercise bounded mission slices against real downstream systems.
Downstream tools retain their native architecture and authority.
```

The Reference Mission remains representative and synthetic. Public material must not include proprietary, confidential, export-controlled or NDA-protected mission information.

## Contributing

Contributions are welcome when they improve the reference model, deterministic scenarios, documentation, Engineering Stories, CI or ecosystem-facing clarity while preserving the architectural and clean-room boundaries.

Before contributing, read:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)

## Ecosystem role

This repository does not replace OrbitFabric Core, OrbitFabric Studio or downstream engineering systems.

Its role is to provide a shared, inspectable mission context where the ecosystem can be taught, validated and challenged against reproducible engineering questions.

The governing principle is simple:

```text
One canonical mission meaning.
Explicit projection boundaries.
Native downstream ownership.
Reproducible evidence.
```
