# Medical / Healthcare Audit

Apply this review when software influences medical interpretation, clinical workflow, patient-facing decisions, physiological measurements, or healthcare data processing.

## Intended use

Determine:

- intended user;
- intended population;
- intended environment;
- input modality;
- claimed output;
- whether the output is informational, triage, decision support, or diagnostic/therapeutic;
- whether current repository claims exceed available evidence.

Never describe a research prototype as a validated medical product without evidence.

## Data and ground truth

Inspect:

- dataset provenance;
- consent/privacy constraints where documented;
- annotation protocol;
- annotator expertise;
- adjudication;
- inter-rater variability;
- patient-level splitting;
- site/scanner/device separation;
- demographic and disease coverage;
- prevalence mismatch;
- external datasets.

## Evaluation

Use task-appropriate metrics. Examples include:

- sensitivity;
- specificity;
- PPV/NPV;
- ROC-AUC;
- PR-AUC;
- Dice/IoU for segmentation;
- calibration;
- clinically meaningful operating points;
- subgroup performance;
- failure analysis.

Do not accept aggregate accuracy as sufficient when clinical errors are asymmetric.

## Generalization

Inspect evidence for:

- external validation;
- cross-site validation;
- scanner/device/domain shift;
- protocol variation;
- acquisition quality variation;
- uncommon/edge cases;
- OOD behavior.

## Safety and auditability

Assess:

- explainability appropriate to the task;
- traceable model/data version;
- logging and audit trail;
- human override/review;
- failure states;
- uncertainty handling;
- unsafe defaults;
- privacy exposure;
- security of medical data;
- rollback.

## Regulatory implications

Identify regulatory implications as a risk/gap, not as legal certification advice. Record what cannot be verified. Separate:

- research readiness;
- clinical evidence readiness;
- operational readiness;
- regulatory readiness;
- commercial readiness.
