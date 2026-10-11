# Pre-existing source-snapshot gaps

Audit: 2026-10-05, baseline revision `f740735ef03bc6f43240f037e5d59ec2324773e1`.

The original laboratory documentation states that early debugging runs predate full source snapshots. Their manifests identify source versions, but **89 declared source files (32 unique SHA-256 values) are absent** from five early experiment snapshot directories. A search of retained Git source blobs found no byte-identical recovery candidates. All 3,902 inventoried waveforms/exports exist and match their hashes; the surviving source snapshots also match. Original metadata and failed experiments are unchanged.

[Exact missing paths and expected hashes](legacy-source-gaps.json) retain the dated observation. Do not manufacture replacement snapshots from current code, rerun experiments as recovery, or remove the declarations to obtain a passing score. Exact bytes from an independently retained original source may be restored with dated provenance and hash verification.

The project folder became `meridian-microphone/` on 2026-10-06. The ledger retains its original `meridian/` paths and hashes; backup checks map those paths to the renamed folder. Earlier backups restore their original layout.

Private capture may protect all **available** evidence despite these known gaps. Its manifest records the missing declarations; restore verification proves the captured bytes, not the existence of missing originals. Full original-evidence preservation remains incomplete while the gaps remain. New or changed gaps are not silently accepted. An independent backup and restoration are separate remaining requirements.
