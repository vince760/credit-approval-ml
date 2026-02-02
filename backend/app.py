import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(REPO_ROOT, "artifacts", "model.pkl")

app = Flask(__name__)

_model = None


def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"model.pkl not found at {MODEL_PATH}. "
                "Run Step 3 training first to generate artifacts/model.pkl."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/predict")
def predict():
    model = load_model()

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Expected JSON body"}), 400

    if isinstance(payload, dict) and "application" in payload and isinstance(payload["application"], dict):
        payload = payload["application"]

    if not isinstance(payload, dict) or len(payload) == 0:
        return jsonify({"error": "Provide a JSON object with feature names and values"}), 400

    # Model expects a DataFrame with column names
    X = pd.DataFrame([payload])

    try:
        proba = float(model.predict_proba(X)[:, 1][0])
        pred = int(proba >= 0.5)
    except Exception as e:
        return jsonify({"error": "Prediction failed", "details": str(e)}), 400

    return jsonify({"approved": pred, "probability": proba})


if __name__ == "__main__":
    # localhost:5000
    app.run(host="127.0.0.1", port=5000, debug=True)
