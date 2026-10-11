# Contributing

[Start here](docs/start-here.md) · [Current state](CURRENT.md) · [Quality](QUALITY.md)

Run `python3 tools/project.py context <route>` before changes. Tie claims to evidence; distinguish research, qualified implementations and measurements.

## Complete a change

Update `project.json`, decisions and original evidence. Register modules/routes. Run `refresh`, `audit`, `check` and applicable tests; tooling changes also need Git/recovery tests. Review staged content. Preserve failures, identities, parents, hashes and scientific requirements. Inventory/verify new batches. GitHub is canonical for committed files; private capture/restore is optional. [Full procedure](docs/maintaining-repository.md#complete-a-change).

## Local setup

Install [pinned dependencies and all four hooks](docs/maintaining-repository.md#local-setup) in every new/restored checkout. Hooks never download, rewrite or stage.

## Documenting a hardware project

[Build conventions](docs/documenting-hardware.md): revision-matched sources, BOM/sourcing, fabrication, assembly, calibration and measured validation when available.

## Private evidence

[Capture/restore](docs/maintaining-repository.md#private-evidence) · [Licensing](LICENSE). No purchase, contact, payment, licence acceptance or publication is authorized here.
