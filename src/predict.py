import json
import joblib, pandas as pd
from config import METRICS_PATH, MODEL_PATH, PHISHING_THRESHOLD, SUSPICIOUS_THRESHOLD
from src.feature_extraction import extract_features

class ModelNotTrained(Exception):
    pass

class Predictor:
    def __init__(self, model_path=MODEL_PATH, metrics_path=METRICS_PATH):
        self.model_path, self.metrics_path = model_path, metrics_path
        self.bundle = self.metrics = None
        self.reload()

    def reload(self):
        self.bundle = joblib.load(self.model_path) if self.model_path.exists() else None
        self.metrics = json.loads(self.metrics_path.read_text()) if self.metrics_path.exists() else None

    @property
    def ready(self):
        return self.bundle is not None

    def scan(self, url):
        feats = extract_features(url)  # raises ValueError on bad input
        if not self.ready:
            raise ModelNotTrained()
        X = pd.DataFrame([feats], columns=self.bundle["features"])
        p = float(self.bundle["model"].predict_proba(X)[0][1])
        label = "Phishing" if p >= PHISHING_THRESHOLD else "Suspicious" if p >= SUSPICIOUS_THRESHOLD else "Legitimate"
        return {"classification": label, "phishing_probability": round(p, 4),
                # shown only if the model has verified held-out metrics
                "show_confidence": self.metrics is not None, "features": feats}
