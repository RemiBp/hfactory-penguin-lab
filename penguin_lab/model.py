"""A fixed holdout experiment, with preprocessing fitted only on training data."""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]
CATEGORICAL_FEATURES = ["species", "sex", "island"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "body_mass_g"


def build_pipeline():
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocessing = ColumnTransformer(
        [
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline([("preprocess", preprocessing), ("regression", Ridge(alpha=1.0))])


def evaluate_model(frame):
    """Hold out 25% of labelled rows, stratified by species, with seed 42.

    Explorer filters never change this experiment. Hyperparameters are fixed
    beforehand; no test-set tuning is performed. Missing targets are excluded.
    """
    labelled = frame.dropna(subset=[TARGET]).copy()
    if len(labelled) < 20 or labelled["species"].value_counts().min() < 4:
        raise ValueError("At least 20 labelled rows and 4 per species are required")
    train, test = train_test_split(
        labelled, test_size=0.25, random_state=42, stratify=labelled["species"]
    )
    model = build_pipeline()
    model.fit(train[FEATURES], train[TARGET])
    prediction = model.predict(test[FEATURES])
    baseline = DummyRegressor(strategy="mean").fit(train[FEATURES], train[TARGET])
    baseline_prediction = baseline.predict(test[FEATURES])
    comparison = pd.DataFrame(
        {
            "Measured mass (g)": test[TARGET],
            "Predicted mass (g)": prediction,
            "Species": test["species"],
        }
    )
    return {
        "model": model,
        "mae": float(mean_absolute_error(test[TARGET], prediction)),
        "baseline_mae": float(mean_absolute_error(test[TARGET], baseline_prediction)),
        "r2": float(r2_score(test[TARGET], prediction)),
        "n_train": len(train),
        "n_test": len(test),
        "n_excluded": len(frame) - len(labelled),
        "train_indices": tuple(train.index),
        "test_indices": tuple(test.index),
        "predictions": comparison,
    }
