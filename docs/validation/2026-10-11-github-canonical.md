# GitHub storage-policy validation — 2026-10-11

[Owner decision](../decisions/2026-10-11-github-canonical.md) · [Contributor procedure](../maintaining-repository.md#private-evidence)

GitHub is canonical for the versioned repository. Private capture/restore is optional, and the historical recovery item leaves current status and workflows. Local gates report configured authority separately from remote synchronization. The complete original-evidence audit remains available.

| Measure | Before | After |
| --- | --- | --- |
| Shared mandatory reading | 14,361 characters | 14,823; below 15,000 |
| Largest engineering entry route | 47,572 characters | 48,285; below 50,000 |
| Maintained folders | 167 | 167 |
| Existing protected files | 46,292 | All retain SHA-256 and execute mode; one registered archival move |
| Active recovery prerequisite | Independent private storage and historical source recovery | GitHub authority for committed files; private backups optional |

| Verification | Result |
| --- | --- |
| Completion sequence | Deterministic refresh, audit and working gate pass; no oversized/unreachable maintained files or stale navigation |
| Repository regressions | 36 Git/recovery tests and 23 fast tests pass; pinned lint/format pass |
| Archival integrity | Ledger retains exact bytes and original Git revision/path/hash; report matches the preceding committed bytes |
| New policy regressions | Reject claims that GitHub covers ignored evidence; allow protected archival relocation; reject staged rewrites and new missing snapshots |
| Recovery compatibility | Old ledger layout and optional capture/restore remain tested; available-byte integrity never grants original-evidence completeness |
| Fresh-clone regression | Committed repository passes without private originals; full evidence audit still exposes local omissions; old storage-policy fallback retained |
| Original-evidence audit | 11,971 inventory and 31,166 source declarations checked; zero damaged or uninventoried files; archived omissions remain recorded |
| Scientific scope | No lab code, frozen experiments, thresholds, budgets, model identities or qualification states change |

The absent sources already contain no files to delete. Current recovery reminders are removed; their historical audit/ledger are archived unchanged. Frozen manifests, failures, parents and dated validation outcomes remain intact. Original-evidence completeness is unchanged, and ignored raw/vendor bytes are outside GitHub's coverage.

The initial archival attempt found that the audit report postdated the fixed original baseline. Its exact preceding-commit bytes were retained in protected history; the older ledger retains registered original provenance. The first audit rejected an oversized test file. Storage-policy regressions were moved into their own file, preserving the limit; the final full suite passes. Diagnostic outputs remain private.

The latest scientific evidence remains the [94-test cohort](../../meridian-microphone/lab/results/verification/20261011T133548Z_000612f5/verification.json). This storage-policy change creates no replacement experiment and supplies no new engineering, physical, sourcing or patent qualification.
