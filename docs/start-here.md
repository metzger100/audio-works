# Start here

M100 Audio Works currently contains one microphone research project. [Current state](../CURRENT.md) gives the latest blockers; [Meridian](../meridian-microphone/README.md) explains the intended equipment. No build release or selected prototype exists.

| Your task | First useful page | Reading route |
| --- | --- | --- |
| Understand the repository | [Folder map](repository-layout.md) | `orientation` |
| Work on documents or repository tools | [Contributor procedure](maintaining-repository.md) | `documentation` |
| Investigate devices and models | [Device findings](../meridian-microphone/lab/research/devices/device-model-validation.md) | `device-models` |
| Investigate circuits | [Architecture findings](../meridian-microphone/lab/research/architectures/architecture-comparison-001.md) | `topology` |
| Check implementation behavior | [Lab commands](../meridian-microphone/lab/docs/setup.md) | `qualification` |
| Explore bounded optimization | [Optimization findings](../meridian-microphone/lab/research/architectures/optimization/robust-optimization-report.md) | `optimization` |
| Reproduce reports | [Report commands](../meridian-microphone/lab/docs/setup.md#reproduce-derived-reports) | `reporting` |
| Edit identity or artwork | [Branding](../branding/README.md) | `branding` |

From the repository root, request the applicable reading list:

```sh
python3 tools/project.py context documentation
```

Read the returned files before changing their subject. Engineering routes retain the complete scientific contract and acceptance specifications; follow [scoped evidence reading](../meridian-microphone/lab/research/reading.md) for additional required originals.

For everyday discovery, the repository tools omit generated pages and preserved evidence unless requested:

```sh
python3 tools/project.py files
python3 tools/project.py search 'startup'
```

Use the command's `--include-generated`, `--include-evidence` or `--include-history` switch when you need those records. [Research subjects](../meridian-microphone/lab/research/README.md) answer scientific questions; the [complete index](INDEX.md) exposes individual files.

GitHub is canonical for committed files. Original raw/vendor bytes are local supporting evidence; [optional capture and recovery](maintaining-repository.md#private-evidence) can preserve them. A passing repository check establishes organizational/software hygiene; scientific, procurement, patent and measurement claims retain their evidence requirements.
