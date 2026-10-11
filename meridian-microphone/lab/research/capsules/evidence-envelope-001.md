<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# K47FRB evidence envelope 001 — 11 October 2026

**Continue research with the existing assumed nominal and broad coverage. No literature found here justifies a tighter K47FRB central estimate, safe polarization, acoustic noise, maximum SPL or polar rating.** K47FRB remains the selected simulation capsule for MIC-34-M/MIC-34-C under P48. The owner cannot measure it now; all physical tests are deferred and their qualification/safety/calibration gates remain.

[Assumption ledger](parameters-001.yaml) · [similarity matrix](similarity-001.csv) · [source/locator register](sources-001.yaml) · [queries](queries-001.json) · [versioned scenarios](scenarios-001.yaml) · [independent physics](physics-001.md) · [finite experiment receipt](analysis-001.md). The locked specification and baseline comparison cohort are unchanged; no production distribution or architecture selection is asserted.

## Direct evidence and conflicts

The refreshed [Arienne selected listing S01](https://store.arienneaudio.com/microphone-capsules/20-26-arienne-audio-flat-k47-microphone-capsule.html#/12-options-cardioid_omni) identifies **K47FRB, Cardioid/Omni**, supplied mounting hardware and a changed manufacturing facility. It supplies no traceable current electrical test data or approved bias. The unselected product URL can display the Cardioid-only version; retain variant identity rather than transferring its evidence. Current product photographs and the News/FAQ route did not yield an authoritative current lead/isolation drawing. Historical wire-color reports SC14 remain discovery leads.

[Designer post SC01](https://groupdiy.com/threads/soliloqueens-k87-k67-and-k47-capsules.81968/page-19), 10 March 2023, #569, contains informal approximate sensitivity/capacitance and a venting revision warning. Conditional interpretation of −36 dB as dBV/Pa gives 15.849 mV/Pa at stated unity gain/60 V. Its dB reference, receiver loading, pressure calibration, batch and correspondence to today's Flat K47 are undocumented. Use a separate scenario; do not adopt its 70±3 pF as a present tolerance, its voltage as a maximum, or its estimate as calibrated data. The historical [S04 RF discussion](https://groupdiy.com/threads/diy-rf-condenser-mics.71586/page-21) suggests 120–150 pF when sides are combined, without measurement. Its connection assumption cannot identify per-side C.

The [regular Arienne K47 SC02](https://store.arienneaudio.com/microphone-capsules/33-arienne-audio-k47-microphone-capsule.html) lists 70 pF for another product. [Advanced Audio AK47 SC09](https://advancedaudio.ca/pages/cm47le-owner-manual) states 78–83 pF without measurement conditions. [RecordingHacks SC23](https://recordinghacks.com/capsules/) documents the author's per-side measurements averaged together: GK47 78.9 pF, GK49 77.3 pF and CEK47 49.3 pF; the CEK47 maker value 56 pF is at 65 V while the author's value is at 0 V. Instrument, calibration and batch are absent. The CEK47 is described as a dual-backplate K67-derived construction, despite its name. These conflicts demonstrate the value of conditions; none changes the retained range.

[Current RK47 SC10](https://microphone-parts.com/products/rk47-microphone-capsule) documents a single backplate, two diaphragms, 27 mm film diameter and 3 µm film, but no gap, electrode fraction or tension. Other historical K47-family entries use different diameters/6 µm films. Similar body diameter, appearance or K47 naming is insufficient equivalence. Geometry witnesses in the physics note use the RK47 radius as an analogy and explicitly assume the other quantities.

## Similarity and transfer decisions

The machine matrix records exact product/variant, construction, electrode topology, active-area/gap/tension evidence, mount/headbasket, polarization, pattern, amplifier and calibration for ten source groups. No complete microphone test was deembedded: the necessary receiver/loading/gain and uncertainty are absent. Bare capacitance observations remain separate from complete microphone sensitivity/noise/overload.

[Shure SC03](https://www.shure.com/damfiles/default/global/documents/publications/en/performance-production/us_pro_dual_diaphragm_paper_ea.pdf-ff7e23c323c72be3deac4ffd742c1d26.pdf), pp.4–5/13, gives a dual-diaphragm acoustic-network mechanism and tests at several source distances. It cannot supply K47FRB patterns. B&K's retrieved **March 2019 BE1447-12** handbook SC04 supersedes search metadata suggesting 1996; its measurement-cartridge specifications do not transfer. Both Shure-hosted PDF hashes are retained as document variants, never counted as independent tests.

The coupled membrane/air analysis SC19 follows the COMSOL citation chain to Homentcovschi/Miles and their comparisons against published vibrometer results. The equations support independent physical controls, while their geometry-specific noise does not transfer. Haas-Christensen's 2009 thesis SC05 supplies capacitance/loading/finite-loop and reset mechanisms. Its printed force equation has a dimensional error; the independent note corrects it explicitly. The generic COMSOL documentation also has a surface-density prose issue, recorded rather than copied into the calculation.

Patent publications SC06/07/20/21/22 supply construction, push-pull, guard and charge/reset mechanisms. One diaphragm between two backplates differs from K47's two-diaphragm hypothesis. Patent dimensions/voltages are embodiments, not capsule limits. [Prompt 11 feature handoff](../patents/capsule-envelope-001-leads.yaml) links actual candidate hashes and preserves the unresolved claim/territory/current-status holds. No commercial microphone circuit was cloned or introduced.

## Assumptions retained and added

| State | Parameter/evidence | Treatment |
| --- | --- | --- |
|Direct fact|Current selected-product identity; repository's locked parameter values|Document facts only, no measured specimen |
|Analog-derived central scenario|Historical conditional 15.849 mV/Pa; coupled gap/compliance witnesses|Versioned supplementary probes; existing 20 mV/Pa stays assumed |
|Retained adverse coverage|Front/rear 45–100 pF; Sref 5–40 mV/Pa; leakage 1 GΩ–100 TΩ; case 0.5–10 pF; cross 0–5 pF|No narrowing, likelihoods or discarded failures |
|New supplementary stress|Loss tangent, excess-current 1/f and local electrostatic-softening hypotheses|Analytic term/amplitude assumptions, separately labelled; not new certified bounds |
|Unknown|Lead isolation, active area/gap/tension/damping, C versus approved bias, acoustic/noise/overload/covariance/temperature laws|Nulls, no favorable credit |
|Not transferable|Regular versus Flat; Cardioid-only versus Cardioid/Omni; system versus capsule; normalization versus approved bias; dual-backplate versus dual-diaphragm|Explicit rejection ledger retained |

The disk witness reproduces assumed C/S mathematically, but its implied3µm film stress exceeds the other industrial Mylar grade's typical ultimate strength (SC25). That material transfer is explicitly rejected and preserved. Separately frozen annular center-constraint examples reproduce the paired C/S scenarios below that other grade's F5 typical stress; actual film/constraint/damping/equilibrium and allowable stress remain unknown. At fixed area/tension, paired 45/100 pF gap changes imply 12.857/28.571 mV/Pa at the mathematical reference. Independent front/rear and opposed combinations test identifiability without claiming a production joint distribution. The current simulator imposes a shared SREF for both pressure ports and no acoustic network; rear-specific compliance cannot be inferred from these runs.

For leakage, equilibrium resistor noise, dielectric loss, excess current noise and acoustic/Brownian noise are distinct. The RC thermal integral and reset kT/C identity validate their equations, not the unknown amplitudes/mechanisms in the real unit. Constant-voltage and constant-charge electrostatic boundary conditions differ. Simulated softening or pull-in cannot approve physical bias, and linear electrical pressure-port headroom cannot give maximum acoustic SPL. The 2026 photoelectric-servo preprint SC11 and MEMS distortion paper SC12 are mechanism/fixture evidence only. Their noise/distortion outcomes are not assigned to Meridian.

## Findings that survive the finite scenarios

The corrected frozen batch tests **14 shared scenarios × 4 candidates = 56 DC/AC sets**, 42 conditional JFET noise jobs and 6 nominal refinement jobs. It preserves an initial batch whose tiny-value math checks used an unsuitable default absolute tolerance; the corrected zero-tolerance controls pass independently. Results are not pooled with comparison 001, which retains the complete earlier suites and failures. No new candidate values, devices, threshold or baseline model were edited.

| Scenario | 0017 response dB | 0019 response dB | 0023 response dB | Interpretation |
| --- | ---: | ---: | ---: | --- |
|Baseline|0.7924|0.6606|0.4721|Servo response flatter |
|Paired 45 pF/gap witness|0.8537|0.7219|0.7586|0019 reverses order against servo |
|Front100/rear45 pF witness|0.7682|0.6364|0.8010|Both fixed-bias children flatter |
|Case10/cross5 pF|0.7793|0.6475|1.2766|Servo fails 1 dB screen |
|Rear45/case10/cross5 pF|0.7793|0.6475|2.0843|Strong capsule-only reversal |
|Leakage1 GΩ|22.9314|22.8042|18.4591|All fail; no selection follows |

Across all 14 cases, 0019 is flatter than lower-count 0017; 0017 retains its passive-count tradeoff. With unchanged leakage, fixed-bias simulated polarization stays 26.100 V versus servo 22.546 V; C/S changes do not change DC in this model. At 1 GΩ these fall to 12.783/9.249 V. These are operating-point calculations, never safe-use ratings.

Conditional unweighted electronics noise is lower for the fixed-bias children in all 12 non-1GΩ cases. At baseline, 0019/0023 give 0.310/1.052 mPa RMS; at 1 GΩ they give 18.706/17.295 mPa and the order reverses while response fails. The combined leaky witness also reverses noise order. There is no universal noise winner over the retained envelope, and semiconductor/excess/acoustic spectra remain incomplete. The tiny 0017/0019 noise differences are below the refinement scale and receive no separate noise rank. Common sensitivity scaling leaves normalized response unchanged and does not reverse electronics noise order at fixed C/leakage.

0012 remains a failed BJT charge control in every case (17.438–23.153 dB response deviation). Its finite-loop/current-reset limitations cannot be repaired by assuming favorable capsule sensitivity. CMOS guard/reset and carrier results remain on their existing integration/periodic-noise prerequisite tracks: no nominal ideal replacements earn performance credit. As an analytic bridge diagnostic, opposed45/100 pF cells give static imbalance magnitude 55/145=0.3793 before fixture capacitance; shared C scaling alone preserves that ratio. Both mechanical sign/correlation and electrode isolation must be known before assuming carrier cancellation.

## Identifiability and deferred measurement handoff

The [handoff](../../measurement/priority-plan.md) now explicitly treats measurements as deferred because the owner has no access. Highest-value future evidence is: applicable lead/isolation and safe DC/RF conditions; complex front/rear/case/cross admittance with fixture corrections; leakage I–V/time/RH and excess-current PSD; calibrated transfer at an approved actual bias; damping/acoustic transfer and noise with the intended headbasket.

Rear C and case/cross terms identify the response reversal region; leakage identifies whether either JFET operating point is viable. Calibrated sensitivity enables pressure-referred electronics comparisons, but cannot identify intrinsic noise without a receiver/background separation. Capacitance by itself cannot identify gap/tension/damping or approved bias. Carrier balance needs actual electrode topology, phase/pressure coupling and excitation-safe conditions; CMOS/BJT reset needs measured current and recovery plus validated electronics. The existing P0–P5 gates and original measurement schema remain mandatory.

## Preservation and limits

Public sources were searched through 33 exact query strings and followed through manufacturer documents, a thesis, original papers, patent publications and citation chains. The finite search is not exhaustive. The [retrieval records](retrieval-001-part-1.json) and [second batch](retrieval-001-part-2.json) and [material bulletin receipt](retrieval-001-part-3.json) preserve 26 acquired originals plus the failed archive request (HTTP429). Initial sandbox DNS failures and browser-provider open errors remain recorded. The blocked public archive supplies no historical revision bytes; current manufacturing lineage and calibrated batch identity remain unresolved. No access controls were bypassed or account/contact/purchase/publication action taken.

Original third-party bytes/notices stay in ignored private storage with hashes and reproducible URLs; no redistribution permission is inferred. Job decks/logs/frozen authored sources, finite failures, tables, plots and inventories are repository evidence. Passing repository/lab checks does not replace missing physical data or establish procurement/patent qualification. The original waveforms/vendor bytes and private source originals are still required for affected reproduction; GitHub covers committed files only.
