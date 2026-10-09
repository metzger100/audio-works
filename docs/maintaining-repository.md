# Maintaining and preserving the repository

[Contributing](../CONTRIBUTING.md) · [Quality](../QUALITY.md)

## Local setup

Use Python 3.12 or later, Git and ripgrep. Install pinned gate dependencies once; hooks never download them. The commands below run from the repository root. Install the checkout's four local gates:

```sh
python3 -m venv .project-local/quality
.project-local/quality/bin/python -m pip install -r requirements-quality.txt
python3 tools/project.py hooks install
python3 tools/project.py check
```

The installer preserves unrelated hook configurations and reports conflicts. Fresh clones and restored checkouts need installation again. Scientific work separately follows the laboratory bootstrap, model acquisition and [contract](../meridian-microphone/lab/CONTRACT.md); the repository gate needs no vendor bytes or simulator.

## Complete a change

1. Update current facts/evidence references in `project.json`; record rationale and owner-directed changes in the relevant decision log.
2. Classify new modules, register their navigation and update affected reading routes. Edit source documents rather than generated pages.
3. Run `python3 tools/project.py refresh`, `python3 tools/project.py audit`, then `python3 tools/project.py check`.
4. Run `python3 -m unittest discover -s tests/project` after tooling changes. Engineering edits require the applicable lab verification/evaluation, unchanged thresholds and retained failures.
5. For a new research batch, create a separately dated inventory (`evidence inventory`), verify original evidence, update its index and refresh the private backup. Preserve existing manifests and records.
6. Review the staged change; `check --staged` and the commit hook inspect the index. Report failures, omissions and unknowns explicitly.

The four hooks inspect commits, merge commits, applied patches and all outgoing push revisions. They run structural checks, Ruff and fast regression tests. The gate does not rewrite/stage files, run simulations or require local waveform archives. A passing repository gate does not establish scientific, sourcing, legal or backup readiness.

Apply the [repository licences](../LICENSE) to new project-authored material: GPL-3.0-or-later for software and general material, CERN-OHL-S-2.0 for hardware sources and their design documentation. Retain third-party notices and record origin/redistribution terms before adding external material. Use the applicable SPDX identifier for new source files; preserve frozen snapshots. Licence changes require an owner decision and updated scope/reading routes.

## Private evidence

Read [storage boundaries](../meridian-microphone/lab/results/README.md). A clone contains metadata, not all original waveform/vendor bytes. Check them with `python3 tools/project.py evidence verify`. Private backups require idle evaluators:

```sh
python3 tools/project.py evidence backup --destination /owner/chosen/storage
python3 tools/project.py evidence restore --source /path/to/backup-directory --destination /empty/restore-directory
```

Use `--independent` only for owner-designated persistent storage independent of this checkout's device. Temporary/same-device storage cannot establish full preservation. Verify the restored archive before reporting completeness; keep the original backup. Re-running a simulation creates new evidence rather than recovering the original. Commands do not contact suppliers, accept licences or publish data.

The [legacy-source audit](legacy-evidence.md) records original gaps. Capture/restore reports distinguish available-byte integrity from full original-evidence completeness. Default searches include maintained source/proposals; add `--include-generated`, `--include-evidence` or `--include-history` deliberately.

Quality/tooling changes require a [dated decision](decisions/INDEX.md) and a regression fixture reproducing the defect. Use `audit` to identify the next focused improvement; update an authoritative record, fix the cause and repeat the completion sequence. No scheduled jobs or separate issue ledger are needed. Configure the CI job `repository-quality` as a required GitHub status check when remote settings changes are authorized. See [mechanical rules](quality-rules.md).
