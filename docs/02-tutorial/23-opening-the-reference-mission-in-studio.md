# 23, Opening the Reference Mission in OrbitFabric Studio

Status: Studio Preview 1 tutorial  
Scope: opening the Reference Mission through the real Core-backed Studio workflow

## Purpose

The previous tutorial steps built the Mission Data Contract, exercised it with scenarios and reviewed the structured evidence emitted by OrbitFabric Core.

This step changes viewpoint without changing authority.

The question is now:

```text
How does an engineer begin exploring this same mission in OrbitFabric Studio?
```

OrbitFabric Studio Preview 1 is a local-first, read-only engineering workbench. It does not replace OrbitFabric Core and it does not create a second interpretation of the Mission Model.

The governing rule remains:

```text
OrbitFabric Core owns the fact.
Studio makes the fact understandable.
```

## Preview baseline used by this tutorial

This Studio block targets:

```text
OrbitFabric Studio 0.15.0 Preview 1
v0.15.0-preview.1
```

Preview 1 is validated against a Core baseline that contains the Mission Snapshot and explicit FDIR Relationship Manifest additions required by the current Studio interaction model.

The Reference Mission is the primary engineering acceptance mission for this preview.

That makes this section different from a generic UI tour: the mission used throughout this tutorial is also a real acceptance input for Studio.

## Before opening the mission

Follow the current OrbitFabric Studio README for host prerequisites, source installation and the validated Core baseline.

The important runtime inputs are:

```text
OrbitFabric Studio source tree
OrbitFabric Core executable
OrbitFabric Reference Mission repository
```

Studio deliberately does not embed or replace Core in this preview.

## Start Studio

From the OrbitFabric Studio source tree:

```bash
npm run tauri:dev
```

On Linux hosts affected by the documented WebKitGTK DMA-BUF rendering issue, use the fallback described by the Studio README.

## Configure the Core executable

In the pre-open launcher, set **OrbitFabric executable** to the validated `orbitfabric` executable.

For example:

```text
/home/user/dev/orbitfabric/.venv/bin/orbitfabric
```

The exact path is host-specific.

What matters is the architectural boundary:

```text
Studio
  -> invokes Core
  -> receives Core-owned structured results
  -> renders those results
```

Studio is not expected to reconstruct mission semantics by parsing the Reference Mission YAML files itself.

## Select the Reference Mission

Studio accepts either:

- the `mission/` directory directly; or
- the repository root containing the conventional `mission/` child directory.

For this repository, selecting the repository root is the most natural tutorial path because the reader can keep the complete Reference Mission workspace as the context.

Core remains authoritative on whether the selected source is a loadable mission.

## What Studio hydrates

The current preview progressively consumes these Core-owned machine-readable surfaces:

```text
Mission Snapshot
Entity Index
Relationship Manifest
lint JSON
```

The Mission Snapshot gives Studio a complete read-only model envelope.

The Entity Index provides domain-qualified entity identity and catalog information.

The Relationship Manifest provides explicit declared relationships, including the current additive FDIR relationship families.

The lint surface provides validation findings.

Studio may normalize, group, label and lay out those facts for presentation. It must not invent missing mission meaning.

## No generated files are written into this repository

Opening the Reference Mission in Studio does not populate a `generated/` directory inside this repository.

Preview 1 writes temporary hydration reports only to Studio-owned operating-system temporary storage.

This preserves the repository policy introduced earlier:

```text
mission/ and scenarios/ are authored source
Core outputs are reproducible evidence
a Studio session is not a source mutation
```

## First visual checkpoint

After the mission opens successfully, the reader should see the mission-level Studio workspace rather than a file browser or raw JSON viewer.

The next step begins the visual exploration with Mission Atlas, then moves from the mission-wide view to individual entities.

## What this step proves

This step proves a narrow but important point:

```text
The same Mission Data Contract used by Core can be opened directly as a read-only engineering workspace in Studio.
```

It does not prove:

- Mission Model editing;
- scenario replay in Studio;
- live telemetry;
- command uplink;
- mission control behavior;
- private Studio semantics.

Those capabilities are not part of Preview 1.

## Modeling rule introduced in this step

The twenty-third rule is:

```text
Opening a mission in Studio must preserve Core as the semantic authority and the Mission Model as read-only source.
```

## What comes next

The next step uses Mission Atlas and Entity X-Ray to move from the mission-wide view to specific contract entities.
