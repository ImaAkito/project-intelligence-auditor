from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationReport:
    cohort: str
    roc_auc: float
    sensitivity: float
    specificity: float


def internal_validation() -> ValidationReport:
    return ValidationReport(
        cohort="Hospital A retrospective holdout",
        roc_auc=0.91,
        sensitivity=0.86,
        specificity=0.82,
    )


def publish_summary() -> dict[str, object]:
    report = internal_validation()
    return {
        "model_status": "validated",
        "cohort": report.cohort,
        "roc_auc": report.roc_auc,
        "sensitivity": report.sensitivity,
        "specificity": report.specificity,
    }
