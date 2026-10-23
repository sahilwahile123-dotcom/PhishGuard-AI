# PhishGuard AI - AI-Based Phishing Website Detection System
A college project: a Flask web app that classifies a URL as **Legitimate**, **Suspicious** or **Phishing** using a scikit-learn Random Forest trained on URL text features. URLs are analysed as strings only; the site is never visited.

## Objectives and features
- Extract lexical URL features and train/evaluate a real ML model (no fake predictions).
- Dashboard with scanner, feature table (heuristic indicators, not verified facts), and Chart.js charts.
- REST API: `GET /api/health`, `POST /api/scan`, `GET /api/model-info`.
- Metrics (accuracy, precision, recall, F1, confusion matrix) come only from a held-out test set.

## Status: you must train the model first
This ZIP contains **no dataset and no trained model**. Until you train, the scanner shows a "Model not trained" message instead of a prediction.

## Requirements
Windows 10/11, Python 3.10+ (tick "Add Python to PATH" when installing), internet for pip and the Chart.js CDN.

## Setup (Windows Command Prompt)
```
cd PhishGuard-AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
PowerShell: activate with `venv\Scripts\Activate.ps1` (if blocked: `Set-ExecutionPolicy -Scope Process Bypass`).

## Dataset setup
Download a public dataset and save it as `data\dataset.csv` (see `data\README.md`). Example PhiUSIIL (label 1 = legitimate) command below uses `--phishing-value 0`.

## Train the model
```
python -m src.train_model --data data\dataset.csv
python -m src.train_model --data data\dataset.csv --phishing-value 0
```
(Use the second form for PhiUSIIL; the first for Kaggle good/bad files.) This removes duplicate URLs, does a stratified 80/20 split, trains, evaluates on the test part, and writes `models\model.joblib` and `models\metrics.json`.

## Run the website
```
python app.py
```
Open http://127.0.0.1:5000 in your browser. Restart is not needed after retraining the first time you open the page, but refresh it.

## Testing
```
python -m unittest discover -s tests -t .
```
Covers normal, malformed, empty, IP-based and suspicious-looking URLs, plus the API and a mechanics-only training check using made-up fixture URLs (never used for the real model).

## Files
- `app.py` Flask routes. `config.py` paths and thresholds.
- `src/feature_extraction.py` feature extraction shared by training and prediction.
- `src/train_model.py` loading, cleaning, split, training, saving. `src/evaluate_model.py` metrics. `src/predict.py` loads model, classifies.
- `templates/index.html`, `static/css/style.css`, `static/js/app.js` the interface.
- `tests/` unit and API tests.

## How classes are decided
Phishing probability >= 0.70 = Phishing; 0.40 to 0.70 = Suspicious; below 0.40 = Legitimate (change in `config.py`). The probability is shown only when `metrics.json` exists.

## Common errors
- `'python' is not recognized`: reinstall Python with PATH ticked.
- `Cannot train: ... No such file`: put the CSV at `data\dataset.csv`.
- Scanner says model not trained: run the training step, then refresh.
- Charts empty: you are offline (Chart.js loads from a CDN) or no model is trained.
- Port 5000 busy: change `port` in `app.py`.

## Limitations
Only URL text is examined (no page content, domain age or reputation). Dataset bias, false positives and false negatives are expected. A heuristic flag is a hint, not proof. HTTPS does not mean safe. Educational use only.
