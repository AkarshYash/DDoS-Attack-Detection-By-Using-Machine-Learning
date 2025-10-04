# scripts/train_model.py
# Creates dummy RF, IsolationForest and scaler files needed by shieldai_final.py
import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification

print("Creating models folder...")
os.makedirs("models", exist_ok=True)

print("Generating fake dataset...")
X, y = make_classification(n_samples=2000, n_features=3, n_informative=3, n_redundant=0, random_state=42)

print("Training RandomForest...")
rf = RandomForestClassifier(n_estimators=50, random_state=42)
rf.fit(X, y)

print("Training IsolationForest...")
iso = IsolationForest(contamination=0.01, random_state=42)
iso.fit(X)

print("Fitting scaler...")
scaler = StandardScaler()
scaler.fit(X)

print("Saving models to ./models ...")
joblib.dump(rf, os.path.join("models", "rf.joblib"))
joblib.dump(iso, os.path.join("models", "iso.joblib"))
joblib.dump(scaler, os.path.join("models", "scaler.joblib"))

print("Done. Saved rf.joblib, iso.joblib, scaler.joblib in ./models")
