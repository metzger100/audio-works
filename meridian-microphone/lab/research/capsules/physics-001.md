<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Capsule physics controls — 11 October 2026

These are independent SI-unit derivations and hypothetical geometry witnesses, not measurements or a K47FRB mechanical model. Source IDs resolve through [sources-001.yaml](sources-001.yaml); original URLs, MIME, hashes and failed acquisitions are in the retrieval records. [Reproduction](../../tools/reporting/capsule_envelope.py) freezes the inputs and checks finite differences/quadrature before circuit analysis.

## Capacitance, compliance and charge

For an ideal parallel air capacitor with effective electrode fraction eta,

`A = pi*a^2; C = epsilon0*eta*A/d; dC/dx = C/d` for displacement x toward the electrode.

Units: `(F/m)*m^2/m = F`; `dC/dx` is F/m. Haas-Christensen [SC05](https://backend.orbit.dtu.dk/ws/files/5037185/PhD-thesis_jhc.pdf), printed p.4 (PDF p.17), equations 1–2 gives the capacitance and sensitivity magnitudes. The sign of constant-charge voltage is negative: `deltaV = -V*deltaC/C`; the repository pressure-port sign is a convention, not acoustic directionality. Its equation 3 incorrectly prints `F=P/A`; the correct force is `F=p*A` (Pa*m²=N). Its square-root resonance expression is angular frequency; divide by `2*pi` for hertz. The rendered original confirms these printing issues; they are not extraction errors.

For a uniformly tensioned circular membrane clamped only at its perimeter, ignoring mass, air reaction and electrostatics, the membrane equation gives

`x(r)/p = (a^2-r^2)/(4*T); mean(x)/p = a^2/(8*T)`.

T is tension per length in N/m, not tensile stress in Pa. Averaging follows from integrating `x(r)*2*pi*r dr / A`. [Homentcovschi/Miles SC19](https://ws2.binghamton.edu/me/MSL/PDF_Paper/2011Dec%20JASA%20Analytical_Condensor%20Mic.pdf), p.3699 equations 1–3 supplies the membrane equation and perimeter boundary; p.3702 equation 21 gives the corresponding volume compliance. Thus

`k = (mean(x)/p)/d [1/Pa]; Sref = Vref*k [V/Pa]; deltaQ/p = C*Vpol*k [C/Pa]`.

The K47 center termination, nonuniform metallization, holes, air cavities, possible central mechanical constraint and backplate motion invalidate direct use of this simple disk as the actual capsule. Perforated-electrode electrostatic area and force weighting need not be the same fraction. The derivation establishes an internally consistent *example*, not identified K47FRB gap or tension.

[RK47 SC10](https://microphone-parts.com/products/rk47-microphone-capsule) documents 27 mm diaphragm diameter and 3 µm film. Use its radius only as an analogy, with **assumed** eta=0.55. At C=70 pF and assumed Sref=20 mV/Pa, the equations imply d=39.832 µm, mean compliance=13.277 nm/Pa and T=1715.805 N/m. None is inferred from the selected capsule. The generic 40 µm patent example SC06 is numerically compatible, but supplies no same-product geometry validation.

Keeping this example's area/fraction/tension fixed yields:

| C per side | Implied gap | Sref at mathematical 60 V | Signal charge/Pa at mathematical 40 V |
| ---: | ---: | ---: | ---: |
|45 pF|61.961 µm|12.857 mV/Pa|0.386 pC/Pa|
|70 pF|39.832 µm|20.000 mV/Pa|0.933 pC/Pa|
|100 pF|27.882 µm|28.571 mV/Pa|1.905 pC/Pa|

These are paired gap scenarios within the retained envelope, with no population weights. At fixed gap/area, S scales inversely with T; 5 and 40 mV/Pa correspond to example T multipliers 4 and 0.5. This shows why independently varied C and sensitivity can be physically possible, while some chosen correlations also merit tests. In differential form, `dlogC=2*dloga+dlogeta-dlogd`, while `dlogk=2*dloga-dlogT-dlogd`. C alone cannot identify k, active area, d or T.

## Material consistency and center-constrained examples

The perimeter-only disk above is a mathematical witness, **not an established physically feasible 3 µm polyester diaphragm**. Its implied stress is `sigma=T/thickness=571.935 MPa` at the RK47 thickness analogy. DuPont Teijin's manufacturer-authored [SC25 H-37232-3 bulletin](https://stenbacka.fi/wp-content/uploads/sites/3/2016/07/mylar_a_fysikaaliset_ominaisuudet.pdf), June2003, p.1 Table1, gives industrial grade92A typical ultimate MD/TD20/24 kgf/mm² and strength at5% elongation10 kgf/mm². The conversion is `1kgf/mm²=9.80665MPa`, giving196.133/235.360MPa ultimate and98.0665MPa F5. Those grade/thickness-specific typical observations are not the selected film's allowable stress. They reject casual material equivalence of the unconstrained disk; they do not reject the assumed capsule sensitivity or prove a safe polarization.

An independently derived annular membrane, fixed at outer radius a and inner radius b, has the same low-frequency membrane equation as SC19 but different boundaries. For unit pressure,

`x(r)=[a²-r²-(a²-b²)*ln(a/r)/ln(a/b)]/(4*T)`.

This solves `T*(x''+x'/r)=-1`, with x(a)=x(b)=0. Averaging over the annulus yields `mean_x=[a²+b²-(a²-b²)/ln(a/b)]/(8*T)`. Use `C=epsilon0*eta*pi*(a²-b²)/d`. These equations are this work's derived transformation of the SC19 membrane equation, not a published K47 construction. Independent radial quadrature checks the mean with zero absolute tolerance, and endpoint/positive displacement controls check signs and units.

The separately frozen [material plan](material-controls-001.yaml) uses **assumed** inner/outer ratios0.4 and0.6, respectively6µm and3µm film analogies, the prior radius/fraction and assumed70pF/20mV/Pa. They imply (d,T,stress)=(33.459µm,496.890N/m,82.815MPa) and (25.492µm,287.200N/m,95.733MPa). Both are below that other grade's F5 typical value. This supplies positive-gap/tension, material-screened examples for paired45/70/100pF at12.857/20/28.571mV/Pa, while **actual center contact size, film grade, stress allowance, air loading and electrostatic equilibrium remain unknown**. No claim is made that these are actual capsule geometries or safe operating equilibria.

The independent5mV/Pa endpoint at the same assumed geometries requires331.260/382.933MPa, above the comparison grade's typical ultimate strength. These two failed material transfers are retained explicitly. Do not remove that adverse sensitivity coverage: its feasibility depends on unknown construction/area/constraints/damping and cannot be ruled out by grade92A. Capacitance plus sensitivity identifies combinations of geometry and compliance, never a unique mechanical unit.

## Electrode network, lead/case and correlation

The existing model has f–b and r–b capacitive branches, per-side leakage, f/r–case PAR and f–r CROSS. With b and case held at reference, its reduced capacitance matrix is

`[[CF+PAR+CROSS, -CROSS], [-CROSS, CR+PAR+CROSS]]`.

Its energy is `0.5*(CF*vf²+CR*vr²+PAR*(vf²+vr²)+CROSS*(vf-vr)²)` joules; all retained nonnegative branches produce a positive matrix. Independent eigenvalue checks cover equal/opposed C and cross endpoints. With a floating or driven backplate, use the full nodal matrix; treating the rear as a grounded added capacitor would lose its bias/servo effect. Parallel front/rear C is CF+CR only for the documented electrode connection; two equal series cells give C/2 instead. Community 120–150 pF combined estimates cannot select either connection or establish per-side tolerances.

Common construction may correlate gaps, but tension, coating and mount contamination may differ. There is no measured coefficient; perfectly paired and opposed endpoint scenarios are deterministic probes, not correlation estimates. Mechanical noise cross spectra also remain unknown. For two noise paths, use `Sout=|Hf|²*Sff+|Hr|²*Srr+2*Re(Hf*conj(Hr)*Sfr)` and enforce `|Sfr|²<=Sff*Srr`. Neither adding two independent noise powers nor assuming perfect cancellation is justified for the real capsule.

## Polarization and electrostatic boundary conditions

`S(V)=Sref*(V/60)` is the existing fixed-compliance, small-signal normalization. It cannot bound real bias dependence. In a local parallel piston approximation, constant-voltage attraction is `Fe=epsilon0*A*V²/(2*g²)` and its negative spring contribution is `Ke=epsilon0*A*V²/g³`. With mechanical stiffness Km, a local tangent sensitivity multiplier is `1/(1-lambda)` for `lambda=Ke/Km`, only where a stable equilibrium already exists. Supplementary lambda=0.1/0.3 stresses give 1.111/1.429; neither lambda nor an associated voltage is measured. Under ideal constant charge and no parasitics, `Fe=Q²/(2*epsilon0*A)` has no direct gap derivative; real finite bias impedance/strays produce frequency-dependent back-action. Static deformation and changing tension still matter.

[COMSOL SC13](https://doc.comsol.com/6.3/doc/com.comsol.help.models.aco.condenser_microphone/condenser_microphone.html), equations 1–6/Table 1/Figure 5 illustrates coupled static deformation, thermoviscous loading and differing AC/DC capacitance in a generic unperforated geometry. Its prose surface-density expression appears inverted; physically use `rho_surface=rho_bulk*thickness`. No parameters or performance from that model are assigned to K47FRB. A textbook piston pull-in value, even if solved numerically, omits actual diaphragm/mount/defect conditions and establishes no safe bias. Other-capsule DC/RF voltages and historical informal 60 V comments remain non-authorizing.

## Leakage, loss, reset and noise

For an isolated resistor R across fixed C at temperature T, `tau=R*C`, `fc=1/(2*pi*R*C)`, leakage `I=V/R` and equilibrium voltage PSD `Sv=4*kB*T*R/(1+(2*pi*f*R*C)^2)` (one-sided, V²/Hz). Integrated from f1 to f2:

`variance=2*kB*T/(pi*C)*[atan(2*pi*f2*R*C)-atan(2*pi*f1*R*C)]`.

The all-frequency integral is kBT/C. Independent log-frequency quadrature agrees with the closed form using zero absolute tolerance. [Obo et al. SC11](https://arxiv.org/pdf/2604.18969v1), p.3 equations 4–6, independently gives this RC redistribution identity. At 70 pF/298.15 K, R=1 GΩ/1 TΩ/100 TΩ gives tau=0.07/70/7000 s and 20 Hz–20 kHz node thermal RMS=2.058/0.06520/0.006520 µV. At hypothetical 40 V, leakage is 40 nA/40 pA/0.4 pA. These are isolated controls; candidate feed/servo paths change charging, noise and settling.

An ideal thermal reset of 70 pF leaves `sqrt(kBT/C)=7.668 µV` node uncertainty, or `sqrt(kBT*C)=0.537 fC` charge uncertainty. This is a reset initial condition, **not** white audio ASD or a complete CMOS noise prediction. Reset scheduling, charge injection, dielectric absorption, recovery and sampled noise require their own transfer/aliasing evidence. Base-current reset authority must exceed the actual sum of input/insulator currents without per-unit selection.

For a passive lossy capacitance, locally `Y=omega*C*tan(delta)+j*omega*C`. Its dissipative current PSD is `4*kBT*Re(Y)` under thermal equilibrium; equivalent impedance and network propagation determine voltage noise. Supplementary tan(delta)=1e-4/1e-3 values are deliberately **assumed**, not measured material bounds. Contaminated/humid leakage is not necessarily equilibrium Johnson noise. A separate hypothetical excess-current spectrum `Si=A²*(100Hz/f)` with A=1/10 fA/sqrt(Hz) at 100 Hz is a falsifiable stress, not a K47FRB noise floor; no mechanism establishes its amplitude. Deterministic leakage R does not identify that spectrum. Guarding reduces particular electric fields/leakage paths; it cannot eliminate intrinsic diaphragm dissipation or undocumented lead losses.

[Gabrielson SC08](https://zenodo.org/records/1260557/files/article.pdf), p.904 equations 3–4 gives `SF=4*kBT*Rm` and pressure PSD `Sp=4*kBT*Ra`, where `Ra=Rm/A²` has units Pa*s/m³. Actual complex acoustic impedances, transfer and area are missing; calculate each dissipative source and cross spectrum separately. Electronic, mechanical, humidity/excess and environmental terms are never a single guessed dBA value. Complete-microphone overload/distortion includes capsule, amplifier, source and calibration; no inverse extraction is permitted here. These omissions prevent absolute system noise, SPL, angle and safe-bias conclusions.
