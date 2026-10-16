<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Diverse behavior coverage

| Behavior | Observed scope | Missing prerequisite |
| --- | --- | --- |
|BJT finite charge conversion|12 ideal KCL controls pass|Actual open-stage two-port/capacitance population|
|BJT reset authority|2 ideal reset controls; exact parents replay and KCL|Real actuator and measured base/flicker noise; full no-selection envelope|
|CMOS floating reference|OPA197 -20V local pass; +20V fails both; OPA928 -20V fails|Full translation/nonlinear validity; no internal rewrite|
|CMOS guard|Grounded OPA928 two-stage AC/load diagnostic|CMOS noise, complete loops, translation and P48 loading|
|CMOS charge/reset|Both grounded/translated charge fixtures unsupported; reset unsupported|Grounded charge macro validation precedes structural child|
|Carrier deterministic|Recovery/zero/off/refinement controls pass after retained timeout|Integrated P48 demodulation, RF safety and real hardware|
|Carrier ideal stochastic|32 seeded LPTV cells; covariance/PSD/Parseval and source calibration|Native periodically biased device spectra/cross correlations/oscillator AM-PM|
|Realized hardware and qualification|No new implementation/BOM or qualified front|Complete applicable suite after actual structural realization; procurement/patents/physical gates|
