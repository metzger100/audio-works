# Repository structure validation — 2026-10-10

Local implementation of the [owner-directed decision](decisions/2026-10-09-repository-structure.md). This receipt establishes software/structure evidence; engineering, procurement, patent and physical gates remain held.

| Check | Result |
| --- | --- |
| Shared onboarding | Seven mandatory pages: 40,069 → 14,707 characters (63% smaller). The original six-page registered route measured 31,967 |
| Repository hub | 76,105 → 1,341 characters; bounded subject/child indexes |
| Maintained text | 1,775 text files; zero size violations. Exact UTF-8 character ceiling: 15,000 passes, 15,001 fails; no general file waivers |
| Navigation | Baseline flat index had no reachability gate; now 1,853/1,853 maintained files reachable, zero stale outputs across 356 generated files |
| Device-model reading | 652,579 → 95,194 characters (85% smaller), retaining the complete scientific contract and scoped evidence |
| Scientific data | 77 resolved structured records identical to baseline; all 951 paginated CSV rows retained |
| Original bytes | All 33,620 pre-existing frozen files retain bytes and execute modes; original reports, policies and decisions retain SHA256/Git provenance |
| Fast gate regressions | 12 tests pass, plus pinned Ruff correctness/format checks |
| Git/recovery regressions | 28 tests pass, including all original 24 cases, real commits/merges/patch application/multiple-ref pushes/other outgoing branches |
| Scientific verification | [70 tests pass](../meridian-microphone/lab/results/verification/20261009T201251Z_55f494ca/verification.json); source unchanged true; specification hash retained |
| Selected content | Staged and committed-tree validation pass using a temporary index/object store; working index/refs untouched |
| Hook installation | Commit, merge-commit, applied-patch and push gates installed locally; hooks do not fetch dependencies or change content |
| CI | One `repository-quality` job; private originals and simulator qualification remain local |
| Preservation | Capture `20261009T201844Z_fdef3c9f`: 68,260 available files verified and restored with matching bytes/modes. Independent backup and 89 legacy missing sources remain incomplete |
| Gate runtime | Original gate 1.99 s; expanded working gate 11.63 s; staged 11.27 s; committed 11.45 s. Refresh 3.63 s; repeated refresh changes zero files |

Specification SHA256: `f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd`. No scientific threshold, optimizer budget, candidate identity, original failure or parent relationship changed. Current reports separate findings, conditions, failures, limitations and next work; full originals are in [history](history.md). [Path migrations](config/path-migrations.json) preserve old source-relative record meanings.

The first verification attempt passed its 69 tests but overlapped the end of data restoration; its `source_unchanged: false` record remains preserved and receives no completion credit. A regression now makes verification exit with failure when sources change. Stable 70-test runs remain separate cohorts; the final record linked above covers the final scientific sources.

The source migration initially rewrote 93 ignored private inputs. They were restored from the verified prior capture and compared by hash; subsequent edits are restricted to Git-visible maintained files. YAML partition tests prevent integer-key conversion, parser tests reject malformed/duplicate/cyclic data, and snapshot tests verify transitive include coverage.

All seven required onboarding pages now count toward the shared limit, including contributor instructions. Detailed builder/setup/preservation procedures are scoped documents. The final scientific source comparison matches all 898 files from the stable verification; no scientific source changed after that run. The original restored backup covers all new research evidence; final documentation/tooling edits are retained in a separate private handoff copy.

Preservation verification caught refresh treating source-snapshot indexes as generated navigation. Three new snapshot copies were restored only from bytes matching their recorded hashes. Refresh now excludes originals from deletion, a regression exercises frozen indexes, and the gate verifies required snapshot files/hashes. The final evidence audit reports zero damaged or uninventoried files; only the 89 pre-existing missing source copies remain.

Local hooks are bypassable. Remote settings/publication were not changed. Require `repository-quality` in GitHub branch protection when the owner authorizes those settings. [Git hooks](https://git-scm.com/docs/githooks) define the distinct integration points; selected hygiene patterns come from [CPython](https://github.com/python/cpython/blob/main/.pre-commit-config.yaml) and [Canonical documentation workflows](https://github.com/canonical/documentation-workflows). [GitHub branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) describes the server-side requirement.

A fresh clone can run repository checks after installing pinned dependencies, but cannot reconstruct missing private originals by rerunning simulations. [Storage boundaries](../meridian-microphone/lab/results/README.md) and [legacy gaps](legacy-evidence.md) remain authoritative. The [pre-migration validation receipt](history/2026-10-09/docs/VALIDATION.md) retains its original figures and conditions.
