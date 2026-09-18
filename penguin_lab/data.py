"""Validated CSV import and filters with explicit empty-selection semantics."""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "penguins.csv"
NUMERIC = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
REQUIRED = ["species", "island", *NUMERIC, "sex", "year"]
CATEGORIES = {
    "species": {"Adelie", "Chinstrap", "Gentoo"},
    "island": {"Biscoe", "Dream", "Torgersen"},
    "sex": {"male", "female"},
}


def load_penguins(source=DATA_PATH) -> pd.DataFrame:
    """Read a CSV path or file-like object, preserving genuine missing values.

    Malformed non-empty numeric values, duplicate rows and invalid categories
    are rejected rather than silently converted or counted twice.
    """
    frame = pd.read_csv(source, na_values=["NA", ""], keep_default_na=True)
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    frame = frame[REQUIRED].copy()
    if frame.empty:
        raise ValueError("The CSV contains no observations")
    if frame.duplicated().any():
        raise ValueError("The CSV contains duplicate observations")
    for column in [*NUMERIC, "year"]:
        original = frame[column]
        values = pd.to_numeric(original, errors="coerce")
        if (original.notna() & values.isna()).any():
            raise ValueError(f"Invalid numeric value in {column}")
        if ((~np.isfinite(values)) & values.notna()).any():
            raise ValueError(f"Non-finite value in {column}")
        if (values.dropna() <= 0).any():
            raise ValueError(f"Non-positive value in {column}")
        frame[column] = values
    if frame["year"].isna().any() or (frame["year"] % 1 != 0).any():
        raise ValueError("Year must be a non-missing integer")
    frame["year"] = frame["year"].astype(int)
    for column, allowed in CATEGORIES.items():
        invalid = set(frame[column].dropna()) - allowed
        if invalid:
            raise ValueError(f"Unknown {column}: {sorted(invalid)}")
    if frame[["species", "island"]].isna().any().any():
        raise ValueError("Species and island must be present")
    return frame


def filter_penguins(frame, species=None, islands=None, years=None):
    """None keeps all values; an empty list intentionally selects no rows."""
    mask = pd.Series(True, index=frame.index)
    for column, selected in (("species", species), ("island", islands), ("year", years)):
        if selected is not None:
            mask &= frame[column].isin(selected)
    return frame.loc[mask].copy()


def complete_measurements(frame):
    """Rows usable in the measured-mass scatterplot, without imputing values."""
    return frame.dropna(subset=["flipper_length_mm", "body_mass_g"]).copy()
