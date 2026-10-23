from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "model.joblib"
METRICS_PATH = BASE_DIR / "models" / "metrics.json"
DATASET_PATH = BASE_DIR / "data" / "dataset.csv"
MAX_URL_LENGTH = 2048
PHISHING_THRESHOLD = 0.70    # probability >= this -> Phishing
SUSPICIOUS_THRESHOLD = 0.40  # between the two -> Suspicious
RANDOM_STATE = 42
