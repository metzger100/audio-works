# Physical measurement handoff

Measurement adapters must emit the same check names, metric units and four states (`pass`, `fail`, `error`, `incomplete`) as simulation. Retain raw instrument records, serial/batch IDs, fixture calibration, uncertainty, bandwidth/weighting, ambient temperature/humidity, bias, P48/loading, instrument/software versions and checksums. `result.schema.json` is the interchange contract.

Measurements can be compared to simulations only at corresponding stimulus and configuration. Never pool different backends into one asserted manufacturing yield. Add measured capsule/device parameters through a separately versioned model change and rerun controls/regressions. Keep original measurements and simulation records.

Future adapters: calibrated acoustic pressure/angle, low-noise analyzer FFT, stepped THD/headroom, impedance injection, leakage and capacitance. No instrument connection or prototype is currently assumed.
