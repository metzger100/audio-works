# Start here

M100 Audio Works currently contains one microphone research project. [Current state](../CURRENT.md) gives the latest blockers; [Meridian](../meridian-microphone/README.md) explains the intended equipment. No build release or selected prototype exists.

| Your task | First useful page | Reading route |
| --- | --- | --- |
| Understand the repository | [Folder map](repository-layout.md) | `orientation` |
| Work on documents or repository tools | [Contributor procedure](maintaining-repository.md) | `documentation` |
| Investigate devices and models | [Device guide](../meridian-microphone/lab/research/devices/README.md) | `device-models` |
| Investigate circuits | [Architecture guide](../meridian-microphone/lab/research/architectures/README.md) | `topology` |
| Check implementation behavior | [Lab commands](../meridian-microphone/lab/docs/setup.md) | `qualification` |
| Explore bounded optimization | [Optimization findings](../meridian-microphone/lab/research/architectures/optimization/robust-optimization-report.md) | `optimization` |
| Reproduce reports | [Report commands](../meridian-microphone/lab/docs/setup.md#reproduce-derived-reports) | `reporting` |
| Edit identity or artwork | [Branding](../branding/README.md) | `branding` |

From the repository root, request the applicable reading list:

```sh
python3 tools/project.py context documentation --format text
```

Read the returned files before changing their subject. Engineering routes retain the complete scientific contract and acceptance specifications; follow [scoped evidence reading](../meridian-microphone/lab/research/reading.md) for additional required originals.

Everyday discovery keeps maintained sources and proposals visible while omitting internal data fragments, generated views and preserved evidence:

```sh
python3 tools/project.py files
python3 tools/project.py search 'startup' --path meridian-microphone/lab/research
python3 tools/project.py search 'leakage' --files-with-matches
```

Use `--include-data-pages` for fragments, `--include-generated` for derived views, `--include-evidence` for evidence and `--include-history` for history. These switches are independent: an evidence data page needs both evidence and data-page switches. `--path` accepts a repository-relative file or directory, with the same visibility filters; absolute paths and traversal are rejected. Search returns 0 for a match, 1 for none and 2 for a search error. JSON remains the default context format.

[Research subjects](../meridian-microphone/lab/research/README.md) answer scientific questions; the [complete index](INDEX.md) exposes every maintained file, including fragments omitted from discovery.

GitHub is canonical for committed files. Original raw/vendor bytes are local supporting evidence; [optional capture and recovery](maintaining-repository.md#private-evidence) can preserve them. A passing repository check establishes organizational/software hygiene; scientific, procurement, patent and measurement claims retain their evidence requirements.
