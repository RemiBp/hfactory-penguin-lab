import numpy as np
import pytest

from penguin_lab.data import load_penguins
from penguin_lab.model import FEATURES, evaluate_model


@pytest.fixture(scope="module")
def result():
    return evaluate_model(load_penguins())


def test_holdout_is_disjoint_and_excludes_missing_targets(result):
    assert not set(result["train_indices"]) & set(result["test_indices"])
    assert result["n_train"] + result["n_test"] == 342
    assert result["n_excluded"] == 2
    assert "body_mass_g" not in FEATURES


def test_imputation_is_fitted_only_on_training_data(result):
    frame = load_penguins().loc[list(result["train_indices"])]
    learned = (
        result["model"]
        .named_steps["preprocess"]
        .named_transformers_["numeric"]
        .named_steps["imputer"]
        .statistics_
    )
    expected = frame[["bill_length_mm", "bill_depth_mm", "flipper_length_mm"]].median()
    np.testing.assert_allclose(learned, expected)


def test_reproducible_predictions(result):
    again = evaluate_model(load_penguins())
    assert again["test_indices"] == result["test_indices"]
    np.testing.assert_allclose(again["predictions"].iloc[:, 1], result["predictions"].iloc[:, 1])


def test_model_beats_mean_baseline_on_fixed_dataset(result):
    assert 0 < result["mae"] < result["baseline_mae"]
    assert np.isfinite(result["predictions"].iloc[:, 1]).all()


def test_insufficient_data_rejected():
    with pytest.raises(ValueError, match="At least"):
        evaluate_model(load_penguins().head(10))
