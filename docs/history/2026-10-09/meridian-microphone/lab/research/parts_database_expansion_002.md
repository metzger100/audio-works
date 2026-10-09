# Parts evidence strengthening 002

9 October 2026 · M100 Meridian MIC-34-M/MIC-34-C · K47FRB under P48

The database is stronger in identity, provenance, search, evidence-state separation and reproducible controls. It now contains **20 exact semiconductor entries, 27 distinct hash-pinned SPICE files across18 device types,16 exact passive entries and17 separate documentary leads**. Physical owned stock remains unknown. Scientific behavior, live sourcing, patent clearance and physical qualification are still incomplete; they cannot honestly be described as strong merely by improving the catalogue.

The verified continuation baseline was17 entries/21 SPICE files/15 modeled types/15 passives. The original seven-device/nine-file baseline and failures remain in [expansion001](parts_database_expansion_001.md). Four JFE150 variants still count as one device; MMBFJ113 still has no acquired model. Two historical TI revisions added here count as files, not additional parts or independent manufacturers.

Use the [machine-readable matrix](parts_database_expansion_002.yaml), [CSV index](parts_database_expansion_002.csv), [dated search/acquisition ledger](parts_sources_expansion_002_2026-10-09.yaml), [sourcing register](procurement/parts_expansion_002_2026-10-09.yaml) and [technical prior-art handoff](patents/parts_expansion_002_2026-10-09.yaml). The existing semiconductor registry, acquisition manifest, references and corner records remain canonical. Earlier reports, raw failures, inventories and frozen sources were retained.

From the lab, search exact names, manufacturers or any recorded evidence:

```sh
.venv/bin/python research/parts_database.py 5551
.venv/bin/python research/parts_database.py --role p48_power --state characterized
.venv/bin/python research/parts_database.py --counts
.venv/bin/python research/parts_database.py --audit
```

The audit checks the searchable view against exact canonical identities/model hashes/states, keeps model variants separate, and rejects unconditioned physical-behavior passes or unsupported candidate qualification. Search works without redistributing manufacturer bytes. “Acquired” means the recorded model acquisition for semiconductor/lead rows; the PP passive explicitly marks acquisition as a datasheet, with characterization false.

| Aspect | Current evidence quality | Exact remaining requirement |
| --- | --- | --- |
| Identity, provenance and state integrity | Strong metadata and regression coverage | Original ignored bytes require private restoration; neither model loading nor a typical point qualifies a part |
| Mechanism coverage | Every role has primary routes, experiment blockers and next falsification | Carrier periodic noise, fully supported independent JFET noise/leakage and full charge/guard behavior |
| DC/capacitance/leakage controls | Useful restricted PNP and existing NPN/diode controls | Exact temperature/bias laws, production covariance and package/SOA/electrothermal behavior |
| Noise/transients | Conditioned PSD/NF oracles and retained discrepancies | Independent spectra at actual operating currents; no unreferenced transient, flicker or periodic-noise credit |
| Practical passives | Exact PP package and conditioned IR/DF supplement PET/C0G/electrolytic audit | High-R excess noise/board insulation; absorption/time/temperature law; every real combination |
| Germany sourcing/cost | Exact routes, MOQ/packs and primary consumer/shipping terms | Live exact stock/acceptance, actual dispatch and complete intended-use delivered totals |
| Patent screening | Source-linked feature flags and distinct implementation gates | Prompt11 exact candidate claims, DE/EP territories, current official status and material professional interpretation |
| Physical evidence/preservation | New original evidence locally verified and privately recoverable | Capsule/owned-stock measurements,89 legacy missing sources and independent persistent private backup |

## Useful additions and failures

[Diodes MMBT5401-7-F](https://www.diodes.com/part/view/MMBT5401/) is a150V PNP SOT23 option, separate from5551 NPNs and from another maker's5401. The working original [manufacturer model](https://www.diodes.com/spice/download/2587/MMBT5401.spice.txt), version2 dated08FEB2011, closes the complementary-PNP acquisition gap. Original bytes/notices stay private. The [DS30057 Rev12-2 sheet](https://www.diodes.com/datasheet/download/MMBT5401.pdf) supplies the independent conditioned limits.

At VCE5V25°C, beta121.94 at1mA and124.92 at10mA passed the corresponding50 minimum and60–240 interval. Cobo3.706pF atVCB10V1MHz passed6pF; modeled ICBO6.37pA at120V25°C and4.78nA at100°C passed their separate limits. These are isolated model points, not measured parts or a temperature law. The local1kHz NF screen was8.790dB at200µA/VCE5V/**Rs10Ω**, exceeding the sheet's8dB limit. The unspecified instrument filter prevents a conclusive measured NF equivalence; it remains a failing conditional screen. KF is absent; no low-frequency input-noise merit follows.

The100µA/1mA/2mA/10mA grids at−10/25/50°C and coupled44/48/52V support fixtures remain available. An ordinary1kΩ emitter/100kΩ base-resistor fixture produced0.541/0.630/0.695mA and23.5/29.9/35.6mW across those coupled conditions. The substantial base-feed drops0.490/0.467/0.450V demonstrate why actual support circuitry matters. This is an isothermal nominal fixture using existing exact RC0603 values, with an ideal test reference; it is not a regulator implementation, thermal solution or qualified BOM.

[DMMT5401-7-F](https://www.diodes.com/part/view/DMMT5401/) adds an ordinary factory-matched adjacent-die PNP package. [DS30437 Rev9-2](https://www.diodes.com/datasheet/download/DMMT5401.pdf) specifies maximum2% matching under its stated gain/saturation tests. This is ordinary documented production variation; no selected specimens or matching service is used. Pin order isC1/B1/B2/C2/E2/E1, physical1/2/3/4/5/6. Its200mA per-half and300mW **combined** package limits differ from the discrete part.

Its independent control passed tested gain/capacitance and100°C leakage rows, failed the same conditioned NF screen, and retained a25°C leakage convergence warning. The two nominal halves produced equal10.001mA currents: numerical symmetry does not validate the2% matching envelope, shared heating or production covariance. No behavior credit was transferred from the discrete package.

[Diotec2N5551](https://diotec.com/en/product/2N5551.html), ordinary TO92 taped package, now has its own acquired original2017 example and2025-01-17 sheet. It is an NPN BJT, as are MMBT5551 and PMBT5551; onsemi2N5551BU remains a distinct documentary option. Diotec's website1500mA technical field conflicts with its600mA datasheet; the sheet controls. Pin/footprint implementation remains unqualified.

The wrapper now accepts the specifically documented `ltpsa` mode from the [ngspice47 release manual](https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf), retaining existing `ps` behavior and rejecting arbitrary/injected modes. Diotec2N5551/MMBT5551 then fail because their files use an undeclared pi constant. A separate frozen control declared only mathematical pi in the fixture; parsing proceeded but ngspice warned that BVCBO/BVBE were ignored. Strict failure handling remains. The original models receive no accepted performance, breakdown or implementation credit. The SOT23 sheet is dated2025-11-19; one retained control label incorrectly says2025-01-17. Its numeric limits were independently checked against the exact SOT23 sheet; that label error is disclosed, not silently repaired in frozen evidence.

Linear LSK389A's metadata-only child exposes ignored ISR/NR/ALPHA/VK on this backend. No accepted DC/noise/leakage characterization follows from its raw outputs. The original and child retain distinct ancestry/hashes. JFE150/JFE2140 and LSK170A still provide two manufacturer sources for restricted discrepancy/DC experiments; complete low-frequency/current-noise/leakage/charge validation remains blocked. J113/MMBFJ113, InterFET and historical names remain research leads without invented models or performance.

OPA928's grounded16V25°C nodeset control retains15.684nV/√Hz at1kHz and fixed275µA macro current. Translating the same16V follower by+20V produces convergence/singular failures. OPA1656 and LMP7721 still time out at15s even with an output initial guess. These failures are preserved; nodeset changes no electrical bias or accuracy budget. Guard load, servo/charge behavior, supply limits, physical leakage and overload remain unsupported.

Primary TI TINA/reference files were also recovered. OPA1656 TINA1.2 dated23JUN2021 differs from the existing PSpice1.3; OPA928's reference archive contains older1.0, while its current TINA1.1 member is byte-identical to the existing model. Distinct older revisions are registered as uncharacterized historical manufacturer controls. Duplicate members are not extra files/devices, and older revisions do not silently replace current models. Binary TINA reference circuits are not declared runnable SPICE.

## Support circuitry, sourcing and handoff

[TMUX1102](https://www.ti.com/product/TMUX1102) documents an active-low low-voltage switch and a charge-injection test using Q=C_LΔV. Its current/leakage/Ron/injection figures are conditioned, and its public IBIS route does not supply an analog periodic-noise SPICE model. The exact SC70-5 TMUX1102DCKR remains a carrier research lead requiring regulation and real injection/leakage/noise controls. No ideal-switch result becomes implementation evidence.

[WIMA MKP2D031001F00KSSD](https://www.tme.eu/de/details/mkp2-100n_100/tht-folienkondensatoren/wima/mkp2d031001f00kssd/) adds an exact100nF±10%100V nonpolar PP package,5×10×7.2mm/5mm pitch. The [manufacturer03.26 document](https://www.wima.de/wp-content/uploads/media/e_WIMA_MKP_2.pdf) supplies IR≥100GΩ at20°C100V after1minute, discrete DF limits and0.05% series absorption guidance. These are not a broadband/temperature/time-constant law. The retailer's110°C conflicts with the sheet's100°C; the sheet controls. The exact German route displays0stock,MOQ/multiple1,3500factory pack and€0.59 gross; future lead time is unknown. It is an investigated practical coupling/compensation option, not a qualified PET/C0G substitute.

The existing1GΩ dependency remains material:10pA through1GΩ gives10mV, BAV199's5nA limit would give5V, and a300pA JFET leakage bound gives0.3V. These are arithmetic scenarios at their respective specification conditions, not actual simultaneous currents or safe capsule biases. At298.15K an ideal1GΩ resistor has4.058fA/√Hz Johnson current noise; excess noise and surface leakage remain unknown. HVA's tolerance/TCR/VCR must be coupled, and two500MΩ resistors need their own qualification. Ohmite RX-1M1007FE is an independent1GΩ catalogue lead, but its advertised PDF endpoint returnedHTML200; the failed bytes remain evidence, with no inferred noise/TCR/VCR law or Germany stock.

EEU-FR1J470's29.6µA rated-bias/2minute leakage bound scales to59.2–118.4µA for2–4parallel capacitors per leg only at that test condition. It does not establish low-bias leakage, absorption, audio-wide ESR or reverse-startup capability. Each actual count and polarity combination remains unqualified.

The [TME Germany consumer terms](https://static.cs.tme.eu/2025/01/677d16e64f859/de.pdf) explicitly permit consumer guest ordering. The [primary shipping page](https://www.tme.eu/de/how-to-buy/7345/Transportart-und-Transportkosten/) quotes€9.40 gross below15kg and approximate1–2working days after advance payment receipt; bank-transfer fees remain customer-dependent. An exact PNP DigiKey route and exact WIMA TME route now have preserved dated price/stock/MOQ observations. Direct requests still returned403, and indexed stock is not live orderability. No confirmed delivered cost, purchase, contact or comparison-stock recommendation is asserted.

TI's [2018 phantom-power application report](https://www.ti.com/lit/pdf/SBOA320) and [noise analysis note](https://www.ti.com/lit/pdf/SBOA345) supply technical support-circuit/current-budget/noise handoffs. The electret example cannot establish a K47FRB operating envelope. Component/model terms and ordinary matching do not resolve the existing differential/JFET/BJT/current-sink, bootstrapped input or phantom-cascode claim flags. Current official DE/EP family/status and exact candidate mappings remain missing; affected prototype/manufacture/build-publication gates stay held under Prompt11.

The justified next set is **PMBT5551 plus MMBT5401 restricted feedback/current-budget controls, DMMT5401 documented mismatch/combined-power sensitivity, LSK170A/JFE2140 discrepancy controls, and OPA928 grounded/floating prerequisites with exact PP/C0G support values**. They address mechanism gaps; none is a microphone substitute or procurement selection. Carrier, full independent JFET behavior, high-R noise, exact live sourcing, patent implementation screening and capsule measurements remain explicit prerequisites.

## Immutable controls and completion

- [Plan003](parts_control_plan_003.yaml): [27jobs/14errors](../results/device_models/20261009T145346Z_parts2_742caaa3/results.json), all source hashes unchanged.
- [Plan004](parts_control_plan_004.yaml): [6jobs/6errors](../results/device_models/20261009T170734Z_constant_ae3a9e1d/results.json), missing-constant fixture only, sources unchanged.
- [Plan005](parts_control_plan_005.yaml): [13jobs/1error](../results/device_models/20261009T171204Z_dual_pnp_9ff5882e/results.json), exact independent package control, sources unchanged.

Each driver, imported helper, plan, backend wrapper, models/spec and primary-source inputs is included in its initial frozen manifest. All46jobs and21errors survive. No15s/100job budget,20% typical screen,1% numerical threshold, qualification gate or capsule assumption changed. Device transient validation was deferred because independent references/settled extraction remain absent.

The search ledger preserves14web sessions (13raw records; first exact UTC/raw absent) and32direct response receipts, including HTML/404/403 outcomes. [Decisions](parts_database_expansion_002_decisions.md), [validation](parts_database_expansion_002_validation.json) and [preservation](parts_database_expansion_002_preservation.json) record completion checks. GitHub publishes project-authored research metadata and sources. New unresolved-redistribution manufacturer bytes and raw waveforms remain private; existing tracked synthetic probe traces retain their original history. GitHub history provides remote recovery for published files; it does not close private-original backup coverage.
