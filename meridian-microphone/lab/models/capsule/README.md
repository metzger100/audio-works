# Electrical capsule realization and limits

`flat_k47.cir` is authoritative. The native-Q r1, scaled-observer r2 and series-motion r3 files preserve numerical experiments; do not substitute them without rerunning controls. The active implementation uses the scaled observer with Gear-2 integration. Its physics identities and AC/transient/timestep tests pass; this does not establish a complete capsule model or a circuit's loop stability.

For each diaphragm, `Q=C0*(1+k*p)*V`, `k=Sref/Vref`. A behavioral **voltage** source supplies `Q/Cscale`; a native capacitor `Cscale=1 nF` therefore carries `dQ/dt`. A zero-volt current probe and current-controlled source copy that current between the actual electrodes. This normalization improves numerical conditioning without changing the charge law. Pressure voltages are virtual pascal scalars referred to global zero, independently of electrical shield potential.

The linearized electronics-test mode uses `Q=C0*V-C0*k*Vpol_dc*p`. The harness obtains `Vpol_dc` from the actual loaded operating point. It reproduces first-order sensitivity while excluding hypothetical mechanical nonlinearity from electronics THD. The prescribed-motion model has no electromechanical spring/force feedback, acoustic resistance, membrane thermal noise, angular transfer, pull-in or known overload limit. Front/rear acoustic inputs are independent; electrical two-sided access alone does not establish a polar pattern.

Leakage resistors include ordinary Johnson noise only; real contamination leakage may have excess/shot noise and time dependence. All unmeasured parameters and sweep brackets live in `spec/capsule_model.yaml`. No simulator normalization voltage is a safe hardware rating.

The [derivative AC reproducer](../../research/probes/ddt_ac_reproducer/results.json) demonstrates why exit codes alone are insufficient. Native B-source `ddt` completed AC with zero signal. Some charge implementations also encountered timestep failures. Those failures remain implementation/solver evidence, not rejection of charge sensing as a physical principle.
