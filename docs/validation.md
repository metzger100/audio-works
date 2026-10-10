# Repository validation — 2026-10-11

[Current decision](decisions/2026-10-11-research-consolidation.md) · [Earlier structure/report receipts](validation/2026-10-10-meridian-reports.md) · [Quality contract](../QUALITY.md)

Meridian has one research home: [laboratory research](../meridian-microphone/lab/research/README.md), with capsule, device, architecture, sourcing, patent and memory subjects. The project root contains overview, brief, decisions and the laboratory. No engineering, sourcing, patent or physical readiness is promoted.

| Check | Result |
| --- | --- |
| Research ownership | Project-level research folder removed; one declared root enforced by the shared gate |
| Capsule originals | 13 files relocated; all original bytes, names, baseline Git identities and hashes retained |
| Original protection | 184 identities/hashes unchanged; dropped protection, duplicate/replaced identity, altered bytes/modes rejected |
| Frozen evidence | All 39,200 files from the preceding completion retain hashes; snapshots/failures/parents unchanged |
| Scientific data | 961 resolved maintained JSON/YAML records unchanged; specification/uncertainty/budgets unchanged |
| Navigation | 1,843/1,843 maintained files reachable; 367 fresh generated outputs; zero oversized/unreachable/stale files |
| Original navigation | History pages derive from preservation declarations, with encoded local links and hashes |
| Reading efficiency | Prompts01–05: 37,508 → 25,881 characters (31% smaller); artwork guide: 13,040 → 7,098 (46% smaller) |
| Future outputs | Eight planned report paths use subject directories and valid filenames |
| Shared onboarding | 14,707 characters; hard ceiling remains 15,000 |
| Repository tests | 17 fast and 29 Git/recovery tests pass; pinned lint/format checks pass |
| Scientific verification | [75 tests pass](../meridian-microphone/lab/results/verification/20261010T220036Z_6e3b12f0/verification.json); source unchanged true; all 866 captured sources match current files |
| Working gate | Pass in 11.72s; selected staged content checked again at commit |
| Available-byte integrity | Zero damaged/uninventoried files; new 71-file inventory retains verification waveforms/exports |
| Private recovery | Current available-byte capture and restoration verified; detailed receipts remain private |

The Git regression moves a real protected original, stages changed bytes, restores working bytes and proves that the commit is rejected without altering either state. Existing commit, merge, applied-patch, multi-ref/other-branch push and recovery cases continue to pass. Repeated refresh produces identical outputs.

Specification SHA256 remains `f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd`. The seven additional scientific source files are the relocated original capsule PDFs/checksum text; old source cohorts remain frozen. Mandatory policies and the complete scientific contract still load through shared/scoped authority; repeated prompt text was removed without changing their requirements.

The 89 pre-existing source gaps and independent persistent backup remain incomplete. Local recovery establishes available-byte integrity. All implementations remain unqualified. Remote publication/settings are unchanged; hooks remain bypassable without the required server-side `repository-quality` status check.
