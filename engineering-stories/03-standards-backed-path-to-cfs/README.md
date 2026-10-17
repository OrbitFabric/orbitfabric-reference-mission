# R3 - A Standards-Backed Path to cFS

**Public headline:** One Bit, Zero Telemetry, and an Unknown Command That Ran.

This directory contains the repository-side proof and provenance package for the third OrbitFabric Engineering Story.

The readable narrative and Technical Deep Dive are owned by the MkDocs \`docs/engineering-stories/r3-eds-cfs/\` pages. They are not duplicated here.

## Reading path

- [Engineering Story](../../docs/engineering-stories/r3-eds-cfs/index.md)
- [Technical Deep Dive](../../docs/engineering-stories/r3-eds-cfs/technical-deep-dive.md)
- [Reference Project and source pins](reference-project/README.md)
- [Retained evidence with SHA-256 manifest](evidence/README.md)

## What this package proves

The historical product-native investigation exercised CCSDS EDS generation, pinned NASA EdsLib and cFS materialization, and a fixed \`of_demo_app\` runtime.

It preserves three technically distinct observations:

1. A standalone 1-bit target boolean was not byte-aligned for the exercised DDS/IDL writer. Adapter-local \`Boolean8\` fixed this without changing semantic \`bool\`.
2. An initially wrong telemetry TopicId produced an invalid MID. Native telemetry succeeded after correcting the selected mission mapping, with the final public Profile using symbolic mission-owned \`topic_ref\`.
3. An undefined FC127 invoked the typed \`payload.enable\` handler on the pinned EdsLib path. The negative property was falsified. Accepted P3 evidence is **CHARACTERIZATION**, not automatic rejection.

P2-B also showed that projected \`ValidRange\` does not alone guarantee automatic target-runtime range enforcement.

## Why this is not another application fork

The executable implementation and native workflow scripts are already public in [orbitfabric-eds-cfs-adapter](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter). A second \`of_demo_app\` copy would risk diverging from the actual accepted proof.

The Reference Project therefore preserves exact links, commands and independent evidence identification instead of duplicating generated code or repackaging native binaries.

## Scope and non-claims

This is historical host-software evidence, not a new cFS execution. There is no physical flight-hardware run, universal EDS coverage, generic command validation guarantee or determination that the observed EdsLib fallback is an upstream defect.

The retained evidence files are selected excerpts from real original GitHub Actions job logs and are hashed individually. The original full CI artifact archives are not replicated by this package.
