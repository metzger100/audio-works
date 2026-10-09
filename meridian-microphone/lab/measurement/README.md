# Physical measurement handoff

[Project status](../../README.md#status) · [Laboratory](../README.md) · [Result schema](result.schema.json)

No physical measurements have been made. This document defines the future measurement records and comparison boundary.

The [prioritized measurement plan](priority_plan.md) connects capsule safety, capacitance, leakage, sensitivity and acoustic uncertainty to the tested architecture comparison. Equipment access remains unknown; existing or borrowed equipment comes first. No purchase or safe polarization is inferred.

Measurement adapters must emit the same check names, metric units and four states (`pass`, `fail`, `error`, `incomplete`) as simulation. Retain raw instrument records, serial/batch IDs, fixture calibration, uncertainty, bandwidth/weighting, ambient temperature/humidity, bias, P48/loading, instrument/software versions and checksums. `result.schema.json` is the interchange contract.

Measurements can be compared to simulations only at corresponding stimulus and configuration. Never pool different backends into one asserted manufacturing yield. Add measured capsule/device parameters through a separately versioned model change and rerun controls/regressions. Keep original measurements and simulation records.

Future adapters: calibrated acoustic pressure/angle, low-noise analyzer FFT, stepped THD/headroom, impedance injection, leakage and capacitance. No instrument connection or prototype is currently assumed.
