# Run log

The dated run logs live next to the outputs they describe:

- [`results/run_log.md`](results/run_log.md) — confirmatory analyses (primary pipeline,
  descriptives, PCA, learning curve, age sensitivity, classifier comparison, model export)
- [`explore/run_log.md`](explore/run_log.md) — exploratory hearing-impairment analyses

Each entry records the date, script, seed, a sha256 prefix of the input data, the
model and cross-validation parameters, package versions, compute resource, and the
headline results. `results/run_info.json` holds the latest primary run in
machine-readable form.

All random operations use seed 42.
