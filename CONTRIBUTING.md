# Contributing to OrbitFabric Reference Mission

Thank you for your interest in improving the OrbitFabric Reference Mission.

This repository is a contract-oriented engineering reference mission used to exercise and explain OrbitFabric Core and OrbitFabric Studio. Contributions are welcome when they improve the reference model, deterministic scenarios, documentation or ecosystem-facing clarity while preserving the project's architectural and clean-room boundaries.

## Contribution scope

Useful contributions include:

- corrections or clarifications to the Mission Model;
- improvements to the deterministic scenario set;
- documentation fixes and tutorial improvements;
- better examples of Core-owned semantic relationships;
- improvements to CI, MkDocs or repository maintenance;
- corrections to Studio walkthrough material when current implemented behavior changes.

This repository is not the place to implement new OrbitFabric Core semantics or new Studio product behavior. Changes that require new schema, validation, export or application capabilities should normally be proposed in the corresponding Core or Studio repository first.

## Architectural rules

The Mission Model is the source contract and OrbitFabric Core is the semantic authority.

Contributions must preserve these rules:

1. Keep `mission/` compatible with the real OrbitFabric Core loader and schema.
2. Do not invent YAML fields or relationships that Core does not define.
3. Do not infer mission semantics from identifier names, file layout or scenario co-occurrence.
4. Keep scenarios deterministic and focused on contract-level evidence.
5. Do not describe generated runtime-facing artifacts as flight software.
6. Do not describe generated ground-facing artifacts as a ground segment.
7. Keep Studio documentation traceable to Core-owned facts and implemented Studio behavior.
8. Do not document planned Studio features as if they already existed.
9. Keep the Reference Mission representative and synthetic rather than tied to a real spacecraft program.

## Clean-room requirement

Do not contribute:

- proprietary mission data;
- private spacecraft architecture details;
- private packet or protocol definitions;
- real operational logs or anomaly timelines;
- private bus maps, pinouts or hardware mappings;
- employer-owned or customer-owned code;
- NDA-protected material;
- export-controlled material;
- credentials, tokens or private infrastructure details.

All examples must be synthetic or based only on material that can legally be used and redistributed.

By contributing, you confirm that the contribution is your original work or material you have the legal right to contribute.

## Public engineering artifact boundary

Published repository content must help a reader understand, use, inspect, verify or reproduce the engineering work. This applies to **every Engineering Story** and the Reference Mission tutorial.

Keep source-backed technical investigations, explicit design decisions, verified constraints, negative tests, genuine technical questions, version-pinned evidence and reproducible reference-project assets.

Do not commit prepublication working material: social-media copy, cover-production checklists, temporary approval or sign-off notes, editorial-review tables, authoring plans, chat summaries, transient publishing instructions or release-gate reminders. Such working material belongs outside the public engineering repository.

An unresolved technical limitation is not an editorial TODO. Preserve honest **NOT RUN**, falsified assumptions and pending upstream technical clarifications when they materially qualify the engineering claims.

Before submitting documentation, review the **whole file** for audience relevance. A file's absence from the MkDocs navigation does not make it private.

## Validation

Before opening a pull request, run the relevant checks locally when possible.

Documentation:

```bash
python -m pip install -r requirements-docs.txt
mkdocs build --strict
```

Mission model:

```bash
orbitfabric lint mission/
```

When scenario behavior is affected, run the relevant scenario files under `scenarios/` with the OrbitFabric Core baseline used by repository CI.

The repository CI remains the authoritative integration check and also regenerates the Core inspection surfaces used by the tutorial and Studio acceptance flow.

Generated outputs under `generated/` and the MkDocs `site/` directory should not normally be committed.

## Pull request expectations

A good pull request should state:

- what changed and why;
- whether the Mission Model or scenario behavior changed;
- whether tutorial or Studio-facing documentation changed;
- which validation checks were run;
- any impact on architectural boundaries;
- confirmation that no private, proprietary, export-controlled or NDA-protected material is included.

Prefer focused pull requests. Avoid mixing model changes, editorial cleanup and unrelated repository maintenance when that would make review harder.

## Community and security

Please also read:

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)

Do not report security vulnerabilities or protected mission information in a public issue.
