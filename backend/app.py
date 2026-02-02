import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(REPO_ROOT, "artifacts", "model.pkl")
FRONTEND_DIST = os.path.join(REPO_ROOT, "frontend", "out")

# Approval rule: approve if default risk below threshold
DEFAULT_APPROVAL_THRESHOLD = float(os.environ.get("APPROVAL_THRESHOLD", "0.30"))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
_model = None


def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run backend/predict.py to generate artifacts/model.pkl."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/config")
def config():
    return jsonify({"approval_threshold": DEFAULT_APPROVAL_THRESHOLD})


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

    X = pd.DataFrame([payload])

    try:
        default_prob = float(model.predict_proba(X)[:, 1][0])
    except Exception as e:
        return jsonify({"error": "Prediction failed", "details": str(e)}), 400

    approved = int(default_prob < DEFAULT_APPROVAL_THRESHOLD)

    return jsonify({
        "approved": approved,
        "default_probability": default_prob,
        "approval_threshold": DEFAULT_APPROVAL_THRESHOLD
    })


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIST, "index.html")

@app.get("/<path:path>")
def static_files(path):
    # let API routes keep working
    if path.startswith("api/") or path == "health":
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(FRONTEND_DIST, path)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
