<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Prerequisite publication checks — 2026-10-11

The owner explicitly authorized committing and pushing the completed work in this chat. This supersedes the earlier local-only state recorded in [scientific validation](2026-10-11-simulation-prerequisites.md). The proposed commit includes the earlier capsule evidence dependencies and the isolated semiconductor/transient controls, extraction fixes, original failures and frozen records.

Staged review found three downloaded ngspice copies that belong outside Git under the existing storage policy. Their exact local files and frozen hashes remain unchanged. The first staged check rejected their absence; the [storage correction](../decisions/2026-10-11-runtime-storage.md) applies that existing boundary to the repository gate and preserves full original-byte verification. The two independent runtime regressions reproduced a missing-source rejection and an optional restore completeness contradiction before the correction. Initial fixture setup errors are recorded in that decision.

All39 Git/recovery regressions pass (67.721s), including both new runtime-storage controls. The refreshed repository audit passes. The full original-byte audit again reports16403 declared waveforms and37153 source snapshots, with the same89 historical gaps as the preserved prior receipt,0 damaged files and0 uninventoried waveforms. Staged and commit/push hook gates inspect the final proposed content. The earlier 109-test scientific verification remains unchanged; the publication storage correction does not alter the simulator, models, fixtures, extraction code, thresholds or budgets.

Original solver logs, copied third-party files and frozen snapshots retain their original whitespace. Generated CSV error cells retain the diagnostic strings. A whole staged whitespace check consequently flags those retained bytes; it does not authorize rewriting them. Maintained authored software remains subject to the pinned correctness/format gate.

Ignored waveforms, vendor archives and downloaded runtimes remain local supporting evidence. GitHub synchronization is verified separately after the authorized push; this precommit record does not attest remote synchronization. The original 89 historical snapshot gaps remain declared separately from repository completeness.
