# Verified native output selections

Status: **ORIGINAL ZIP DIGESTS VERIFIED / RETAINED NATIVE RECORDS**

The first P2 failure, accepted P2 and accepted P3 GitHub Actions artifact archives were downloaded on 2026-10-17. Each complete ZIP archive SHA-256 matched the value recorded by GitHub. The selected text files here are historical native outputs, not new test executions.

| Source ZIP | Artifact ID | Original SHA-256 |
| --- | --- | --- |
| First P2 failure, run [34024060461](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/34024060461) | `9986514078` | `d9030502210a4ce4040a4f31dc8fb35b0df5253a5f0a05192d5f3cc8be67c97b` |
| Accepted P2, run [34027854957](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/34027854957) | `9987664271` | `d6705a63d470e8f8734cff8a33e077d3ad9f5df052cc746fafb21f36a0501ee0` |
| P3 characterization, run [34049249662](https://github.com/OrbitFabric/orbitfabric-eds-cfs-adapter/actions/runs/34049249662) | `9994084984` | `38943507d93180ae15640cf0ae23ab4ae6372a6a973dcaa21198982d817a672a` |

| Retained native file | Source member | Retained SHA-256 |
| --- | --- | --- |
| [Original TopicId failure](p2-original-invalid-topic.log) | First P2: `cfs-runtime.log` selected lines 124-125, 128, 165-169 | `207643c4820e25e44311f78c29b3922977af0017e4151587e6257ab65d6a1b8c` |
| [P2 acceptance](p2-a-acceptance.txt) | Accepted P2: `p2-a-acceptance.txt` | `06643909191411f4b6267400f49c785d385d5801f98340f472bb205c72e0bfb1` |
| [P3 acceptance](p3-acceptance.txt) | P3: `p3-acceptance.txt` | `3e7076d4500065a42352325af430e61e82f7ac5b7fda87396320438fe19fd4e3` |
| [Undefined FC result](p3-unknown-function-code-result.txt) | P3: `unknown-function-code-result.txt` | `f8c968f809a0195913c827ac92c1948fad99a5f898709042076b75a8959bd571` |
| [Causal control](p3-edslib-causal-control.txt) | P3: `edslib-derived-dispatch-control.txt` | `2da25c8b2f8b0123fbba214e3df16d1cf8736fb85238a7b5f32656486e833223` |
| [Range observation](p2-b-valid-range-observation.tsv) | P3: `p2-baseline/p2-b-valid-range-observation.tsv` | `17ec1d45578e9bb554694cbb188ec760d10cd89610504a6ebc7353a38deb4cc7` |

Except for the first P2 excerpt, the retained files above are complete, byte-for-byte copies of the named ZIP members. The first P2 selection contains the original source lines and a curator's provenance header. The complete original archives have not been committed to this repository.

The first P2 runtime log's `1980-` timestamps are **simulated target-clock values**, not historical UTC run dates. The original Actions runs are dated September 2026.

To check all selected native records:

```bash
sha256sum p2-original-invalid-topic.log p2-a-acceptance.txt p3-acceptance.txt p3-unknown-function-code-result.txt p3-edslib-causal-control.txt p2-b-valid-range-observation.tsv
```

See [original job-log excerpts](README.md) for independent source line slices, source job IDs and their separate digest provenance.
