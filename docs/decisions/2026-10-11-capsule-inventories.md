<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Nested capsule batch inventories — 2026-10-11

The owner requested finite capsule research, frozen inputs and verification of all new batches. New immutable capsule cohorts place their SHA256 inventory inside each dated batch folder while keeping the established laboratory-relative entry paths. The integrity reader previously inferred the laboratory root from two parent directories; nested inventory declarations consequently resolved to nonexistent duplicated paths.

Resolve the laboratory root from the existing `/lab/results/` boundary instead. Preserve every inventory byte and path, earlier root-level inventories, the historical folder-rename interpretation and all completeness/error checks. This changes path resolution only; no scientific invariant, threshold, exclusion or evidence requirement changes.

The regression `test_nested_batch_inventory_keeps_lab_relative_paths_and_detects_damage` uses a synthetic control batch to verify correct coverage, corruption detection and missing-byte detection. Existing root-level, legacy-rename, recovery and clone tests remain mandatory. This fixture never touches real experiment evidence.

[Research findings](../../meridian-microphone/lab/research/capsules/evidence-envelope-001.md) · [Reader](../../tools/repo_quality/evidence.py) · [Regression](../../tests/project/test_recovery.py).
