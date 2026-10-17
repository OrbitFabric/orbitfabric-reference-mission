## Summary

Describe the purpose of this pull request.

## Changes

List the concrete changes introduced by this PR.

- 
- 
- 

## Affected Area

Select all that apply:

- [ ] Mission Model
- [ ] Scenarios
- [ ] Core validation / generated evidence
- [ ] Tutorial / documentation
- [ ] Studio walkthrough
- [ ] CI / tooling
- [ ] Repository maintenance
- [ ] Other

## Mission Contract Impact

Does this PR change the Reference Mission contract or scenario behavior?

- [ ] No
- [ ] Yes

If yes, describe the impact clearly and note whether the change requires any corresponding OrbitFabric Core capability.

## Architectural Boundary

For non-trivial changes, state what this PR intentionally does **not** implement or redefine.

Examples:

- new OrbitFabric Core semantics
- flight runtime behavior
- ground segment behavior
- real spacecraft configuration
- private mission-specific behavior
- future Studio capabilities that are not implemented

## Clean-Room Confirmation

By opening this PR, I confirm that this contribution does not include proprietary, confidential, export-controlled or NDA-protected material, including private mission data, spacecraft architecture, packet formats, operational logs, customer-owned code or credentials.

- [ ] Confirmed

## Public Artifact Hygiene

- [ ] No prepublication working documents, social post drafts, editorial approvals, release-gate notes or temporary publication checklists are committed.
- [ ] New Engineering Story files serve readers, source inspection or reproducibility; technical limitations and original evidence are retained.

## Validation

Select the checks that were run as relevant.

- [ ] `orbitfabric lint mission/`
- [ ] affected scenarios executed successfully
- [ ] `mkdocs build --strict`
- [ ] repository CI is green
- [ ] documentation reviewed for Core/Studio boundary accuracy

If some checks were not run, explain why.

## Generated Artifacts

- [ ] This PR does not commit generated artifacts.
- [ ] This PR intentionally updates controlled generated artifacts or publication assets.

If generated artifacts are committed, explain why.

## Notes for Review

Add anything the reviewer should pay particular attention to.
