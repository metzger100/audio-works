<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Architecture comparison 002 — 17 October 2026

**No implementation qualifies for prototype selection.** The realized filtered servo0025 improves its parent's conditional noise and paired response screen; fixed-bias0017/0019 retain lower current/count and slightly lower nominal modeled noise. Leakage, loaded output/balance, nonlinear/device evidence and physical unknowns prevent an overall winner. M100 Meridian MIC-34-M/MIC-34-C, K47FRB/P48 remains conditional research. No production topology, PCB or physical prototype is selected.

[Finite plan](architecture-comparison-002.yaml) · [later-work audit](comparison-audit-002.json) · [primary-source methods](comparison-source-notes-002.md) · [machine comparison](../../results/reports/architecture_comparison_002/comparison.json) · [tables and exact implementations](../../results/reports/architecture_comparison_002/tables.md) · [provenance/hashes](../../results/reports/architecture_comparison_002/provenance.json) · [validation](../../../../docs/validation/2026-10-17-comparison-002.md).

## Audit, finite cohort and boundaries

Inspected comparison001, its staged generator/provenance,17 original suite records,six optimizer records and original parents. Read-only verification rechecked9,117 declared original files. Comparison001 and frozen originals were not rewritten. Prompts6–11 contain actual finite outputs with incomplete gates; Prompt12's written task has no located completed sourcing/preservation report. Earlier inventories and catalogue receipts do not complete that task. The later carrier formula correction, failed macros, isolated controls, adverse cases, all14 family records and22 concepts remain authoritative. The [knowledge matrix](diverse-knowledge-001.json) retains unimplemented mechanisms and family-specific falsifications. Solver/model failure retires no family.

The plan was recorded before evaluation. Eight exact existing implementations/controls received the complete existing14-check suite attempt. The five realized representatives additionally received18 shared named capsule/interface scenarios,16 independent paired holdouts,four tolerance/TCR/opposed output-capacitor endpoints and one refinement; the four JFETs also received two complete weak/strong-file stresses. Total:203 matched cells and731 simulator jobs; eight simulator errors remain. No value search, new structural child, threshold/range amendment or optimizer budget extension occurred.

## Realized mechanisms and nominal evidence

Values below use the ordinary suite's original32/decade response and64/decade stationary noise grids. Matched/refined values are separately identified. Noise is20Hz–20kHz electronics-only, conditional on assumed capsule transfer and incomplete device spectra; A denotes A-weighted pressure equivalent. It is not capsule acoustic self-noise.

|Representative|Operating principle / niche|P48 mA; active/total count|Response dB|Noise unweighted / A, µPa RMS|
|---|---|---:|---:|---:|
|0017|Fixed-divider/source-degenerated JFE150; two47µF/output leg|4.10355;5/48|0.792408|309.901 /165.144|
|0019|Same input; four47µF/output leg improve LF drive|4.10355;5/52|0.660555|309.895 /165.141|
|0023|Discrete source-current servo; unfiltered final backplate|5.15043;7/72|0.472123|1051.74 /959.674|
|0025|Actual0023 child;100nF WIMA final-backplate filter with IR/ESR/ESL|5.15043;7/73|0.575066|362.825 /194.694|
|0012|BJT differential charge feedback and continuous resistive reset|4.08600;5/45|20.9306|113896 /84283.1|
|0010 /0014|Actual CMOS guard /charge integrations|unknown;6/40,5/38|unknown|unknown|
|0013|Ideal anti-phase bridge/buffers/multiplier/outputs with passive P48 support|1.23425 partial;1/36 partial|unknown|unknown|

Each [table entry](../../results/reports/architecture_comparison_002/tables.md#exact-implementations) links its frozen netlist/BOM/full suite and faithful terminal-connectivity diagram; companion connectivity tables retain every source line and ordered pin. Equivalent loss/insulation/inductance branches are not counted as additional physical parts.0013 is an ideal mechanism/integration control, not a realized carrier architecture; its incomplete power/count cannot compete with actual microphones.

All candidates extract P48 through two2.2kΩ paths, filter raw power and use a divider/NPN follower rail with midpoint/polarization networks. Loaded rails are13.5558V(fixed),11.0103V(servo) and13.5983V(BJT); actual simulated front polarization is26.1001V,22.5462V(0023),22.5434V(0025) and22.3107V(BJT). None is a permitted capsule bias. Real output variants drive both legs, using a phase inverter except the bipolar differential pair; balanced wiring does not imply impedance balance.

No-selection strategy is fixed nominal parts, degeneration or feedback plus documented variation, with no matching/hidden trim. Missing manufacturer-bounded joint populations prevent a no-selection production claim. The finite JFE weak/strong stresses execute but retain their known gm/limit-validation failures. The BC846B model is the explicit emitter-r1 child of the retained faulty vendor parent; no vendor approval or missing flicker/noise law is inferred.

0025 reduces nominal unweighted modeled noise65.50% versus0023 at a response penalty0.102943dB and one added physical part. Its sensitivity rises10.7251→10.8544mV/Pa; power is essentially unchanged within model uncertainty. Continuous proposals retain their exact prior identities and [actual parameter deltas](../../results/reports/architecture_comparison_002/realization-deltas.csv); their older performance is not pooled.0017/0019 noise differs by less than the measured refinement scale, so no separate noise rank is assigned.0012 remains the strongest completed ordinary-passive no-FET charge control in this audit;0024's smaller series feedback C moves the unchanged reset pole into audio and does not justify promotion.

## Adverse, withheld and assumption-sensitive results

[Matched cases](../../results/reports/architecture_comparison_002/matched-scenarios.json) preserve the retained45–100pF front/rear,1GΩ–100TΩ leakage,0.5–10pF case and0–5pF cross-capacitance envelope,5–40mV/Pa sensitivity and common interface stresses. Coupled-gap/sensitivity records are literature-derived analogies, not observed K47FRB tolerances. Loss-tangent, electrostatic-softening and excess-current examples remain supplementary analytic assumptions in the earlier envelope records; they have no validated hardware distribution or new device performance credit.

|Matched case;64/decade response|0017|0019|0023|0025|
|---|---:|---:|---:|---:|
|Nominal|0.790175|0.658615|0.472129|0.573313|
|Case10pF/cross5pF|0.777155|0.645595|1.27659|0.572664|
|Rear45pF plus those strays|0.777155|0.645595|2.08442|0.572664|
|1GΩ leakage|22.9347|22.8075|18.4621|19.3080|
|44V/high-feed/100m/600Ω/−10°C stress|3.49260|3.08442|2.73792|2.84957|

The unfiltered servo loses its nominal response lead in rear/case/cross regions. The filtered servo controls those tested parasitic cases better but still fails1GΩ and the combined cable/load/supply case. At1GΩ, conditional electronics noise is18.705mPa(0019),17.295mPa(0023) and13.750mPa(0025); noise order reverses while every response fails. Earlier DC oracles retain servo saturation and gate/source order reversal; this comparison does not repair authority.

Corrected paired holdout DC/AC screens pass13/16 for0017,0019,0025;2/16 for0023;0/16 for0012. Exact95% binomial intervals are[0.54354,0.95953],[0.01551,0.38348] and[0,0.20591] respectively, conditional only on this artificial sampler. Worst responses are1.68275,1.42133,1.29838,1.82701 and22.6014dB in that same candidate order. No all-requirement manufacturing yield is known. Original annotation-error denominators remain in [original summaries](../../results/reports/architecture_comparison_002/original-uncertainty.csv).

Nominal64→128/decade response refinement changes at most0.0007522dB;128→256/decade integrated noise changes at most0.00481%. These are numerical scales, not model-error bounds. Incomplete semiconductor current/flicker spectra, capsule transfer/leakage excess noise, capacitor temperature/absorption and joint process variation dominate the unresolved uncertainty. [Spectra](../../results/reports/architecture_comparison_002/noise-spectra.json) and [disjoint contributions](../../results/reports/architecture_comparison_002/noise-contributions.json) derive from original root vectors and verify quadrature closure. Capsule/environment Johnson surrogates are explicitly excluded from electronics totals; missing physical noise is not zero.

## Remaining checks and scoped fronts

[Coverage](../../results/reports/architecture_comparison_002/coverage.csv) includes every required check, errors, adverse finite values and reasons. All eight suites remain failed/unqualified. The fixed candidates pass their supported nominal rail-startup screen(3.596s/4.260s); the servos fail, and the5s observation edge is not achieved settling. Earlier supply-dip/recovery and voltage-return diagnostics retain their own cohort, censoring and bilateral-loop limitations. This cohort's HF/no-peaking test cannot establish loop stability. Hotplug, ESD, distributed RF cable, self-heating and physical protection remain unsupported.

The full suite records loaded two-port output matrices/balance and cable/preamp cases. Nominal maximum differential impedances are298.50Ω(0017),249.49Ω(0019),269.63Ω(0023/0025); mismatch is4.503%,5.306%,12.053%,12.037%. These fail the200Ω/1% targets. The input table records actual moving-return admittance under the driven capsule boundary; it is not an independently isolated input two-port. Charge-node voltage suppression alone is not conversion loss.

H2/H3/H4–H10,THD,electronics clipping and headroom remain null: full-DUT settled nonlinear prerequisites fail. Isolated follower/synthetic harmonic controls do not settle microphone behavior. There is no conversion of censored headroom into maximum acoustic SPL and no mechanical-noise, overload or polar-response rating. CMOS macro integration failures do not reject CMOS sensing. Earlier successful grounded/ideal controls remain separate from the failed actual floating/charge fixtures. Carrier deterministic and32 seeded ideal periodic-noise controls remain separate from stationary noise and failed0013 integration; oscillator/mixer/buffer/device covariance, dynamic loaded power and capsule RF permission are missing.

The [research Pareto view](../../results/reports/architecture_comparison_002/research-pareto.json) uses only nominal response/current/count among the four identical-device-scope JFET implementations:0017,0019,0023 remain on that projection.0025's useful conditional noise benefit is excluded from dominance because noise validation is incomplete. BJT/CMOS/carrier, costs, yield and continuous proposals do not enter that joint front. The stricter [production/physical fronts](../../results/reports/architecture_comparison_002/production-front.json) stay empty with their original gates.

## Parts, costs, patent holds and next milestone

[Per-reference BOM](../../results/reports/architecture_comparison_002/bom.json), [quantity/package/source/pack scenarios](../../results/reports/architecture_comparison_002/procurement-lines.json) and [cost axes](../../results/reports/architecture_comparison_002/cost.csv) preserve exact grades, ratings and tolerances. Each alternative implementation is for one intended finished microphone, not a basket of comparison purchases. Exact Germany private orderability/delivered EUR totals remain unknown. Historical priced net electronics subtotals are partial and dated; new WIMA EUR0.55 VAT-inclusive retail evidence is not a delivered quote. One fixed K47FRB, mount/body/headbasket/PCB/connector and other costs remain separate nulls; missing shipping/import/payment fees and unverified pack excess are visible. K47FBSB's default price is rejected for K47FRB. BC850C/PMBT5551 have only isolated tradeoff evidence; OPA928 and other leads are not integrated qualified substitutes. No untested combination inherits a favorable result.

The exact eight circuit hashes match [executed candidate screening001](../patents/candidate-screening-001.md). Claim mappings, territorial records, activities, search limits and holds remain frozen inputs. [Three17October official German observations](../../results/reports/architecture_comparison_002/patent-status-refresh.csv) agree with16October: EP2675188 is labelled“Anhängig/in Kraft”; EP1585365 and EP2974369 are labelled“nicht anhängig/erloschen”, with their individual term/nonpayment events retained. Other official observations retain16October dates. No new structural change or claim coverage conclusion is inferred. Official US/amended/pending/family/territory and material interpretation gaps retain all affected prototype/manufacture/build-publication holds. No legal clearance or simulation-derived safety claim is made.

The [updated measurement handoff](../../measurement/comparison-002-handoff.md) keeps physical access deferred. The next milestone is a discriminating prerequisite, not a production design:

|Useful niche|Smallest next falsification|
|---|---|
|0017/0019 low-count/current|Reduce the coupled full-DUT transient failure one physical network at a time; retain1GΩ bias failure. Establish independent intended-bias JFE current/noise behavior before a new performance claim.|
|0023/0025 servo/filter|Bilateral loaded return-ratio and DC actuator-authority control at nominal/1GΩ; distinguish real filter absorption/leakage/temperature from the constant-law assumption. Stop the full-envelope authority claim on saturation.|
|0012 no-FET charge/reset|Actual low-current base-current spectra/two-port plus two reset-actuator authority endpoints; reject that actuator hypothesis if LF noise or DC compliance fails. Retain alternative no-FET mechanisms.|
|CMOS guard/charge|Unchanged macro in the documented grounded charge reference backend, then complete terminal translation/reset and loaded guard return/noise. Retain backend failure without ideal performance substitution.|
|Carrier/floating|Calibrated correlated physical-device injection or supported periodic source/covariance analysis before a real oscillator/mixer/output implementation; keep RF capsule permission unknown.|

All14 families remain open with their existing finite tasks. Later safe physical work still requires electrode/approved-stimulus documentation, calibrated complex admittance/leakage/noise/transfer, realistic device/SOA evidence, exact procurement and complete applicable patent review before affected prototype gates.


[Reproduction, exact cohort/seed contracts and retained reporting failures](comparison-reproduction-002.md) preserve the detailed methods. GitHub covers committed authored/compact evidence; ignored originals remain local.
