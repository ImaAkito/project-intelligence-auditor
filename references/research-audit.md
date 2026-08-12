# Research Audit Reference

Use this reference when the repository supports a scientific or research claim.

## Separate engineering and scientific readiness

A technically polished pipeline may still have weak scientific validity.

Score or discuss separately:

- engineering completion;
- experimental validity;
- reproducibility;
- research readiness;
- publication readiness.

## Research question

Recover:

- hypothesis or research question;
- claimed novelty;
- target population/domain;
- dependent and independent variables;
- primary endpoint/metric;
- baseline or comparison method.

If these are not explicit, mark the scientific scope as ambiguous.

## Experimental design

Review:

- train/validation/test or experimental splits;
- independence of observations;
- leakage;
- randomization;
- controls;
- confounders;
- sample-size rationale;
- repeated runs/seeds;
- statistical tests;
- multiple-comparison handling;
- uncertainty intervals;
- missing-data policy;
- exclusion criteria.

## Baselines and ablations

Strong claims generally need a meaningful baseline, strongest practical comparator where feasible, ablation of claimed novel components, and sensitivity analysis for major hyperparameters or assumptions.

A result without a baseline should not receive strong evidence for superiority.

## Reproducibility

Inspect:

- locked dependencies;
- environment specification;
- deterministic/random seed handling;
- data acquisition instructions;
- preprocessing;
- experiment configuration;
- model/checkpoint versioning;
- result-generation scripts;
- hardware/runtime requirements.

Distinguish code availability, local experiment reproducibility, and independent result reproducibility.

## External validity

Review whether conclusions generalize beyond the development data/environment: external datasets or institutions, different hardware/scanners/devices, temporal validation, prospective evaluation, or unseen operating conditions.

Do not equate a held-out internal set with external validation.

## Publication readiness

Potential blockers include unclear hypotheses, weak baselines, leakage, insufficient statistical analysis, no ablation for novelty claims, irreproducible preprocessing, no error analysis, unsupported causal wording, or conclusions broader than the data.

## Output

Record:

- strongest supported scientific claim;
- strongest unsupported or overextended claim;
- missing experiment with highest information value;
- reproducibility blockers;
- publication blockers;
- next experiment that most reduces uncertainty.
