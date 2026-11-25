import csv, random
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from feature_extractor import extract_features, features_to_vector

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "Phishing_site_urls.csv"
MODEL_PATH = BASE / "model" / "gb_phishing_model.pkl"
SAMPLE = 60000

rows = []
with open(CSV_PATH, newline="", encoding="utf-8-sig", errors="ignore") as f:
    reader = csv.DictReader(f)
    cols = {c.strip().lower(): c for c in reader.fieldnames}
    url_col, label_col = cols["url"], cols["label"]
    for r in reader:
        # In this dataset 1 = legitimate, 0 = phishing -> flip it
        label = 1 if r[label_col].strip() == "0" else 0
        rows.append((r[url_col], label))

random.seed(42)
random.shuffle(rows)
rows = rows[:SAMPLE]

X, y = [], []
for url, label in rows:
    try:
        X.append(features_to_vector(extract_features(url)))
        y.append(label)
    except Exception:
        continue

X = np.array(X, dtype=float)
y = np.array(y)
print("Samples used:", len(y), "| Phishing share:", y.mean().round(2))

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
clf = GradientBoostingClassifier(n_estimators=200, random_state=42)
clf.fit(X_tr, y_tr)
print(classification_report(y_te, clf.predict(X_te)))

MODEL_PATH.parent.mkdir(exist_ok=True)
joblib.dump({"model": clf}, MODEL_PATH)
print("Saved model to", MODEL_PATH)