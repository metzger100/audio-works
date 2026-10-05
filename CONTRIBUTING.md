# Contributing and maintaining quality

Start with [CURRENT.md](CURRENT.md), [QUALITY.md](QUALITY.md) and the applicable agent instructions. Run `python3 tools/project.py context <route>`; choose orientation, documentation, branding, device-models, qualification, topology, optimization or reporting. Context counts are character-based estimates, not billed model tokens.

## Local setup

Use Python 3 with the standard library, Git and ripgrep. Install the checkout's local commit gate:

```sh
python3 tools/project.py hooks install
python3 tools/project.py check
```

The installer preserves unrelated hook configurations and reports conflicts. Fresh clones and restored checkouts need installation again. Scientific work separately follows the laboratory bootstrap, model acquisition and [contract](meridian/lab/CONTRACT.md); the repository gate needs no vendor bytes or simulator.

## Complete a change

1. Update current facts/evidence references in `project.json`; record rationale and owner-directed changes in the relevant decision log.
2. Classify new modules, register their navigation and update affected reading routes. Edit source documents rather than generated pages.
3. Run `python3 tools/project.py refresh` and `python3 tools/project.py check`.
4. Run `python3 -m unittest discover -s tests/project` after tooling changes. Engineering edits require the applicable lab verification/evaluation, unchanged thresholds and retained failures.
5. For a new research batch, create a separately dated inventory (`evidence inventory`), verify original evidence, update its index and refresh the private backup. Preserve existing manifests and records.
6. Review the staged change; `check --staged` and the commit hook inspect the index. Report failures, omissions and unknowns explicitly.

The hook does not rewrite/stage files, run simulations or require local waveform archives. A passing repository gate does not establish scientific, sourcing, legal or backup readiness.

## Private evidence

Read [storage boundaries](meridian/lab/results/README.md). A clone contains metadata, not all original waveform/vendor bytes. Check them with `python3 tools/project.py evidence verify`. Private backups require idle evaluators:

```sh
python3 tools/project.py evidence backup --destination /owner/chosen/storage
python3 tools/project.py evidence restore --source /path/to/backup-directory --destination /empty/restore-directory
```

Use `--independent` only for owner-designated persistent storage independent of this checkout's device. Temporary/same-device storage cannot establish full preservation. Verify the restored archive before reporting completeness; keep the original backup. Re-running a simulation creates new evidence rather than recovering the original. Commands do not contact suppliers, accept licences or publish data.

The [legacy-source audit](docs/LEGACY-EVIDENCE.md) records original gaps. Capture/restore reports distinguish available-byte integrity from full original-evidence completeness. Default searches include maintained source/proposals; add `--include-generated`, `--include-evidence` or `--include-history` deliberately.
