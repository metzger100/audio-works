# One research home and concise current documentation

Date: 2026-10-11. The owner rejected the remaining confusing layout and directed completion of the repository cleanup.

## Decision

Consolidate project-level capsule research into `meridian-microphone/lab/research/capsules/`. The project root owns overview, brief and decisions. Laboratory research owns subject findings and sources; executable helpers remain in tools and derived tables in results. Subject hubs state their distinct purposes. Each project with research registers one `research_root`; competing maintained research directories fail the gate.

Keep original reports, datasheets, filenames and bytes. Their register entries retain baseline Git revision, original source path and SHA256 through relocation. Gate checks reject dropped protection, replacement/duplicate identity, altered bytes or execute mode. Original material stays within the established research/history scopes. No new exclusion or file waiver is introduced.

Generate the original-evidence history index directly from that register, including encoded links and hashes. Refresh verifies it alongside the other navigation. Future prompt outputs use the same subject structure and filename rules; mandatory policy paragraphs load from the shared workflow and authoritative policies. Compact the artwork guide while retaining construction dimensions, limits, provenance and rebuilding requirements. Keep earlier validation receipts linked from the current completion report.

## Regression coverage and limits

[Structure fixtures](../../tests/quality/test_structure.py) reproduce competing research roots. [Original fixtures](../../tests/quality/test_originals.py) reject changed identity, bytes, modes, missing protection and duplicate identities. [Git navigation regression](../../tests/project/test_navigation.py) exercises real original relocation and rejects altered staged bytes even when working bytes are restored; rejected commits leave content untouched. Existing [Git gates](../../tests/project/test_hooks.py) continue to cover merges, patches and outgoing branches.

No specification, budget, uncertainty range, candidate identity, parent or qualification rule changes. New source snapshots include the relocated capsule reference files. Original frozen evidence remains unchanged. [Validation](../validation.md) records measured sizes, navigation, tests and private recovery. Independent persistent backup and 89 pre-existing source gaps remain incomplete. Remote publication/settings are outside this local cleanup.
