# Purpose and Reading Path

Status: editorial orientation  
Scope: OrbitFabric Reference Mission documentation structure

## Purpose

This repository is the Reference Mission workspace for OrbitFabric.

Its role is not to provide a static set of YAML files and not to document a mission that is already complete. Its role is to show how a realistic small-spacecraft Mission Data Contract can be introduced progressively, starting from operational reasoning and ending in validated model artifacts, scenario evidence and downstream visual inspection in OrbitFabric Studio.

The intended reader should experience the Reference Mission as a construction and understanding path:

```text
mission need
-> operational scenario
-> subsystem integration problem
-> mission model fragment
-> Core validation
-> generated artifacts
-> scenario evidence
-> Studio exploration
```

## Editorial rule

The validated mission model is the technical end-state. It is not the tutorial order.

The tutorial must be reconstructed from the validated baseline, then presented forward as if the reader were building the mission step by step.

In practice:

```text
validated end-state
-> editorial decomposition
-> step-by-step construction path
-> reader-facing tutorial
-> Studio-based mission understanding
```

## Current reading path

Use this order when reading or extending the documentation:

1. `docs/00-orientation/`, repository purpose and reading path.
2. `docs/02-tutorial/`, progressive tutorial path from mission need through Core evidence and Studio exploration.
3. `docs/03-reference-overview/`, compact view of the current validated model and ecosystem role.
4. `docs/engineering-stories/`, reproducible investigations that take bounded mission slices into real downstream tools and external runtime boundaries.

## What must remain separate

The documentation must keep a strict conceptual separation between:

| Area | Role |
|---|---|
| Tutorial construction steps | Build the mission progressively for the reader. |
| Scenario walkthroughs | Explain why each executable scenario exists and what evidence it exercises. |
| Generated evidence steps | Explain Core-owned outputs and their compatibility boundaries. |
| Studio exploration steps | Show how Studio consumes Core-owned facts to help a human understand the mission. |
| Reference overview | Describe the current validated end-state without pretending to be the construction sequence. |
| Engineering Stories | Pressure-test bounded slices of the validated mission against concrete downstream systems without redefining the canonical mission semantics. |

## Core and Studio boundary

The tutorial must preserve this architectural rule throughout:

```text
Core defines, validates, computes and emits.
Studio consumes, links, organizes and renders.
```

Studio must never be described as a second Mission Data Contract implementation or as the source of mission semantics.
