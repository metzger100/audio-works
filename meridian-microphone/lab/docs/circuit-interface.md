# Circuit and evidence interface

[Laboratory](../README.md) · [Complete scientific contract](../CONTRACT.md)

## DUT

A candidate is a plain SPICE netlist with this interface:

```spice
.subckt DUT f b rear p n g rail
* capsule front/back/rear; XLR pins 2/3; local ground; observed rail
...
.ends DUT
```

The harness supplies the capsule, pressure, phantom feeds, cable, shield resistance and AC-coupled/mismatched preamp. One virtual pressure-port volt represents one pascal independently of electrical ground. Nominal rear pressure is zero; two electrical diaphragms do not validate cardioid/omni acoustics. Carrier mechanisms need a documented backend/environment extension with equivalent interface tests.

`topology.yaml` records bounds, provenance, device populations/corners, niches, parents and hypothesis. Candidate analyses/options/spec overrides are prohibited. Ideal hypothetical amplifiers make a candidate ineligible; absent macro behavior stays unknown. No specimen selection or hidden trimming.

## Tests and limits

The suite screens DC/loaded power, 1Hz–10MHz AC, unweighted/A-weighted component noise, settled H2–H10/THD, headroom brackets, two-port output impedance, balance/common mode, startup, P48/feed/temperature/cable/preamp scenarios and three-port loading. Convergence warnings, missing vectors, truncated/nonfinite data and unsettled waveforms fail.

The assumed charge law is `Q=C0(1+k·p)V`, `k=Sref/Vref`. A native-capacitor scaled observer realizes `I=dQ/dt`; Gear-2 and timestep-refinement controls support its numerical use. Linearization at the actual simulated bias isolates electronics distortion. This does not establish safe polarization, pull-in, mechanical/acoustic noise, SPL or angular response.

Full return-ratio/Nyquist/multi-loop stability, joint semiconductor/noise populations, SOA/electrothermal behavior, all-corner nonlinear/noise qualification, all-requirement yield, RF/ESD/humidity and asymmetric hot-plug/disconnect remain incomplete. Closed-loop peaking is not stability proof; finite assumed scenarios are not production yield. Unknown checks cannot qualify a candidate.

## Provenance

Each unique run retains implementation/source/spec snapshots, parameters, rendered decks, raw data, logs, versions, hashes, seeds, failures and results. Candidate `results.json` points to the latest immutable run; it never replaces history. Early debugging runs missing source snapshots remain disclosed. Evaluators require stable shared sources; capture includes imported control/reporting modules.

[Storage](../results/README.md) separates tracked metadata from private vendor bytes/waveforms. Do not delete ignored evidence. [Specification lock](../spec/lock.yaml) is unchanged; amendments require separate evidence and a [decision](../research/memory/specification-amendments.md).

The derived archive separates cohorts by specification/suite/backend. Missing axes cannot dominate; novelty earns no performance credit. Only complete qualified evidence can populate eligible fronts/champions. The [measurement interchange](../measurement/result.schema.json) preserves matching metrics, raw/calibration provenance and uncertainty; no physical measurement exists yet.
