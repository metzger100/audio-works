# Documenting hardware

[Contributing](../CONTRIBUTING.md) · [Quality](../QUALITY.md)

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

Follow [COMPONENTS.md](../COMPONENTS.md) for actual nominal values, tolerances and substitute requalification. Keep procurement, patent screening and physical qualification separate; the [patent gates](../PATENTS.md#implementation-and-release-gates) apply before affected prototype, manufacture or build-publication steps.

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

