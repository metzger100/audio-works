# Meridian research laboratory

Executable analog research for Arienne Audio Flat K47 Cardioid/Omni K47FRB under realistic P48. **Every candidate remains unqualified; no topology, PCB or prototype is selected.** Capsule safety/mechanics/noise, device populations, delivered costs and patent screening remain unresolved.

[Project](../README.md) · [Scientific contract](CONTRACT.md) · [Current state](../../CURRENT.md)

## Start here

From the repository root, use `python3 tools/project.py context <route>` for required reading. The complete contract and relevant specifications/evidence take priority over a short reading route.

```sh
cd meridian-microphone/lab
./run doctor
./run verify
./run evaluate fixture_0001 --samples 16 --seed 34047
```

Exit 2 means unqualified. The ideal infrastructure fixture is ineligible by construction. [Setup](docs/setup.md) explains installation; [circuit interface](docs/circuit-interface.md) explains DUTs and evidence.

## Research map

| Need | Entry |
| --- | --- |
| Formal requirements and uncertainty | [Specification hub](spec/INDEX.md) |
| Parts, supported behavior and failures | [Device findings](research/devices/device-model-validation.md), [latest expansion](research/devices/parts-database-expansion-002.md) |
| Implementations and comparisons | [Architecture findings](research/architectures/architecture-comparison-001.md) |
| Capsules, sources, sourcing and patent holds | [Research hub](research/README.md) |
| Lessons and failed hypotheses | [Research memory](research/memory/INDEX.md) |
| Next authorized task | [Prompt hub](research/prompts/README.md) |
| Immutable runs and private storage | [Evidence storage](results/README.md) |
| Future physical tests | [Measurement handoff](measurement/README.md) |

[Controls](tools/controls/INDEX.md) and [report generators](tools/reporting/INDEX.md) contain executable helpers. Current reports summarize findings; derived tables/plots live in `results/reports/`. No report generator rewrites a maintained findings report or original record.

All 14 families remain in the [register](search/families.yaml). [Components](../../COMPONENTS.md), [patents](../../PATENTS.md), [licences](../../LICENSE) and the [completion sequence](../../CONTRIBUTING.md#complete-a-change) apply.
