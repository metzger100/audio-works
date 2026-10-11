# First six-mechanism batch — 9 October 2026

Six original DUT attempts plus nine preserved engineering children test distinct sensing mechanisms under the unchanged K47FRB/P48 envelope. **All are unqualified; no topology, PCB or prototype is selected.**

[Comparison with exact records](architecture-comparison-001.md) · [decisions](first-architecture-decisions.md) · [families](../../search/families.yaml) · [primary observations](../architecture_sources/observations_2026-10-09.json)

## Findings and failures

| Mechanism | Evidence |
| --- | --- |
| Conventional JFET | DC/energy works; final1MΩ backplate noise dominates. Separate100nF filter child reduces conditional electronics noise32.34→18.34dBA; other qualification failures remain |
| Discrete servo JFET |0.913dB nominal response; noise/output/startup/loading fail. No selection or favorable population fitting |
| BJT charge | Valid DC; large feedback capacitance/finite loop and output noise miss budgets.1MΩ→500kΩ reset child retains authority/sensitivity tradeoff |
| Guarded CMOS / CMOS charge | OPA-containing parents and NPN-output children retain convergence failures, including preserved nodeset probe. Grounded small-signal agreement does not validate floating integration |
| Carrier | Isolated bridge/demodulator recovers deterministic signal after local-reference/nuisance-tone extraction repairs. Integrated timestep,periodic noise and oscillator/mixer power remain unsupported |

Common power uses both P48 legs through2.2kΩ, divider-fed NPN rail and real divider current. Ten ordinary1MΩ parts realize10MΩ polarization filtering;47Ω/47µF output legs face actual cable/preamp loading. Ideal output blocks remain explicit where present; do not score partial carrier current as total power.

## Evidence and next action

Original cohorts preserve source/model/spec hashes, seed 34047,16 envelope scenarios where supported, errors and every parent. [Integrity](../first_architecture_integrity_2026-10-09.json) covers62 new records, including failed/repaired controls; [inventory](../../results/evidence-20261009T082728Z-78caabc6.sha256) adds1981 waveforms/exports. Original45-test verification is historical.

[Dated sourcing](../procurement/architecture_parts_2026-10-09.yaml) and per-candidate BOMs retain exact variants, technology/tolerance/package, installed/intended quantities and conditional costs. Alternative BOMs are not a purchase basket. [Patent flags](../patents/first_architecture_batch_2026-10-09.yaml) lack completed claims/current-status screening.

Next: address each mechanism's fastest independent falsification, retain CMOS/carrier prerequisites and validate actual device/loss/leakage/production behavior before ranking. Unknown capsule safety/noise/polarization/overload, live sourcing/delivered totals remain open.

[Complete dated original](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/first_architecture_batch.md) · [Current verification](../../../../docs/validation.md). Original tables, failures, conditions and decisions remain authoritative.
