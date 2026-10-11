# Scoped reading and shallow data pages

Date: 2026-10-11. The owner asked to fix the audit's heavy reading routes, recursive data directories and repeated prose.

## Decision and boundaries

Limit declared entry routes to 50,000 UTF-8 characters, counting shared paths once. This is an owner-directed repository reading budget; additional required scientific evidence has no limit. Retain the complete scientific contract, all five acceptance specifications, project description/decisions and laboratory instructions in every engineering route. Load source groups and detailed role, procurement, patent and experiment records before affected work through one scoped reading table. Only loading directions change; scientific thresholds, uncertainty, evaluation budgets and qualification remain unchanged.

Partition mutable structured data into one flat directory per document. Semantic field/candidate names identify pages; deterministic pagination stays below 12,000 characters. Long names retain a hash of their complete identity. Relative includes still reject escapes/cycles/duplicates and preserve resolved types, precision and order. Replace only prior include-owned pages; never glob-delete unrelated files. Frozen data and original paths stay intact.

Put shared candidate conditions and recurring structural changes in the candidate hub. Each implementation retains its conversion, BOM, count, hypothesis, ancestry, failures and result identity. Initial prompts reference the shared workflow instead of copying its authority. No documentation edit grants qualification or clears an unknown.

## Enforcement and acceptance

The gate rejects entry reading above the budget, repeated rendered prose of 180 characters across maintained authored Markdown, and nested data-partition directories. Generated navigation/derived tables and frozen originals retain their existing roles; no per-file waiver is added. Within-file repetition checks remain.

[Efficiency fixtures](../../tests/quality/test_efficiency.py) exercise exact boundaries, shared-path counting, URL-independent prose and flat/frozen paths. [Partition fixtures](../../tests/quality/test_data.py) verify deep lossless deterministic round trips and recognizable candidate IDs. [Git regressions](../../tests/project/test_navigation.py) reject staged overhead even when working bytes differ. [Reporting regressions](../../meridian-microphone/lab/tests/test_reporting.py) check page replacement, retained unrelated files and original evidence.

[Validation](../validation.md) records before/after route sizes, depth, duplication, resolved-data equality, original hashes, gate runtime and private restoration. The baseline routes were 66,143–78,678 characters, maximum maintained directory depth 12, and authored repetition 14 paragraphs. Storage requirements now follow the [GitHub owner decision](2026-10-11-github-canonical.md). Publication/settings remain outside this cleanup.
