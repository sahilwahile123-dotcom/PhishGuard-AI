"""Metrics computed from a held-out test set only."""
import json, sys
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

def compute_metrics(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {"accuracy": accuracy_score(y_true, y_pred), "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0), "f1": f1_score(y_true, y_pred, zero_division=0),
            "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]]}

if __name__ == "__main__":
    from src.train_model import main  # re-runs the same seeded split and prints metrics
    sys.exit(main(sys.argv[1:]))
