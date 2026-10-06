# Contributing and maintaining quality

[Audio Works](README.md) · [Current state](CURRENT.md) · [Quality contract](QUALITY.md) · [Build documentation](#documenting-a-hardware-project)

Contributions should make designs easier to understand, reproduce and maintain. Start with the current state, quality contract and applicable agent instructions. Keep engineering claims tied to evidence and distinguish research from buildable hardware.

For a reading list, run `python3 tools/project.py context <route>` from the repository root. Choose orientation, documentation, branding, device-models, qualification, topology, optimization or reporting. Context counts are character-based estimates, not billed model tokens.

## Documenting a hardware project

Name project folders by family and device, such as `meridian-microphone/` or `meridian-preamp/`. Create a folder when work on that device begins; each project owns its documentation and build files.

A project's README is its builder landing page. Begin with an overview and say whether the project has been released, then describe design goals and known limitations. Link authoritative specifications, decisions and evidence instead of copying them. Separate goals, simulation results, qualified implementations and physical measurements.

As useful material becomes available, add sections in the order a builder needs them: specifications and variants; what you need and BOM; PCB fabrication; assembly; setup/calibration; testing and measurements; troubleshooting; revisions; design documentation and license. Include only sections with useful content. Research projects need no empty build headings or placeholder files.

### Release package

Before releasing a revision, test the hardware and validate its build documentation. A released revision should let another builder choose a variant, obtain parts, order boards, assemble, set up and verify the device. Keep all files matched to that revision and explain incompatible variants or changes.

| Material | What a builder needs |
| --- | --- |
| Design sources | Editable schematic/PCB sources, a readable schematic and relevant mechanical drawings |
| BOM and sourcing | References, quantities, values, manufacturer part numbers, package/footprint, ratings and tolerances; qualified substitutes and dated private small-quantity Germany sourcing/delivered costs |
| PCB fabrication | Gerbers and applicable drill files with a layer map; required board dimensions, stack-up, thickness, copper, finish and tolerances only where the design depends on them |
| Placement and assembly | Assembly drawings, component locations, polarity/orientation, assembly sequence, inspection points and tools; assembly BOM and pick-and-place/CPL data where useful |
| Setup and verification | Safe first-power checks, setup/calibration procedure, test fixtures and instruments, expected measurements with conditions and acceptance limits, and troubleshooting |
| Revision record | Revision identity, supported variants, known limitations, changes and applicable license/third-party notices; firmware and its version only if required |

Follow [COMPONENTS.md](COMPONENTS.md) for actual nominal values, tolerances and substitute requalification. Keep procurement, patent screening and physical qualification separate; the [patent gates](PATENTS.md#implementation-and-release-gates) apply before affected prototype, manufacture or build-publication steps.

### File layout and PCB ordering

Use this convention within a project when real deliverables justify it. Do not create empty directories or move research records to suggest a finished design.

```text
hardware/
├── schematic/
├── pcb/
├── fabrication/
│   ├── gerbers/
│   ├── drill/
│   ├── bom.csv
│   └── cpl.csv
├── mechanical/
└── assembly/
```

`schematic/` and `pcb/` hold editable design sources; `fabrication/` holds revision-matched manufacturing exports. Include drill, mechanical, assembly, BOM and CPL outputs as applicable. Link the authoritative parts BOM from the project README; if a service needs a different assembly-BOM format, derive it from that BOM and identify its source/revision. Explain CPL units, origin, board side and rotation conventions when supplied. Firmware belongs in the project only when needed.

PCB ordering instructions should identify the exact revision/archive to upload to JLCPCB or another service, explain each required setting and allow standard manufacturer choices where electrically and mechanically acceptable. Confirm layer mapping, outlines, drills, dimensions and placement orientation in the manufacturer's preview. Check the assembled-board BOM/CPL against the design and qualified parts. Record export and physical validation; unexplained preferences are not fabrication requirements.

## Local setup

Use Python 3 with the standard library, Git and ripgrep. The commands below run from the repository root. Install the checkout's local commit gate:

```sh
python3 tools/project.py hooks install
python3 tools/project.py check
```

The installer preserves unrelated hook configurations and reports conflicts. Fresh clones and restored checkouts need installation again. Scientific work separately follows the laboratory bootstrap, model acquisition and [contract](meridian-microphone/lab/CONTRACT.md); the repository gate needs no vendor bytes or simulator.

## Complete a change

1. Update current facts/evidence references in `project.json`; record rationale and owner-directed changes in the relevant decision log.
2. Classify new modules, register their navigation and update affected reading routes. Edit source documents rather than generated pages.
3. Run `python3 tools/project.py refresh` and `python3 tools/project.py check`.
4. Run `python3 -m unittest discover -s tests/project` after tooling changes. Engineering edits require the applicable lab verification/evaluation, unchanged thresholds and retained failures.
5. For a new research batch, create a separately dated inventory (`evidence inventory`), verify original evidence, update its index and refresh the private backup. Preserve existing manifests and records.
6. Review the staged change; `check --staged` and the commit hook inspect the index. Report failures, omissions and unknowns explicitly.

The hook does not rewrite/stage files, run simulations or require local waveform archives. A passing repository gate does not establish scientific, sourcing, legal or backup readiness.

Apply the [repository licences](LICENSE) to new project-authored material: GPL-3.0-or-later for software and general material, CERN-OHL-S-2.0 for hardware sources and their design documentation. Retain third-party notices and record origin/redistribution terms before adding external material. Use the applicable SPDX identifier for new source files; preserve frozen snapshots. Licence changes require an owner decision and updated scope/reading routes.

## Private evidence

Read [storage boundaries](meridian-microphone/lab/results/README.md). A clone contains metadata, not all original waveform/vendor bytes. Check them with `python3 tools/project.py evidence verify`. Private backups require idle evaluators:

```sh
python3 tools/project.py evidence backup --destination /owner/chosen/storage
python3 tools/project.py evidence restore --source /path/to/backup-directory --destination /empty/restore-directory
```

Use `--independent` only for owner-designated persistent storage independent of this checkout's device. Temporary/same-device storage cannot establish full preservation. Verify the restored archive before reporting completeness; keep the original backup. Re-running a simulation creates new evidence rather than recovering the original. Commands do not contact suppliers, accept licences or publish data.

The [legacy-source audit](docs/LEGACY-EVIDENCE.md) records original gaps. Capture/restore reports distinguish available-byte integrity from full original-evidence completeness. Default searches include maintained source/proposals; add `--include-generated`, `--include-evidence` or `--include-history` deliberately.
