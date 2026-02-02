import os
import json
import numpy as np
import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import mutual_info_classif


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(REPO_ROOT, "data", "credit_risk_dataset.csv")
ARTIFACTS_DIR = os.path.join(REPO_ROOT, "artifacts")
EDA_DIR = os.path.join(ARTIFACTS_DIR, "eda")

os.makedirs(EDA_DIR, exist_ok=True)


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


def column_profile(df: pd.DataFrame) -> dict:
    out = {}
    for c in df.columns:
        s = df[c]
        info = {
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "unique": int(s.nunique(dropna=True)),
            "top_values": {str(k): int(v) for k, v in s.value_counts(dropna=True).head(10).to_dict().items()},
        }
        if pd.api.types.is_numeric_dtype(s):
            info["min"] = None if s.dropna().empty else float(s.min())
            info["max"] = None if s.dropna().empty else float(s.max())
        else:
            info["min"] = None
            info["max"] = None
        out[c] = info
    return out


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = df.replace({"?": np.nan, "": np.nan, " ": np.nan})

    # Target is typically loan_status in this dataset
    if "loan_status" in df.columns:
        target_col = "loan_status"
    else:
        # fallback to last column if the file differs
        target_col = df.columns[-1]

    y_raw = df[target_col]
    X_raw = df.drop(columns=[target_col])

    y = normalize_binary_target(y_raw)
    if y.isna().any():
        keep = ~y.isna()
        X_raw = X_raw.loc[keep].copy()
        y = y.loc[keep].astype(int)
    else:
        y = y.astype(int)

    # Basic profiling
    profile = column_profile(df)

    # Identify numeric vs categorical for feature engineering plan
    numeric_cols = X_raw.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in X_raw.columns if c not in numeric_cols]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ],
        remainder="drop"
    )

    X_processed = preprocessor.fit_transform(X_raw, y)

    # Build feature names
    feature_names = []
    feature_names.extend(numeric_cols)

    if categorical_cols:
        ohe = preprocessor.named_transformers_["cat"].named_steps["onehot"]
        ohe_names = ohe.get_feature_names_out(categorical_cols).tolist()
        feature_names.extend(ohe_names)

    # Feature selection analysis (mutual information)
    mi = mutual_info_classif(X_processed, y, discrete_features=False, random_state=42)
    mi_df = pd.DataFrame({"feature": feature_names, "mutual_info": mi}).sort_values("mutual_info", ascending=False)

    overview = {
        "dataset_path": "data/credit_risk_dataset.csv",
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "target_col": str(target_col),
        "target_distribution": {str(k): int(v) for k, v in y.value_counts().sort_index().to_dict().items()},
        "missing_cells_total": int(df.isna().sum().sum()),
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "processed_feature_count": int(X_processed.shape[1]),
    }

    with open(os.path.join(EDA_DIR, "overview.json"), "w", encoding="utf-8") as f:
        json.dump(overview, f, indent=2)

    with open(os.path.join(EDA_DIR, "column_profile.json"), "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    mi_df.to_csv(os.path.join(EDA_DIR, "feature_rank_mutual_info.csv"), index=False)

    print("Step 2 (new dataset) complete.")
    print(f"- Saved: {os.path.join(EDA_DIR, 'overview.json')}")
    print(f"- Saved: {os.path.join(EDA_DIR, 'column_profile.json')}")
    print(f"- Saved: {os.path.join(EDA_DIR, 'feature_rank_mutual_info.csv')}")


if __name__ == "__main__":
    main()
