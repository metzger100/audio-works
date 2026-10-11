<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Manufacturer and simulator source review — 2026-10-11

[Main findings](simulation-prerequisites-001.md) · [Exact file comparisons](simulation-prerequisites-sources-001.json) · [Query ledger](simulation-prerequisites-queries-001.json).

## Manufacturer research and simulator baseline

The [TI product page](https://www.ti.com/product/JFE150) and public archives were researched rather than assuming discovery identifiers designate the same current file. The first sandbox retrieval failed; its unique receipt parent is retained. A second retrieval acquired9 documents, retaining the Nexperia model-guide HTML response as a failed document. No proprietary software or licence was installed/accepted.

| Archive / member result | Relationship and reproducibility limit |
| --- | --- |
| SLPM366 generic Final1.2 / SLPM349I PSpice Final1.2 | Current archive hashes and JFE datasheet match the earlier acquired originals. Wrapper/pin/clamp definitions differ; keyed NJFE150/DJFE150/ESD_SW nominal core parameters agree |
| SLPM350B TINA `.lib` member001 | SHA256 `afe3d619…` is byte-identical to the generic model. Tested as that literal member in ngspice, not as a TINA backend result |
| SLPM358 transient reference `JFE150_ALL.LIB` member039 | Earlier VCC/VEE names and repeated clamp definitions; same keyed nominal core. A whole-file token-list comparison initially treated repetition as inequality; corrected metadata retains the first frozen ledger as parent |
| SLPM349I reference decks | Generated `.cir` depends on absent external `.net` and Windows libraries. Retained `.out.1` itself reports floating `SOURCE_NOISE`; not a successful reference reproduction |
| SLPM351B reference / TINA `.TSC` | Binary reference retained; no TINA backend available. No exact reference execution claimed |

The ledger contains full archive/member hashes, original notices, response metadata, comparison fields and limits. Identical cores constitute one numerical hypothesis, not independent extractions or cross-backend validation. Weak/strong files are existing complete coupled hypotheses; their guaranteed-limit failures stay visible. No joint process distribution or measured population follows.

Installed baseline: ngspice47, KLU build19August2026, Python3.12.14, NumPy2.4.2, SciPy1.17.1. Frozen binary and wrapper hashes are in every plan; wrapper loads existing XSPICE modules, one thread, no user initialization, explicit `ps` for TI models before parsing. Original jobs did not individually freeze loaded `.cm` libraries; the final integrity receipt records their current hashes as supplemental evidence, not a retroactive run-time attestation. Future freezes include them and documentary include pages.

Read [version47 manual](https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf), devices/noise, PSpice compatibility, VSWITCH/aswitch, global node0, transient/IC/nodeset and convergence sections. PSpice VSWITCH translation uses XSPICE analog switching; log-conductance transition and internal global references warrant terminal tests. `nodeset` is a starting guess, not a physical initial condition. [Issue824](https://sourceforge.net/p/ngspice/bugs/824/) supplies a concrete redundant-source/DC/discontinuous-source diagnostic lead; it does not prove the microphone root cause. [Quarles' convergence work](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1989/1216.html) separates equation/model defects from iteration control.

Isolated options are `reltol=1e-6 abstol=1e-16 vntol=1e-10 gmin=1e-15 method=gear maxord=2`; each job budget15s. Reduced original DUTs retain `abstol=1e-15 vntol=1e-9` and60s. All other values are in the frozen plans. No tolerance search, rshunt, clamp deletion, hidden bias resistor or ideal substitute earned real-device performance.
