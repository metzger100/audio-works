# Phase 3 semiconductor-model prerequisite — current review 2026-10-09

Current handoff: [expansion002](parts-database-expansion-002.md),20 exact semiconductors/27 model files across18 types. Conditioned PNP controls and ordinary matched-package evidence improve support coverage; strict compatibility/noise/floating failures remain. Earlier reports retain their original scope.

**Readiness remains partial.** The existing JFET, CMOS and bipolar evidence was inspected before changes. This follow-up adds an unmodified Vishay MOSFET model, dated sourcing evidence, isolated characterization and stronger provenance. Nine valid hash-pinned SPICE files now cover five device types; the failed Nexperia response and all previous failures remain. No production topology, PCB, prototype or microphone candidate was selected.



## Current additions and coverage


The [registry](../../models/semiconductor/registry.yaml) retains the original versions and adds `vishay_2n7002k_ps`: **ECN S14-1598 Rev. B, 11 August 2014**, SHA256 `d59ce922b2c814e4aaa63f27459696b8c71494fac61f47c8cf8c093eba273111`. The [public manufacturer archive](https://www.vishay.com/docs/77603/2n7002k_ps_revb.zip), [model guide](https://www.vishay.com/docs/73307/2n7002k_ps_revb.pdf) and [Rev. F datasheet](https://www.vishay.com/docs/71333/2n7002k.pdf) have separate pinned hashes and acquisition records. The model predates the datasheet; exact die/model continuity is not established. Vendor bytes/notices remain private and ignored because redistribution permission is unclear. The public SPICE download required no explicit agreement; the separate Ultra Librarian ECAD agreement was not accepted.

## Vishay measured model agreement and disagreement


Independent references are recorded in [references.yaml](../../models/semiconductor/references.yaml). Typical table values, coarse visual intervals and guaranteed limits remain distinct. The existing 20% typical-value and 1% numerical-refinement screens are unchanged. The MOS table marks relevant high-current tests as pulses no longer than 300 µs and duty no greater than 2%; their DC simulator decks approximate an isothermal pulse value. Values above the continuous-current rating are **simulation references**, not instructions for physical DC testing or evidence of SOA.

## Current sourcing, provenance and gates


The separate [2026-10-09 procurement register](../procurement/semiconductors_2026-10-09.yaml) supplements the unchanged 2026-10-05 record. It records exact SOT-23 variants, intended one-slot quantities, MOQ/pack excess, manufacturer and dispatch lead-time evidence, EUR net/gross observations, optional reel fees and unknown delivered costs. Vishay has two independent retailer routes; indexed MMBFJ113 routes improve alternative sourcing investigation. TI JFE150/OPA197 ACTIVE pages were directly retrieved. Retail direct requests returned 403 or access-denied/challenge content despite some HTTP 200 responses; those failures and indexed crawl ages remain preserved. No live-stock or completed private Germany order claim is made.

## Current verification and preservation


`./run doctor` passes with ngspice 47 and the unchanged specification hash. [Verification 20261009T070533Z_a602e6d5](../../results/verification/20261009T070533Z_a602e6d5/verification.json) passes **38 tests**, including affected P48/capsule/loading/noise/harmonic controls and the new device/provenance controls. No physics-control failure remains in that verification. The MOS observer-sign failure and all device disagreements remain in their original records; passing regressions do not qualify those missing device behaviors.

New raw waveforms, CSVs, frozen vendor sources and reference snapshots are privately retained. The [dated inventory](../../results/evidence-20261009T070957Z-3092a887.sha256) adds **258 raw/CSV files**, including verification controls and all failed-parent outputs. [New-record integrity](../device_model_integrity_2026-10-09.json) checks 364 frozen source files and 194 declared device raw/CSV exports with zero mismatches. Root available-byte verification finds no damage or uninventoried waveforms; it remains incomplete because 89 original legacy source files are absent. A temporary private capture and successful restore verified **12,501 available files**; the initial restore's disk-quota failure and the successful retry are retained in private attestations. The restored checkout has its local hook installed. This is same-computer recovery evidence, not independent persistent storage. Independent backup coverage remains incomplete pending an owner-controlled destination; private paths are excluded from the public records.


## Original 2026-10-05 report and evidence


**Readiness is partial and behavior-specific.** Eight hash-pinned SPICE files represent four exact device types, alongside a rejected MOSFET download and alternative investigations. OPA197 alone is the smallest set agreeing with the tested grounded, mid-common-mode, small-signal DC/capacitance/bandwidth/noise references. There is **no fully validated device set for a complete JFET/CMOS/bipolar microphone architectural comparison**, production variation or P48 output/power qualification. No architecture, PCB or prototype is selected.

The [registry](../../models/semiconductor/registry.yaml) records exact variants/packages, manufacturer lifecycle/ratings, source/date, version/hash, syntax, redistribution state and represented/missing behavior. [References](../../models/semiconductor/references.yaml), [primary evidence](../device-sources/README.md) and [Germany procurement](../procurement/semiconductors_2026-10-05.yaml) remain separate. Unknown behavior is never zero or a pass.


## Method and evidence


Manufacturer tables/curves constrain the models; independent physical controls constrain SPICE. No physical semiconductor or capsule measurements exist. Guaranteed limits, typical values, coarse graph-reading intervals and numerical consistency have distinct statuses. The predeclared ±20% typical-value screen is a research model-accuracy check, not a microphone specification or production bound; numerical refinement uses 1%. Neither threshold changed to admit a device. Typical weak/strong noise/curves remain quantified references, not guaranteed corner limits.

The [characterizer](../../models/semiconductor/characterize.py) freezes shared sources before evaluation and captures model/version/deck hashes, syntax mode, temperature, raw data, CSVs, errors and parents. Deterministic grids use `rng_seed: null`; no statistical manufacturing distribution is inferred. Vendor bytes, original notices, failed responses, full waveforms and their CSV exports remain locally preserved. Copyright/model redistribution permission was not established, so fresh checkouts use reproducible acquisition rather than redistributed models. Git retains authored scripts, metadata, logs, decks, compact records and waveform checksum inventories; ignored evidence is not deleted.

## Coverage matrix


Agreement means only the listed conditions. Recorded numerical behavior without independent device agreement remains unqualified.

## Quantified disagreement and agreement


### JFE150

At 25°C, VDS=10 V/VGS=0, generic Idss is **26.902 mA** (guaranteed 24–46), GFS **49.109 mS**, **10.71% below** the guaranteed 55 mS minimum. Weak gives **17.904 mA / 36.469 mS**; its −40°C/125°C Idss **18.443 / 14.993 mA** fall below the full-temperature 22 mA minimum. Strong gives **40.049 mA / 37.215 mS**, and also misses the tested 2 mA/100 µA/100 nA gate-voltage intervals. Coupled BETA/VTO/series resistances remain unchanged; these are not a defensible guaranteed production set under tested conditions.

Five nonlinear jobs still fail convergence/timestep checks. Headroom, loaded output supply current, clipping refinement, recovery and THD receive no acceptance. Large internal macro capacitors/global-ground references are documented, without invented transistor-level fidelity. Floating common-mode, low supplies, crossover, thermal/SOA and production correlations require independent tests before an architecture can rely on them.


## Physically coupled controls


[corners.yaml](../../models/semiconductor/corners.yaml) preserves complete vendor weak/nominal/strong proposals and their failures. Bipolar IS/BF/temperature laws are not independently randomized; one-bias guaranteed base-current intervals do not justify a population. OPA197 has no defensible process distribution here.

Independent Shockley controls use β=gm²/(4·Idss), VTO=−2·Idss/gm and VGS(I)=VTO·(1−√(I/Idss)), with LAMBDA=0/no series resistance. The original 24 mA/55 mS tuple predicts cutoff **−0.87095 V**, outside −1.5…−0.9 V. The unchanged [r1 proposal](../../models/semiconductor/proposals/corners-r1.yaml) is preserved. Given gm≥55 mS and the cutoff test, this approximation cannot cover Idss below approximately **24.800 mA**. Manufacturer lower bound **24 mA** remains explicit and uncovered, not narrowed away.

## Readiness, sourcing and implementation gates


For a **restricted numerical batch**, `opa197_pspice` alone supports tested grounded linear feedback/input-noise controls. Add `bc846b_emitter_r1`/`bc856b_vendor` only for nominal DC/saturation/bandwidth output hypotheses, carrying capacitance/flicker/temperature/sourcing gaps. This is not a qualified three-device microphone BOM or cross-family ranking. JFE nominal supports falsifiable hypothesis work with its recorded mismatch, not no-selection production evidence.

Unsupported as qualified microphone inputs: discrete MOSFET low-current/noise populations; production-bounded JFETs; bipolar low-frequency/1/f inputs; other JFET/electrometer ICs; floating/differential/carrier families; complete P48 regulator/protection/output combinations. Keep all 14 architecture families alive. A missing qualified model does not reject a physical mechanism; this task need not produce a passing microphone candidate.

[Early patent-feature flags](../patents/device_library_2026-10-05.yaml) separate isolated model work from future concrete implementations. Candidate-linked claim/territory/current official-status screening is not completed; no clearance is asserted. Clamps, floating bias/power, feedback/guarding and output combinations need actual candidate mapping before affected prototype/manufacture/build-publication gates. No contact, purchase, licence acceptance or external publication occurred.

## Reading and evidence

This compact view retains findings and limits. Consult the [complete original report](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/device_model_validation.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../docs/evidence.md) and [scientific contract](../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../docs/validation.md).
