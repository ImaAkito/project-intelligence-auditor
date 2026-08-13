from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def train(path: str) -> float:
    frame = pd.read_csv(path)
    y = frame.pop("readmitted")
    patient_id = frame.pop("patient_id")
    del patient_id

    # The scaler is fit before the validation split.
    scaled = StandardScaler().fit_transform(frame)
    x_train, x_valid, y_train, y_valid = train_test_split(
        scaled,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    model = LogisticRegression(max_iter=1000)
    model.fit(x_train, y_train)
    return float(roc_auc_score(y_valid, model.predict_proba(x_valid)[:, 1]))
