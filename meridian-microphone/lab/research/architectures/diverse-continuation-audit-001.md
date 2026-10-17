<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Prompt 10 continuation audit — 16 October 2026

The requested [diverse prerequisite report](diverse-prerequisites-001.md), [finite plans](diverse-plan-001.yaml), [independent derivations](diverse-derivations-001.md), controls, raw failures and source-linked matrix already exist in commit `b4741414`. This continuation audits that completed evidence as required by the [execution contract](../prompts/research-workflow.md). It does not spend another simulator or optimizer reservation. The primary JFET investigation and all 14 family niches remain open; no structural child or performance rating is promoted.

The audit corrects one active documentation error: the printed carrier sideband formula still contained an extra factor of one half. The existing executable, independent regression and later derivation were already consistent. Frozen source snapshots, models, netlists, earlier results and the original protocol copies remain intact.

[Machine audit](diverse-continuation-audit-001.json) · [refreshed primary-source observations](diverse-audit-sources-001.json) · [original extensive research/citation ledger](diverse-sources-001.json) · [completion validation](../../../../docs/validation/2026-10-16-diverse-continuation.md).

## Independent equation check

For one capacitive bridge with opposite carrier drives, charge balance gives the carrier coefficient `F(C)=(C−Cr)/(C+Cr)`. With `C=C0(1+kp)`, differentiation gives `dF/dp=2 C0 Cr k/(C0+Cr)^2`. Multiplication by pressure `P cos(ωa t)` produces two sidebands, each with peak

```
Vsb = Vc C0 Cr k P / (C0+Cr)^2.
```

The modulation factor 2 and product-to-sum factor one half cancel. A single driven electrode with the other reference at AC ground has coefficient `C/(C+Cr)` and half this derivative. Those are different boundary conditions. At the existing ideal-control values C0=70pF, Cr=100pF, Vc=0.2V, k=0.020/60Pa⁻¹ and P=1Pa peak, each anti-phase sideband is 16.1476µV peak. Ideal synchronous multiplication by `2sin(ωc t)` yields twice that audio peak before the existing RC filter. These are mathematical fixture quantities, not measured capsule sensitivity or safe RF excitation.

The [active carrier protocol](carrier-protocol.md) now states the anti-phase result and retains a dated correction. The original [charge-conservation regression](../../tests/test_architectures.py) and [island control](../../tools/controls/diverse_carrier.py) use the same value independently of the old prose. The 2% analytical and 0.5% timestep screens are unchanged. Integrated 0013 remains a failed physical-integration prerequisite cohort, separate from the successful ideal mechanism control.

## Evidence and deliverable audit

| Required scope | Retained result and boundary |
| --- | --- |
| All families and concepts | 14 families, 22 concepts, all nine physical questions, independent oracles, dependencies, source links, finite tasks and stop conditions. No concepts deleted or assigned invented performance. The 20/10/5 periodic requirements remain unchanged; this is not a periodic challenge. |
| Exact parents and Prompts 6–9 | Current device/capsule evidence, comparison 001, 0012/0024, 0010/0014, 0013 and 0019/0023/0025 are linked from the original audit. Candidate circuits, model identities and specification bytes are checked against frozen inputs. |
| BJT charge/reset | 12 finite-gain complex-KCL controls, two reset pulses, two ideal DC-demand controls and two exact-parent diagnostics remain. Recomputed parent input-KCL residuals are 9.43e−13 and 2.84e−14. Tiny input voltage is not called lost charge. Smaller feedback capacitance retains the original reset impedance and moves its corner into audio. Real base/flicker/actuator noise and DC authority remain prerequisites to a standard-parts child. |
| CMOS floating/guard/charge | Both actual macros, all-rail/reference/load translation and supply/ground currents remain; successful isolated cases and failed grounded/translated charge/reset jobs are retained separately. A model failure does not reject a family. No vendor internal edits or ideal-source CMOS noise/power credit. |
| Carrier deterministic and noise | 53 original simulator attempts include 15 retained execution errors across all tracks; 32 additional seeded ideal LPTV records retain source arrays, seeds, covariance, windows, sampling/settling refinements and confidence. Recovery/zero/off controls pass their local oracle. No stationary `.noise`, short PSD segment or ideal power source receives a native periodic microphone rating. |
| Parts and claims | ADA4530-1ARZ and S5973-01 remain unqualified leads with precise acquisition/behavior gaps. No new real implementation/BOM is declared. Claim-feature alternatives stay separate from technical merit; current territorial/status screening remains unresolved. |

The rebuilt existing analysis verifies all 1,033 primary/successor inventory entries and reproduces the retained deterministic-carrier pass. The source/preflight inventory is checked separately. Full original-evidence verification still reports the same 89 historical missing snapshots, with no damaged or uninventoried bytes; a passing repository gate cannot recover them. Fresh regression records and their inventory belong to this validation, not to the 53 earlier prerequisite attempts.

## Source cross-check and next falsifications

[TI SLOA033A §3.2](https://www.ti.com/lit/an/sloa033a/sloa033a.pdf) supports charge balance and a separate reset path; its ideal approximation and piezoelectric system figures do not validate Meridian. [OPA928 Rev A §§5.6, 7.1.2–3](https://www.ti.com/lit/ds/symlink/opa928.pdf) separates midpoint amplifier/noise conditions, guard loading and near-rail limitations. A completed 15.9V common-mode AC case cannot inherit 8V noise/guard specifications. The existing midpoint charge failures remain unsupported rather than replaced by favorable near-rail results.

The [ngspice47 manual](https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf) documents seeded injection and experimental PSS; [release47 news](https://ngspice.sourceforge.io/news.html) also mentions a PSS update. The manual's old availability wording does not prove absence of an executable feature, and neither document establishes validated periodically biased transistor noise for this circuit. The missing prerequisite remains periodic source spectra and sideband covariance, or independently calibrated seeded physical-device sources, under the existing protocol. [Phillips/Kundert's manuscript](https://designers-guide.org/theory/cyclo-paper.pdf) supports keeping folding and periodic source statistics explicit. No backend was newly installed or rated in this audit.

The [matrix](diverse-knowledge-001.json) retains the distinct finite next task for every family. The three track stop rules remain:

1. **BJT:** obtain intended-bias two-port/capacitance and base-current spectra; test the two declared reset-actuator endpoints. Reject that actuator hypothesis if it lacks DC authority or exceeds the conditional LF noise budget. Keep other no-FET conversions distinct.
2. **CMOS:** validate the unchanged macro's grounded charge fixture in its documented reference backend before complete terminal translation; then measure loaded guard return behavior and reset settling. Solver success alone cannot validate nonlinear or noise behavior.
3. **Carrier:** validate the calculable correlated-noise bridge in a supported periodic backend or documented seeded circuit-injection method before substituting real oscillator/buffer/mixer/output sources. Reject an implementation that fails folding/calibration, dynamic supply/load accounting or capsule RF prerequisites.

The JFET next task remains bilateral loop/leakage authority at the retained failed endpoints. No comparison is upgraded while prerequisite coverage differs. Procurement, patent and physical gates are unchanged; no purchase, contact, licence acceptance, commit, push or external publication is performed in this continuation.
