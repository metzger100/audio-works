# Mechanism transfer, not circuit copying

These are research hypotheses. Performance belongs to simulation and measurements. Source IDs resolve in [sources.yaml](../sources.yaml).

| Domain | Physical problem and mechanism | Capsule analogy | Fast falsification |
|---|---|---|---|
| Electrometers / electrostatic and low-current sensors | Surface leakage corrupts a tiny high-impedance signal; driven guard and low-bias input (S06). | Capsule charge can be lost through mounting/input leakage. | Include guard capacitance, finite guard bandwidth and leakage at hot corners; integrate noise. |
| Piezoelectric charge amplifiers | Charge must be measured despite varying shunt capacitance; feedback C and a DC bleed (S05). | A biased condenser supplies displacement current/charge. The capsule still needs external polarization; its mechanics differ. | Noise gain, feedback-resistor noise, DC drift, input compliance and clipping. |
| Photodiodes / photomultipliers | Current at a capacitive node must become voltage with adequate noise and stability (S07). | Capsule motional current is proportional to pressure derivative. | Low-frequency response/noise of TIA; a plain resistive TIA differentiates pressure unless corrected. Photomultiplier bias and pulse statistics are not imported. |
| Scanning tunneling microscopy | Tiny current, high feedback resistance and nontrivial capacitance require a bandwidth/noise compromise (S08). | Extremely small low-frequency capsule current. | Feedback resistor noise and compensation across C/leakage. Instrumentation performance does not imply audio suitability. |
| Capacitive displacement / MEMS / bridge sensors | Floating differential excitation distinguishes variable capacitance from parasitics (S09). | Sense modulation of two accessible capsule electrode capacitances. | Carrier sidebands, electrode isolation, demodulator noise and electrostatic back-action. Actual microphone front/rear acoustic correlations remain unknown. |
| Ionization chambers / radiation detectors | Integrate small charge while keeping DC leakage from saturating an integrator; electrometer TIA applicability is documented in S06. | Separate slow leakage control from audio charge conversion. | Reset/servo artifacts, finite DC authority and P48 current. Pulse detectors are not automatically continuous-audio front ends. |
| Instrumentation amplifiers | Separate differential sensing and common-mode control; a mechanism proposal, not an assertion of a particular product topology. | Floating capsule and balanced output share a finite common-mode budget. | Sweep electrode/common-mode voltage, CMRR and input current noise; inspect all loop interactions. |

The AD7746 itself is outside the audio-rate and nominal capsule-C requirements. That eliminates a direct use of that device under this brief, not the carrier bridge family. Five scientific mechanisms seed the proposal catalogue; additional primary research is required before detailed implementation.
