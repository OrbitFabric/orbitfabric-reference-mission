# R3 selected native evidence provenance

Status: **SELECTED SOURCE EXCERPTS RETAINED / INDEPENDENT NATIVE REPLAY NOT RUN**

These four files are **verbatim, non-contiguous selections** from four historical GitHub Actions job logs, fetched on 2026-10-17 through the connected GitHub repository. They are not complete job logs, do not replace the original archives, and are not newly executed cFS evidence.

The selected source lines include timestamps and full line content. The `# Extract` boundaries and the preamble were added during curation. Exact SHA-256 values below describe the **entire committed excerpt files**, including their preambles and separators, rather than the upstream full job log or ZIP archive.

| Excerpt | Source run / job | Original 1-based log lines | Curated file SHA-256 |
| --- | --- | --- | --- |
| [First B10 failure](b10-original-failure.log) | [33968752308](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/33968752308), job `101313400030` | 988-1006 | `075a8db5e044bc6dcf733815a58ff438809b97efe3bd2143a265881f13e96f55` |
| [Corrected B10 proof](b10-corrected-proof.log) | [33980808658](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/33980808658), job `101345558752` | 989-998, 1004-1015 | `b571ca9d4ae58d0f1e5423e3a01d90019c5a1ebd74fe4b3c5d888adc49ebdec6` |
| [P2 native loop](p2-native-closed-loop.log) | [34027854957](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/34027854957), job `101471923587` | 5676-5686 | `1fbbbda9d83a478c850b7e29360eab29b4c05a6e2be6ca1f3313dff2766555e2` |
| [P3 original probe and characterization](p3-unknown-fc-characterization.log) | [34049249662](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/34049249662), job `101529767431` | 5671-5687, 5701-5716 | `d23431115321a62e5c72459c058ed78043e019d1cb86fd506591405154f2642c` |

## Original archive provenance

The GitHub Actions ZIP artifacts were verified as existing and not expired on 2026-10-17. **They have not been copied wholesale into this Story.** Their reported ZIP digests are different from the excerpt hashes above.

| Proof | Source artifact ID | GitHub-reported ZIP digest | Listed expiry |
| --- | --- | --- | --- |
| corrected P0/B10 | `9973701282` | `sha256:5c21886a80bfb2505fe886314ea95774b530f0ee8dfb24f3cbff9ebc25d61b11` | 2026-12-04 |
| P2 | `9987664271` | `sha256:d6705a63d470e8f8734cff8a33e077d3ad9f5df052cc746fafb21f36a0501ee0` | 2026-12-05 |
| P3 | `9994084984` | `sha256:38943507d93180ae15640cf0ae23ab4ae6372a6a973dcaa21198982d817a672a` | 2026-12-05 |

The original failing B10 run had **no surviving Actions artifact in the queried run listing**, but its job log was accessible for direct extraction at the time of this preparation.

## Interpretation rules

- The first B10 excerpt establishes the original native IDL-writer assertion, not the field-width root cause in isolation. Cross-check the byte-width cause against the source implementation and the corrected `Boolean8` EDS type.
- The corrected B10 excerpt includes an *intentional invalid-reference negative control*. A negative-control error printed inside a successful workflow is not a regression.
- P2 native log verifies a real typed command, OF_DEMO runtime dispatch and EDS-decoded `PayloadEnabled=true`. It does not independently display the *earlier* TopicId 161 failure, for which the historical investigation remains the source of chronology.
- P3 log **does** display `Process completed with exit code 1` in the deliberate raw negative-conformance probe. Its *whole workflow* can nevertheless complete successfully after the causal controls and the `CHARACTERIZATION` acceptance. See the explicitly reviewed [P3 acceptance implementation](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/blob/v0.1.0/.github/scripts/p3-acceptance.sh).
- Historical runtime evidence is attributable to the v0.1.0 lane. v0.1.1 is the later canonical source identity and is not the source of those 2026-09-05/06 run IDs.
- No real spacecraft flight hardware was involved; do not generalize the frozen SampleMission behavior to every EdsLib/cFS deployment.

## Verification command

From this directory, after checkout:

```bash
sha256sum b10-original-failure.log b10-corrected-proof.log p2-native-closed-loop.log p3-unknown-fc-characterization.log
```

Compare the four computed digests with the table. If any file is edited or reformatted, update this manifest and reverify before the public merge.

This selection preserves critical publicly inspectable output without treating ephemeral CI archive URLs as the sole surviving record. The original scripts, input EDS fixture and fixed target application remain version-pinned in the upstream adapter repository.
