import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from xgboost import XGBClassifier


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(REPO_ROOT, "data", "credit_risk_dataset.csv")
ARTIFACTS_DIR = os.path.join(REPO_ROOT, "artifacts")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def normalize_binary_target(y: pd.Series) -> pd.Series:
    y = y.copy()

    if pd.api.types.is_numeric_dtype(y):
        uniq = set(pd.Series(y.dropna().unique()).tolist())
        if uniq.issubset({0, 1}):
            return y.astype(int)

    s = y.astype(str).str.strip().str.lower()
    mapping = {
        "1": 1, "0": 0,
        "true": 1, "false": 0,
        "yes": 1, "no": 0,
        "default": 1, "no_default": 0,
    }
    mapped = s.map(mapping)

    if mapped.isna().all():
        uniq = s.dropna().unique()
        if len(uniq) == 2:
            counts = s.value_counts()
            zero_label = counts.index[0]
            one_label = counts.index[1]
            return s.map({zero_label: 0, one_label: 1}).astype(int)

    return mapped.astype("Int64")


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in X.columns if c not in numeric_cols]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ],
        remainder="drop"
    )


def metrics_dict(y_true, y_pred, y_proba) -> dict:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = df.replace({"?": np.nan, "": np.nan, " ": np.nan})

    # Target
    target_col = "loan_status" if "loan_status" in df.columns else df.columns[-1]

    y_raw = df[target_col]
    X_raw = df.drop(columns=[target_col])

    y = normalize_binary_target(y_raw)
    if y.isna().any():
        keep = ~y.isna()
        X_raw = X_raw.loc[keep].copy()
        y = y.loc[keep].astype(int)
    else:
        y = y.astype(int)

    # Train/Val/Test split = 70/15/15
    X_train, X_temp, y_train, y_temp = train_test_split(
        X_raw, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    preprocessor = build_preprocessor(X_train)

    model = XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss"
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    pipeline.fit(X_train, y_train)

    # Validate
    val_pred = pipeline.predict(X_val)
    val_proba = pipeline.predict_proba(X_val)[:, 1]
    val_metrics = metrics_dict(y_val, val_pred, val_proba)

    # Test
    test_pred = pipeline.predict(X_test)
    test_proba = pipeline.predict_proba(X_test)[:, 1]
    test_metrics = metrics_dict(y_test, test_pred, test_proba)

    metrics = {
        "target_col": str(target_col),
        "splits": {
            "train_rows": int(len(X_train)),
            "val_rows": int(len(X_val)),
            "test_rows": int(len(X_test)),
        },
        "val": val_metrics,
        "test": test_metrics,
    }

    with open(os.path.join(ARTIFACTS_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    joblib.dump(pipeline, os.path.join(ARTIFACTS_DIR, "model.pkl"))

    print("Step 3 (new dataset) complete.")
    print("Validation metrics:", json.dumps(val_metrics, indent=2))
    print("Test metrics:", json.dumps(test_metrics, indent=2))
    print(f"- Saved: {os.path.join(ARTIFACTS_DIR, 'model.pkl')}")
    print(f"- Saved: {os.path.join(ARTIFACTS_DIR, 'metrics.json')}")


if __name__ == "__main__":
    main()
