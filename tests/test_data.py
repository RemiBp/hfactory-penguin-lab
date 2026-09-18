from io import StringIO

import pandas as pd
import pytest

from penguin_lab.data import complete_measurements, filter_penguins, load_penguins


@pytest.fixture
def frame():
    return load_penguins()


def test_official_snapshot_shape_and_missingness(frame):
    assert frame.shape == (344, 8)
    assert frame.species.nunique() == 3
    assert frame.body_mass_g.isna().sum() == 2
    assert frame.sex.isna().sum() == 11


def test_missing_columns():
    with pytest.raises(ValueError, match="Missing columns"):
        load_penguins(StringIO("species\nAdelie\n"))


@pytest.mark.parametrize(
    "column,value,message",
    [
        ("body_mass_g", "broken", "Invalid numeric"),
        ("body_mass_g", "inf", "Non-finite"),
        ("flipper_length_mm", -1, "Non-positive"),
        ("year", 2007.5, "integer"),
        ("year", None, "integer"),
        ("species", "Unknown", "Unknown species"),
        ("island", "Atlantis", "Unknown island"),
        ("sex", "unknown", "Unknown sex"),
        ("species", None, "must be present"),
    ],
)
def test_bad_csv_rejected(frame, column, value, message):
    modified = frame.head(3).astype(object)
    modified.loc[0, column] = value
    with pytest.raises(ValueError, match=message):
        load_penguins(StringIO(modified.to_csv(index=False)))


def test_duplicate_and_empty_csv_rejected(frame):
    duplicate = pd.concat([frame.head(1), frame.head(1)])
    with pytest.raises(ValueError, match="duplicate"):
        load_penguins(StringIO(duplicate.to_csv(index=False)))
    with pytest.raises(ValueError, match="no observations"):
        load_penguins(StringIO(frame.head(0).to_csv(index=False)))


def test_filters_intersect_and_preserve_input(frame):
    before = frame.copy(deep=True)
    result = filter_penguins(frame, ["Adelie"], ["Dream"], [2007])
    assert not result.empty
    assert set(result.species) == {"Adelie"}
    assert set(result.island) == {"Dream"}
    assert set(result.year) == {2007}
    result.loc[:, "body_mass_g"] = 0
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize(
    "kwargs", [{"species": []}, {"islands": []}, {"years": []}, {"species": ["Unknown"]}]
)
def test_empty_selection_is_empty(frame, kwargs):
    assert filter_penguins(frame, **kwargs).empty


def test_no_filter_returns_copy(frame):
    result = filter_penguins(frame)
    pd.testing.assert_frame_equal(result, frame)
    assert result is not frame


def test_plot_drops_only_missing_pairs(frame):
    pairs = complete_measurements(frame)
    assert len(pairs) == 342
    assert not pairs[["flipper_length_mm", "body_mass_g"]].isna().any().any()
    assert pairs.sex.isna().any()
