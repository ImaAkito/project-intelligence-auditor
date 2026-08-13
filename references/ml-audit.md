# AI / ML Audit

Apply this review when the repository contains trained models, model-serving code, training pipelines, notebooks used as part of the workflow, feature engineering, embeddings, or model evaluation.

## Data

Inspect:

- dataset provenance and license;
- train/validation/test split logic;
- patient/user/entity leakage where relevant;
- temporal leakage;
- duplicate leakage;
- class imbalance;
- missing-data handling;
- annotation protocol;
- data versioning;
- domain coverage;
- out-of-distribution exposure.

## Training

Inspect:

- architecture and baseline choice;
- reproducible configuration;
- random seeds;
- environment/dependency capture;
- checkpointing;
- experiment tracking;
- loss design;
- augmentation;
- hyperparameter search;
- early stopping;
- failure recovery;
- hardware assumptions.

## Evaluation

Inspect:

- relevance of reported metrics;
- per-class/per-subgroup performance;
- confidence intervals where meaningful;
- calibration;
- threshold selection;
- external validation;
- ablations;
- error analysis;
- robustness tests;
- comparison with credible baselines;
- evidence that metrics correspond to the current code/model version.

## Training ↔ inference consistency

Explicitly compare:

- preprocessing;
- normalization;
- resizing/resampling;
- tokenization;
- feature ordering;
- label mapping;
- postprocessing;
- thresholds;
- precision/dtype;
- expected input schema.

Any mismatch is a high-priority evidence item.

## Production ML readiness

Assess:

- model packaging;
- versioning;
- latency;
- throughput;
- CPU/GPU/NPU requirements;
- memory requirements;
- deployment portability;
- batching;
- failure handling;
- monitoring;
- drift detection;
- rollback;
- privacy/security;
- reproducibility;
- model card;
- dataset card.

Keep these distinct:

- research readiness;
- experimental validity;
- model performance;
- ML production readiness.

A high benchmark score alone does not imply production readiness.
