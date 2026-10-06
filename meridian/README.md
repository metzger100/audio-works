# M100 Meridian

Condenser-microphone research for private DIY use in Germany: acoustic instruments, accordion, ukulele, voice-over and distant male choir. Goals: low noise, accurate transients, natural detail, smooth off-axis response and restrained warmth; transparency before added distortion.

[Audio Works](../README.md) · [Current state](../CURRENT.md) · [Brief](BRIEF.md) · [Decisions](DECISIONS.md) · [Laboratory](lab/README.md)

## Status

> **Not released.** No validated build BOM, PCB fabrication package, assembly guide or physical measurements exist.

The owner specified Flat K47 Cardioid/Omni K47FRB for simulation on 2026-10-05, superseding earlier capsule-choice gates for research. Purchase, safe polarization and prototype/production selection remain unresolved.

[Model evidence](lab/research/device_model_validation.md) is partial: scoped OPA197 grounded small-signal agreement; complete production/noise, floating/nonlinear and P48 output/power coverage remains unavailable. Software tests do not qualify a microphone.

## Design goals

Balanced XLR/P48, low distortion and interference resistance are objectives. ≤7 dBA self-noise and approximately ≥135 dB SPL remain aspirational; capsule mechanics/noise/overload are unknown. The [specification](lab/spec/microphone_spec.yaml) defines research thresholds, not hardware ratings.

## Design documentation

The [capsule archive](research/reference-datasheets/README.md) retains history. The laboratory links simulations/results; the [measurement handoff](lab/measurement/README.md) defines future physical records.

Follow [components](../COMPONENTS.md), [Germany procurement](lab/research/procurement_germany.md), [patents](../PATENTS.md) and the [scientific contract](lab/CONTRACT.md). Preserve sources, assumptions, failures and decisions. Use reading routes and the [completion gate](../CONTRIBUTING.md#complete-a-change); read additional evidence needed for correctness.

[Build conventions](../CONTRIBUTING.md#documenting-a-hardware-project) describe future releases. [License](../LICENSE): hardware/design documentation CERN-OHL-S-2.0; software/general material GPL-3.0-or-later; third-party terms apply.
