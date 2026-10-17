# R3 Reference Project - Native proof replay and source index

This is a **reproduction entrypoint to an existing external integration product**, not a new executable cFS project. It consumes no secret assets and adds no custom adapter logic.

## Native source inputs

| Part | Versioned source |
| --- | --- |
| Accepted historical adapter proof | [EDS-cFS adapter v0.1.0](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/releases/tag/v0.1.0) |
| Canonical public adapter source | [v0.1.1](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/releases/tag/v0.1.1) |
| Deterministic generated EDS | [P0/B6 expected.xml](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/blob/v0.1.1/tests/fixtures/p0_b6/expected.xml) |
| Input binding profile | [P0/B3 profile.yaml](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/blob/v0.1.1/tests/fixtures/p0_b3/profile.yaml) |
| Real cFS application | [of_demo_app.c](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/blob/v0.1.1/examples/cfs/of_demo_app/fsw/src/of_demo_app.c) |
| Target reference-project guidance | [Adapter cFS example README](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/blob/v0.1.1/examples/cfs/of_demo_app/README.md) |
| Accepted native coverage | [Integration Coverage](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/blob/v0.1.1/coverage/integration-coverage.md) |

Pinned NASA references are recorded in the [Technical Deep Dive](../../../docs/engineering-stories/r3-eds-cfs/technical-deep-dive.md), including cFS, cFE, EdsLib, ci_lab, to_lab and host tooling.

## Runnable native proof scripts

Run the scripts from the checked-out adapter repository root in an environment satisfying their prerequisites, not from this directory:

```bash
# A historical-equivalent adapter tag/commit should be selected first.
# No script is executed by this Story package.

bash .github/scripts/b10-native-edslib.sh
bash .github/scripts/p1-native-eds-build.sh
bash .github/scripts/p2-runtime-proof.sh
bash .github/scripts/p3-conformance-proof.sh
```

Each script may clone/build pinned NASA components, requires Linux-native dependencies, and writes into disposable job/workspace directories. The P3 script intentionally returns a nonzero exit code for the raw negative probe. The full GitHub Actions workflow has separate follow-on steps for NASA control, disposable EdsLib causal control, postmortem and final characterization acceptance. Running only `p3-conformance-proof.sh` must not be misrepresented as a complete green P3 acceptance.

Inspect [the actual P3 workflow](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/blob/v0.1.1/.github/workflows/p3-conformance-proof.yml) for the complete ordered CI sequence before attempting a fresh reproduction.

## Historical positive and negative observations

| Proof | Source run | Expected interpretation |
| --- | --- | --- |
| First B10 | [33968752308](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/33968752308) | Failure at DDS/IDL writer; not a passing native proof |
| Corrected B10 | [33980808658](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/33980808658) | Successful generation plus deliberately rejected invalid reference |
| P2 runtime | [34027854957](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/34027854957) | Generated command and EDS-decoded `PayloadEnabled=true` |
| P3 characterization | [34049249662](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/34049249662) | Raw FC127 handler invocation, separate causal control, final `CHARACTERIZATION` PASS |

See the [durable selected log excerpts](../evidence/README.md) and exact SHA-256 values for on-repository preservation.

## Native-gate distinctions

```text
P0  Project EDS; exercise native type generation and negative controls
P1  Build a fixed cFS consumer with generated EDS dependencies
P2  Observe typed command dispatch, telemetry and represented range constraints
P3  Observe undefined derived selector, test controls, accept characterization
```

This package deliberately does not copy `of_demo_app`, EdsLib, cFS source, generated EDS internals, or private project artifacts. A successful Story page build is not a substitute for native proof execution.

## Release lineage caveat

The public v0.1.1 release is the present repository/publisher identity. The referenced 2026-09-05 and 2026-09-06 Actions runs remain historical evidence associated with the earlier v0.1.0 product development, which was publicly released on 2026-09-07.

No project run made for this Story is claimed.
