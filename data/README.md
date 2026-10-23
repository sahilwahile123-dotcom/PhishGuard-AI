# Dataset (not included)
No dataset is bundled and none was downloaded for you. Download one yourself and save it as `data/dataset.csv`.

Suggested public sources (check each licence):
- **PhiUSIIL Phishing URL Dataset** (UCI ML Repository, CC BY 4.0). Columns `URL`, `label`. Here label **1 = legitimate, 0 = phishing**, so train with `--phishing-value 0`.
- **Phishing Site URLs** (Kaggle). Columns `URL`, `Label` with `good`/`bad` - works with no extra flags.

Any CSV with a URL column and a label column works. Numeric labels use `--phishing-value` (default 1).
