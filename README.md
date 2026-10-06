<p align="center">
  <img src="branding/design/m100-readme-banner.svg" alt="M100 / METZGER100 AUDIO WORKS" width="960">
</p>

# M100 Audio Works

Working toward open audio hardware for DIY builders.

[Projects](#projects) · [For builders](#for-builders) · [Current state](CURRENT.md) · [Repository guide](#repository-guide)

M100 Audio Works is an independent audio hardware workshop. The goal is to publish designs for microphones, preamps, amplifiers and loudspeakers that others can build and repair. Current work focuses on condenser-microphone research.

Before releasing a design, we will verify the parts supply and assembly instructions, and test the finished hardware.

## Can I build anything yet?

> **No project has been released yet.** Meridian is still being researched, and no prototype has been selected. See [current state](CURRENT.md) for what remains to be done.

## Projects

| Project | Device | Development focus | Status |
| --- | --- | --- | --- |
| [M100 Meridian](meridian/README.md) | Condenser microphone | Flat K47/P48 research for acoustic recording | Not released |

## For builders

Each released project's README links to its build files. These should include:

- **Circuit and parts:** schematic, editable design files and a BOM with manufacturer part numbers, tested substitutes and dated sourcing notes.
- **Boards and assembly:** Gerbers, drill files and assembly drawings; mechanical drawings and pick-and-place/CPL data where needed.
- **Instructions:** PCB ordering, assembly, setup, calibration, testing, expected measurements and troubleshooting; firmware if required.

See the [build documentation guide](CONTRIBUTING.md#documenting-a-hardware-project) for file locations and ordering boards from services such as JLCPCB. All files should refer to the same hardware revision.

## Engineering principles

Use [documented, obtainable parts](COMPONENTS.md) that work across normal production variation, without hand selection or hidden trimming. Test the actual values, tolerances and substitutes.

Keep failed experiments and unanswered questions in the record. Performance claims need measurements from real hardware. See [QUALITY.md](QUALITY.md) and [PATENTS.md](PATENTS.md) for the detailed requirements.

## Repository guide

| Location | Purpose |
| --- | --- |
| [CURRENT.md](CURRENT.md) | Readiness, blockers and evidence |
| Project directories, e.g. [meridian/](meridian/README.md) | Designs and their build/research documentation |
| [docs/](docs/INDEX.md) | Navigation and [experiment evidence](docs/EVIDENCE.md) |
| [branding/](branding/README.md) | M100 identity and existing artwork |
| [COMPONENTS.md](COMPONENTS.md) / [PATENTS.md](PATENTS.md) | Parts, sourcing and implementation constraints |
| [CONTRIBUTING.md](CONTRIBUTING.md) / [QUALITY.md](QUALITY.md) | Engineering and documentation requirements |

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [QUALITY.md](QUALITY.md) before engineering work. From the repository root:

```sh
python3 tools/project.py context orientation
```

## Licensing

Software and general material use **GPL-3.0-or-later**. Hardware sources and design documentation use **CERN-OHL-S-2.0**. See [LICENSE](LICENSE) for scope and third-party terms.
