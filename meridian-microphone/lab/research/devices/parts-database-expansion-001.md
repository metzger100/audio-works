# Parts evidence expansion 001

9 October 2026 · M100 Meridian MIC-34-M/MIC-34-C · K47FRB · P48 · Prompt 06

The library now contains **17 exact semiconductor entries, 21 hash-pinned SPICE files across 15 device types, and 15 exact passive evidence entries**. This expands experimental choices, not a qualified microphone BOM. Six new device types received isolated controls. None receives a blanket noise, sourcing, patent, substitute or candidate-combination qualification. Physical owned stock and capsule measurements remain unknown. No prototype, production topology, purchase or build publication is selected.

Use the searchable [YAML matrix](parts-database-expansion-001.yaml) for roles, exact identities, independent evidence states, models/parents/hashes, behavior conditions, passive fields and gaps; the [CSV index](parts-database-expansion-001.csv) is a compact semiconductor view. The existing [registry](../../models/semiconductor/registry.yaml), [acquisition manifest](../../models/semiconductor/acquisition.yaml), [references](../../models/semiconductor/references.yaml) and [corners](../../models/semiconductor/corners.yaml) remain canonical. Sourcing and exact implementation qualification are separate.

## Verified starting point and research coverage


Before additions, the private baseline receipt `research/device_sources/local/parts_expansion_001/baseline.json` recorded seven device entries, nine present hash-matching valid SPICE files across five types, the hash-matching retained Nexperia HTML failure and fourteen exact passive MPNs. Four JFE150 variants represented one device. MMBFJ113 had no acquired model. The receipt pins the original registry/acquisition/reference/corner/validation/comparison hashes; existing entries, failures and results were retained.

Inspection included acquisition records, conditioned references, corner gaps, `devices/device-model-validation.md`, semiconductor/architecture/robust procurement registers, passive BOMs and [architecture comparison](../architectures/architecture-comparison-001.md). The fourteen families, empty qualified front, adverse leakage/startup/distortion failures and 0019/0017, 0023, 0012 and carrier/CMOS research tracks remain intact. Capsule mechanics/noise/polarization/overload are still unknown; similar devices confer no K47FRB rating or permission to stimulate it.

## Coverage by circuit role



## JFET choices and matching


[TI JFE2140](https://www.ti.com/product/JFE2140) is an ordinary integrated dual, independent of JFE150 as a device but sharing TI as manufacturer. Its [SLPS730B sheet](https://www.ti.com/lit/ds/symlink/jfe2140.pdf) specifies conditioned low-current noise and matching; 25°C VGS mismatch is at most 4mV at 2mA, full-temperature bound 4.2mV, and Idss ratio 0.95–1.05. These are ordinary production bounds, not selected-pair permission. The public PSpice and TINA archives have byte-identical `jfex140.lib` members. The vendor instructs two half-model instances for one physical package; identical simulated halves do **not** model guaranteed mismatch, thermal coupling or a distribution. Explicit documentary coupled bounds were added without fitting synthetic process corners.

## Ordinary BJTs, MOS/CMOS and support controls


**5551/5401 parts are BJTs.** [Nexperia PMBT5551](https://www.nexperia.com/product/PMBT5551), exact `PMBT5551,215`, is a 160V NPN SOT-23 option with an original self-contained model. Model C/B/E order differs from physical B1/E2/C3. At 5V/25°C, beta was 143 at 1mA and 121 at 10mA, above corresponding minimum 80. Temperature/current grids −10/25/50°C and 100µA/1/2/10mA are retained. The 52V fixed-base-temperature stress produced 114mA at 102°C: that invalidates the assumed 2mA/104mW thermal point and exceeds package power by a wide margin. It demonstrates the need for current feedback; it is not a safe operating point or electrothermal solution. Open-emitter capacitance and 25°C ICBO fixtures emitted strict convergence warnings; no cap/leakage validation credit is assigned from those outputs. KF is absent.

## Passive dependency audit


The fourteen original exact MPNs remain individually indexed with their original sourced fields; no resistor/capacitor idealization was promoted. RC0603/AC0603 thick-film series tolerances and TCR do not specify excess-noise spectra. HVA12JA1G00's 5% tolerance,200ppm/°C TCR and20ppm/V VCR require coupled bias/temperature/leakage sensitivity; external surface insulation is unknown. Two exact 500MΩ elements would change noise/leakage/layout and need a realized child, not inherit 1GΩ qualification. Stackpole public/mirror acquisition failures remain. [Vishay CRHV](https://www.vishay.com/docs/68002/crhv.pdf) supplies series-level high-R/VCR guidance; exact ordinary MPN/MOQ/retail coverage is incomplete, and consult-factory options are excluded.

## Procurement and patent boundaries


[The dated sourcing register](../procurement/parts_expansion_001_2026-10-09.yaml) separates exact variant, seller, private Germany eligibility, stock age, MOQ/multiple, factory pack, dispatch, intended quantity and conditional costs. Most direct retail fetches failed; reported stock is indexed, not live orderability. Some exact modeled NPNs show zero stock; independent exact options have no acquired model. Specialist JFET order-code aliases are not silently equated. Multiple retailers do not remove a single-die/manufacturer dependency.

Refreshed [DigiKey Germany terms](https://www.digikey.de/en/terms-and-conditions) address non-business EUR customers and distinguish warehouse DDP from supplier/marketplace CPT. [Delivery guidance](https://www.digikey.de/en/help-support/delivery-information) quotes 25EUR below 75EUR; tax basis/dispatch and exact fees are not fully established. Individual one-slot 19%VAT/shipping scenarios are labelled, never summed across alternatives. All confirmed delivered totals remain null. One fixed K47FRB capsule and mechanical/PCB/connector/test costs remain separate unknowns. No spending cap, cost winner, order, contact or top-up is proposed.

## Controls, verification and handoff


[Initial finite plan](parts-control-plan-001.yaml) and [final child plan](parts-control-plan-002.yaml) preserve deterministic bias grids, unchanged 15s/job timeout,100-job finite bounds and existing 20% typical/1% numerical screens. No random specimen selection, fitted parameters or budget/qualification threshold changes occurred. Full frozen source/model/spec snapshots, decks, diagnostics, raw/CSV hashes and results for the six-device characterization are under `results/device_models/`:

## Reading and evidence

This compact view retains findings and limits. Consult the [complete original report](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/parts_database_expansion_001.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../docs/evidence.md) and [scientific contract](../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../docs/validation.md).
