<p align="center">
  <img src="branding/design/m100-readme-banner.svg" alt="M100 / METZGER100 AUDIO WORKS" width="960">
</p>

# M100 Audio Works

Working toward open audio hardware for DIY builders.

[Projects](#projects) · [For builders](#for-builders) · [Current state](CURRENT.md) · [Repository guide](#repository-guide)

M100 Audio Works is an independent audio hardware workshop. We aim to publish designs for microphones, preamps, amplifiers and loudspeakers that people can build and repair. Current work is condenser-microphone research.

Before release, we will check parts sourcing and assembly instructions, and test the hardware.

## Can I build anything yet?

> **No project has been released yet.** Meridian is being researched; no prototype has been selected. [Current state](CURRENT.md) lists the remaining work.

## Projects

| Project | Device | Development focus | Status |
| --- | --- | --- | --- |
| [M100 Meridian](meridian-microphone/README.md) | Condenser microphone | Flat K47/P48 research for acoustic recording | Not released |

## For builders

Released projects should provide:

- **Circuit and parts:** schematic, editable sources, BOM with manufacturer part numbers, tested substitutes and dated sourcing notes.
- **Boards and assembly:** Gerbers, drill files and assembly drawings; mechanical drawings and CPL data where needed.
- **Instructions:** PCB ordering, assembly, setup, calibration, testing, expected measurements and troubleshooting; firmware if required.

[Build documentation](CONTRIBUTING.md#documenting-a-hardware-project) covers file locations and PCB ordering, including JLCPCB. Files must match the hardware revision.

## Engineering principles

Use [documented, obtainable parts](COMPONENTS.md) that work across normal production variation, without hand selection or hidden trimming. Test values, tolerances and substitutes.

Keep failed experiments and unknowns in the record. Performance claims need hardware measurements. See [QUALITY.md](QUALITY.md) and [PATENTS.md](PATENTS.md) for requirements.

## Repository guide

| Location | Purpose |
| --- | --- |
| [CURRENT.md](CURRENT.md) | Readiness, blockers and evidence |
| Projects, e.g. [meridian-microphone/](meridian-microphone/README.md) | Design and build documentation |
| [docs/](docs/INDEX.md) | Navigation and [experiment evidence](docs/EVIDENCE.md) |
| [branding/](branding/README.md) | M100 identity and artwork |
| [COMPONENTS.md](COMPONENTS.md) / [PATENTS.md](PATENTS.md) | Parts, sourcing and patent requirements |
| [CONTRIBUTING.md](CONTRIBUTING.md) / [QUALITY.md](QUALITY.md) | Engineering and documentation |

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [QUALITY.md](QUALITY.md) before engineering work. From the repository root:

```sh
python3 tools/project.py context orientation
```

## Licensing

Software and general material: **GPL-3.0-or-later**. Hardware sources and design documentation: **CERN-OHL-S-2.0**. See [LICENSE](LICENSE) for scope and third-party terms.
