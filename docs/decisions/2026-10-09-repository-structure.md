# Repository structure and mechanical quality

Date: 2026-10-09. Owner explicitly requested implementation of the agreed repository-wide plan.

## Decision

Enforce 15,000 characters per maintained text file and reduce shared onboarding from 32,000 to 15,000 characters. Keep SVG/media and hash-protected original evidence/third-party material intact. Replace flat lists with bounded child hubs, shared task entry context and scoped scientific reading. Keep original reports/decisions accessible alongside compact current views.

Use one modular Python gate, native Git hooks for commit/merge-commit/patch application/push, pinned lint/parser dependencies and one repository CI workflow. This replaces the prior local-only restriction by explicit owner direction. Gate content comes from the actual index or outgoing revision. Keep simulations and private originals out of CI.

Turn recurring defects into focused regression fixtures; require quality changes to reference decisions/tests. Use audits at change completion, without scheduled jobs, extra process databases or generic file waivers.

## Baseline and evidence

Baseline Git revision and original file hashes are retained in the original-material register. The previous checker passed with 24 repository tests, despite a 76,105-character index, 31,967-character common entry and a 652,579-character device-model reading route. Those measurements motivated the smaller hubs and stronger rejection tests.

Regression coverage: [data composition](../../tests/quality/test_data.py), [structure](../../tests/quality/test_structure.py), [Git hooks](../../tests/project/test_hooks.py), retained recovery/integrity cases. Actual final counts, runtimes and remaining limits belong in [validation](../validation.md).

Original scientific thresholds, budgets, record identities, failures and snapshot bytes remain protected. No sourcing, patent or physical readiness is promoted. Storage requirements now follow the [GitHub owner decision](2026-10-11-github-canonical.md). Deliver locally; no external publication or remote settings change is authorized by this decision.

## Migration corrections

The first reference rewrite incorrectly included private source inputs. All 93 changed private files were restored from the hash-verified preceding private capture; the remaining captured private originals matched. Subsequent rewrites use Git-visible maintained paths only. Frozen experiment records were excluded throughout. Lossless-data comparison also detected integer YAML keys becoming JSON strings; YAML partitions now retain their original key types. These failures receive regression coverage.

Integrity verification detected three new source-snapshot indexes removed by refresh. Restore used exact recorded SHA256 matches. Original navigation is now excluded from refresh deletion and obsolete-output checks; required source snapshots are checked for presence and matching hashes. [The frozen-index regression](../../tests/project/test_navigation.py) exercises the failure. Verification also fails when its captured sources change during a run; original unstable results remain preserved.

Follow-up, 2026-10-10: validate full filename suffixes and complete directory names. A fixture rejects spaces after the first dot, doubled dots and invalid suffix separators, while allowing ordinary compound file extensions. This closes a naming loophole without adding exceptions.

Shared onboarding now explicitly includes the contributor instructions. Detailed builder/setup/preservation procedures move to scoped documents; the root contributor page retains the completion sequence. Schema-2 registration rejects omission of this required page, and the common-reading regression covers it. Scientific contracts and component/patent policies retain their requirements.

The quality gate also validates the registered decision date and requires that date in the decision text, alongside existing regression references. Invalid/absent dates, mismatched text and missing fixtures fail a focused gate test.
