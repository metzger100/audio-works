<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Independent conversion and periodic-noise oracles

16 October 2026. [Finite plan](diverse-plan-001.yaml), [primary-source methods](diverse-source-notes-001.md). All numerical capsule quantities below are exploratory scenarios, not safe bias or measured K47FRB sensitivity. SI units throughout. Independent equations test numerical implementations; assumed noise/gain parameters are not real-device evidence.

## Charge, reset and finite gain

Use the locked small-motion law with k=Sref/Vref. At constant imposed polarization Vp, motional charge magnitude is q=C0 Vp k p and current is i=sq. A 70pF,40V,20mV/Pa-at60V scenario gives q/p=0.9333pC/Pa. The exact DUT uses its own simulated polarization; do not substitute40V into its pressure calibration.

Let vx be the summing-node voltage relative to the quiet reference, vo=−A(s)vx, Ys=Ginput+s(Cs+Cin), Yf=1/Rf+sCf (replace this by the full series/loss/insulation network for0024). KCL and conversion are

```
i = Ys vx + Yf(vx−vo)
vx = i/[Ys+(1+A)Yf]
vo/q = −s A/[Ys+(1+A)Yf]
T = A Yf/(Ys+Yf)
vo/i = −(1/Yf) T/(1+T)
```

Thus tiny electrode voltage is compatible with successful charge conversion. Evaluate vo/q and feedback charge before discussing loss. In the capacitive plateau,

```
vo/q = −A/[Cs+Cin+(1+A)Cf]
       = −1/[Cf+(Cs+Cin+Cf)/A]
```

Large A relative to noise gain, and ωRfCf≫1, are separate requirements. A(s)=A0/(1+s/ωp) makes finite GBW visible. Device capacitance, base conductance and output loading enter Ys and A, rather than disappearing in a virtual-ground assumption. For a BJT, gm=Ic/VT, rπ=β/gm, Cπ includes diffusion charge and Cµ creates bilateral feedback. With Re=1kΩ and Rc=10kΩ the degenerated gain scale is bounded near Rc/Re, before shared-tail/reference/output loading. This is not a measured A=10 for0012.

The runnable isolated oracle deliberately uses A0=10, fp=100kHz, zero output impedance, Ct=Ccapsule+2pF and no native transistor noise. Its RC pole is buffered so feedback loading does not silently change A(s). A separately solved complex KCL is compared against SPICE over1Hz–1MHz. Constant-gain reset transients have

```
τ = Rf[Ct+(1+A0)Cf]/(1+A0)
vo(t) = −A0 Rf Istep/(1+A0) × (1−exp(−t/τ))
```

Two steps form the finite pulse. These controls receive no BJT/CMOS power or noise rating.

For0012, two parallel1MΩ resistors give Rf=500kΩ, Cf=100nF, hence fc=3.183Hz. Even infinite gain yields q/Cf, about0.0007 of q/70pF; this is an intentional conversion scale, not lost charge. Available output gain/noise must be evaluated at that scale.0024 inserts100pF in series with100nF: Ceff=99.9001pF and fc≈3186Hz, retaining the same500kΩ reset. Below this corner vo≈−s q Rf times the finite-loop factor: pressure is differentiated. Lower Cf can increase high-frequency signal while worsening normalized audio response. The real child also has1.59155Ω loss and10GΩ insulation on its100pF part; retain those in quantitative replay.

DC cannot be solved by capacitor gain. At the input,

```
(vo−vf)/Rf + (vb−vf)/Rleak = IB + Iboard
```

The original0012/0024 point has IB≈1.93383µA and vo−vf≈0.966904V; capsule leakage is only≈22.31pA there. Reference/input bases differ≈0.500V: the pair is not balanced just because both parts have the same name. If the same base current were forced through100MΩ, the reset drop alone would be≈193.4V, exceeding its rail. Increasing Rf to restore LF charge conversion therefore needs independent DC current authority. A hypothetical0.5µA oracle demonstrates the demand without inventing saturation behavior for an unlimited controlled source.

Input-current PSD includes base shot noise2q_e IB, excess/flicker terms, reset4kT/Rf and any servo actuator fluctuations. Cancelling mean IB does not cancel its random shot noise. Referred to pressure,

```
Sp_current(f) = Si(f)/[(2πf C0 Vp k)^2]
```

The finite signal transimpedance also transfers input current noise, so lowering output gain does not improve this referred floor. Input voltage noise transfers through the closed-loop noise gain `(Ys+Yf)/Yf × T/(1+T)`; correlated voltage/current noise adds the appropriate complex cross term. The runner integrates hypothetical IB=0.5µA with current-flicker corners0/100Hz separately. Missing KF in the actual BJT model remains unknown, never zero. Reset resistor excess noise and temperature laws are also unqualified.

Identifiability: one closed-loop gain measurement cannot independently determine A(s), Cin, Cµ, rπ and Cf. In the plateau it constrains only `Cf+(Cs+Cin+Cf)/A`. A single tone cannot distinguish reset corner from loop rolloff or output loading. The finite Ct/Cf/Rf grid tests separability of external effects; actual parent DC/base currents and internal/output phasors constrain the diagnosis. Independent open-stage two-port extraction, bias-dependent capacitance and current/flicker spectra remain prerequisites to a real no-FET redesign. No fitted parameter set is claimed.

## CMOS translation, charge and guards

Physical terminal translation maps every node vi→vi+Δ, including V+,V−,input reference, output-load reference and local ground. For a self-contained device with equations depending on terminal differences, terminal currents and vi−vg must be invariant. KCL sums all terminal currents; supply power uses voltage differences. Translating only an input, one rail or a load is a different physical experiment.

The grounded fixture uses16V between rails and8V CM,10kΩ load to8V. Ideal load DC current is zero; actual offset causes a small current through the reference source. Measure currents through both rails, local-ground translation source and reference source. An internally ground-referenced macro can exchange current with global0: a terminal model then has an implicit extra port. A nonzero translation-source current is diagnostic; its magnitude alone does not identify a physical leakage law.

Grounded typical OPA1971mA gives16mW before loads/guard; two stages give about32mW. Previously observed OPA928275µA gives4.4mW for one macro. These scales do not include P48 feed/harvest loss, regulator, polarization, RF/guard dynamic current or balanced output. With two6.8kΩ P48 feeds, the ideal balanced source resistance is3.4kΩ and terminal power is `I(48−3400I)` before harvest loss; rail currents are not terminal input current. No present fixture verifies complete microphone power.

The charge fixture uses Ct70pF,Rf1GΩ,Cf100pF, reference8V. Its ideal plateau gain is−q/100pF, resetτ=0.1s,1% recovery0.4605s, and DC shift≈Rf(IB−Ileak) with sign set by current direction. At22V/1GΩ leakage,22nA would demand22V; macro fA typical values cannot solve the full retained capsule leakage envelope. Noise gain tends to1+Ct/Cf=1.7 plus real input/parasitic C. Closed-loop BW/phase requires the actual A(s), output load and compensation. Nonlinear common-mode crossover, limiting/ESD switches and rail overdrive are separate behaviors.

Unmodified OPA197 contains global0-connected C_C13/C_C14/C_C15, MID construction, VCC_B/VEE_B conversion and noise subcircuits. The header explicitly describes a ground-float IQ change to C14. Therefore global0 use is a testable dependency, not proof that all such references are defects. OPA928 has analogous behavioral subcircuits. Inspect exact failed logs and terminal-current behavior before proposing any correction; a changed internal reference would be a new macro child requiring independent validation, not a repair licensed by gauge invariance.

For a guard with vg=Hg(s)vx+eg, coupling Yg=1/Rg+sCg gives

```
Iinput = [Yother+Yg(1−Hg)]vx − Yg eg
```

Guard tracking reduces effective loading only where Hg≈1 in both phase and amplitude. It also injects driver noise through Yg. Driver isolation Riso and Cload add poles; dynamic current magnitude isω Cload Vguard. A guard cannot cancel leakage through the capsule's biased air gap. In a charge input, the quiet reference is often the appropriate guard target; following the amplified inverted output changes the feedback mechanism.

The ideal positive-feedback oracle uses Ct72pF,Cg100pF,Rb1GΩ,Hg=g/(1+s/ωg),fg10kHz. Its characteristic polynomial is

```
(Ct+Cg)s²/ωg + [Ct+Cg(1−g)+1/(Rbωg)]s + 1/Rb
```

For g=0/.99/2 calculate both roots independently. The adverse gain2 case can have RHP roots although its AC equations converge. This demonstrates why tracking, capacitive loading and parasitic feedback need separate tests. It is not an actual CMOS instability or a general guard stability proof.

## Bridge sidebands and demodulation

The retained island drives capsule and reference with opposite±Vc carriers. Neglecting its explicitly near-zero parasitics,

```
vf_rf = Vc (C−Cr)/(C+Cr) sin(ωc t)
C=C0(1+kp),  d[(C−Cr)/(C+Cr)]/dp=2 C0 Cr k/(C0+Cr)²
δ(vf−vrear) = B p sin(ωc t), B=2 Vc C0 Cr k/(C0+Cr)²
```

For p=Psin(ωa t), each sideband peak is BP/2. Multiply by2sin(ωc t): desired audio is BP, plus2fc images; filter with H(jωa). With Vc0.2V,C070pF,Cr100pF,k=.02/60, each sideband is16.1476µV/Pa peak; recovered1kHz peak≈27.34µV/Pa after1kΩ/100nF. Direct audio caused by DC polarization creates additional mixer images and belongs in the fitting basis. The integrated0013 two-stage passive ladder has loading; it is not the isolated single-RC transfer.

The older carrier protocol's printed sideband formula includes an extra `/2` for this anti-phase fixture. That formula applies to a single driven capacitor with AC-grounded reference. The retained executable used the correct anti-phase expression. This dated equation clarification preserves original bytes and does not change the2%/0.5% control screens.

## Analytically calculable stochastic example

Use an explicitly ideal bridge `n=n1−n2`, equal arm varianceσ², cross-correlationρ=.6, so σd²=2(1−ρ)σ². Source1 and source2 share a Gaussian stream; the second independent stream supplies the remaining variance. With m=2cos(ωc t), stationary two-sided source spectrum S2 gives

```
Sout,2(f)=|H(f)|² [Sd,2(f−fc)+Sd,2(f+fc)]
Sd,2 = S11+S22−2 Re S12
```

Both images must be included. Fully identical arms cancel exactly; statistically independent draws cannot represent this zero control. With genuinely periodic/cyclostationary sources, off-diagonal sideband spectral covariance adds coherent cross terms. Treating those terms as independent loses cancellation or enhancement. This example validates only its declared stationary arm sources and imposed periodic mixer.

The explicit discrete method uses fs800k/1.6MHz,fc100kHz, RCτ100µs and exact held-input recursion `y[j]=a y[j−1]+(1−a)m[j]n[j]`, a=exp(−1/fsτ). White source one-sided PSD S0=1e−16V²/Hz hasσ²=S0 fs/2. A colored AR(1) source has pole r=exp(−2π10k/fs),σ²=S0 fs/2×(1−r)/(1+r), calibrated to S0 at DC; it is Lorentzian-like, explicitly **not** a device1/f model.

For covariance `Rn[l]=σd² r^|l|`, time-average `m[j]m[j−l]=2cos(ωl)` gives an independent infinite-series oracle

```
E[y²] = 2 σd² (1−a)/(1+a)
        × [1−(ar)²]/[1−2ar cos(2πfc/fs)+(ar)²]
```

A separate shifted-spectrum quadrature and Parseval check test normalization/folding. Carrier-off equivalence sets m=1: `E[y²]=σd²(1−a)/(1+a)×(1+ar)/(1−ar)`. White continuous limit is differential one-sided PSD times mixer gain2 and RC ENBW1/(4τ). No pressure or acoustic noise is assigned to these source amplitudes.

Raw seeded arrays retain burn-in20τ, source streams, mixer/output/carrier-off, Hann/boxcar PSDs, seed, sample count/rate and window ENBW. Four independent seeds give a Student-t interval for mean total power; adjacent LPTV spectral bins are correlated, so a naive per-bin chi-square interval is not claimed exact. Compare N131072/262144, both sample rates and windows. Discrete spectra are periodic in fs: the shifted-spectrum oracle includes their image/alias structure. They are not a physical analog anti-alias filter; missing above-Nyquist device noise is not assumed absent.

Actual0013 still needs periodically biased transistor spectra/covariances, oscillator AM/PM/clock jitter, physical bridge buffers/mixer/output, RF loading and power. Carrier voltage adds mean-square excitation and force; Vdc²+Vc²/2 and cross-frequency forces require real capsule mechanics/safety evidence. Neither an ideal source's zero modeled consumption nor stationary `.noise` rates that architecture.

For dynamic-power bookkeeping, a declared capacitive load requires Ipk=2πfc Cload Vpk even if an ideal source reports no P48 consumption. A diagnostic100pF load at100kHz,0.2V peak requires12.57µA peak displacement current. A dissipative full charge/discharge cycle of0.4V swing has scale Cload(ΔV)²fc=1.6µW; an ideal lossless sinusoidal capacitor has zero mean real power but nonzero reactive current. Neither is total oscillator/buffer/mixer power. Real topology, switch edge count, transistor bias, resistance, recovery and output drive determine that budget. These illustrative load values do not replace the actual bridge capacitance matrix.

PSD-resolution limit: the16384-point segments have bin spacing48.828125Hz/97.65625Hz at the two sample rates and Hann ENBW73.2421875Hz/146.484375Hz. The recorded band integrals begin at the first selected bin above20Hz and end below20kHz; they do not include exact band edges or demonstrate20Hz resolution. The validated total mean-square/covariance test is separate. A future audio-band estimator requires longer segments/records, exact edge treatment and adequate independent low-frequency averages; no native architecture noise rating follows from these short PSD segments.
