"""Train on a real dataset: python -m src.train_model --data data/dataset.csv"""
import argparse, json, sys
from datetime import datetime, timezone
import joblib, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from config import DATASET_PATH, METRICS_PATH, MODEL_PATH, RANDOM_STATE
from src.evaluate_model import compute_metrics
from src.feature_extraction import FEATURE_NAMES, extract_features

BAD, GOOD = {"bad", "phishing", "malicious", "malware", "defacement"}, {"good", "legitimate", "benign"}

def load_dataset(path, url_col=None, label_col=None, phishing_value="1"):
    df = pd.read_csv(path)
    low = {c.lower(): c for c in df.columns}
    url_col = url_col or low.get("url")
    label_col = label_col or next((low[k] for k in ("label", "type", "status", "class") if k in low), None)
    if url_col not in df.columns or label_col not in df.columns:
        raise ValueError(f"Need a URL column and a label column. Found: {list(df.columns)}. Use --url-col/--label-col.")
    df = df[[url_col, label_col]].dropna().rename(columns={url_col: "url", label_col: "label"})
    lab = df["label"].astype(str).str.strip().str.lower()
    if lab.isin(BAD | GOOD).all():
        df["y"] = lab.isin(BAD).astype(int)
    else:
        df["y"] = (lab == str(phishing_value).lower()).astype(int)
    df["url"] = df["url"].astype(str).str.strip()
    df = df.drop_duplicates(subset="url")          # a URL can never sit in both train and test
    df = df[df.groupby("url")["y"].transform("nunique") == 1]
    return df[["url", "y"]]

def build_matrix(df):
    rows, ys, skipped = [], [], 0
    for u, y in zip(df["url"], df["y"]):
        try:
            rows.append(extract_features(u)); ys.append(y)
        except ValueError:
            skipped += 1
    return pd.DataFrame(rows, columns=FEATURE_NAMES), pd.Series(ys), skipped

def train(df, model_path=MODEL_PATH, metrics_path=METRICS_PATH, dataset_name="dataset"):
    X, y, skipped = build_matrix(df)
    if y.nunique() < 2 or y.value_counts().min() < 10:
        raise ValueError("Dataset needs at least 10 examples of both classes.")
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
    model = RandomForestClassifier(n_estimators=200, class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE)
    model.fit(X_tr, y_tr)
    m = compute_metrics(y_te, model.predict(X_te))
    m.update(dataset=dataset_name, train_size=len(X_tr), test_size=len(X_te), skipped_invalid_urls=skipped,
             test_class_counts={"legitimate": int((y_te == 0).sum()), "phishing": int((y_te == 1).sum())},
             feature_importances=dict(zip(FEATURE_NAMES, map(float, model.feature_importances_))),
             trained_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    joblib.dump({"model": model, "features": FEATURE_NAMES}, model_path)
    metrics_path.write_text(json.dumps(m, indent=2))
    return m

def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--data", default=str(DATASET_PATH)); a.add_argument("--url-col"); a.add_argument("--label-col")
    a.add_argument("--phishing-value", default="1", help="label value meaning phishing when labels are numeric")
    a = a.parse_args(argv)
    try:
        m = train(load_dataset(a.data, a.url_col, a.label_col, a.phishing_value), dataset_name=a.data)
    except (FileNotFoundError, ValueError) as e:
        print(f"Cannot train: {e}\nSee data/README.md for dataset instructions."); return 1
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items() if k not in ("feature_importances",)})
    return 0

if __name__ == "__main__":
    sys.exit(main())
