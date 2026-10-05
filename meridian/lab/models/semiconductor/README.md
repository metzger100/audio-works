# Device evidence gate

No production semiconductor models have been accepted yet. Generic simulator models cannot establish production yield. Before a benchmark becomes qualified, record manufacturer, part/grade, source URL, retrieval date, model licence/checksum, guaranteed parameter limits, noise coverage and temperature law in `registry.yaml`. Typical curves are not tolerance limits.

Corner and population files must identify bounded vs statistical uncertainty, correlation, temperature dependence and evidence. No arbitrary independent perturbation of Idss and VTO that accidentally changes gm without documenting it. Coupled JFET level-1 beta can be calculated from Idss/VTO² as an approximation, then checked against measured/datasheet behavior. Op-amp macro models often omit current noise, 1/f noise, overload, bias current or protection; absent behavior is an unknown, not zero.

The harness accepts candidate-specific `device_corners` and `population` definitions. Empty definitions cause an incomplete qualification. No device-selection or per-unit trimming is allowed.
