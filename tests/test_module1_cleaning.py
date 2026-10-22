"""
Standalone test for Module 1.
Run with:  pytest tests/test_module1_cleaning.py -v
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules import module1_cleaning as m1


def make_sample_df():
    return pd.DataFrame({
        "age": [25, np.nan, 30, 30, 40],
        "city": ["Delhi", "Mumbai", "Delhi", "Delhi", "Mumbai"],
        "score": [10.0, 20.0, np.nan, 20.0, 50.0],
    })


def test_missing_value_summary():
    df = make_sample_df()
    summary = m1.get_missing_value_summary(df)
    assert "age" in summary["column"].values
    age_row = summary[summary["column"] == "age"].iloc[0]
    assert age_row["missing_count"] == 1


def test_handle_missing_values_mean():
    df = make_sample_df()
    cleaned = m1.handle_missing_values(df, strategy="mean")
    assert cleaned["age"].isnull().sum() == 0
    # mean of [25, 30, 30, 40] = 31.25
    assert abs(cleaned["age"].iloc[1] - 31.25) < 0.01


def test_handle_missing_values_drop():
    df = make_sample_df()
    cleaned = m1.handle_missing_values(df, strategy="drop")
    assert cleaned.isnull().sum().sum() == 0
    assert len(cleaned) < len(df)


def test_find_and_remove_duplicates():
    df = make_sample_df()
    # rows 2 and 3 both have age=30, city="Delhi" -> row 3 is a duplicate of row 2
    dupes = m1.find_duplicates(df, subset=["age", "city"])
    assert len(dupes) >= 1

    cleaned = m1.remove_duplicates(df, subset=["age"])
    assert cleaned["age"].duplicated().sum() == 0


def test_clean_pipeline_runs_end_to_end():
    df = make_sample_df()
    # "median" only fills numeric columns by design, so use "mode" here to
    # confirm every column (including text) ends up with no missing values.
    result = m1.clean_pipeline(df, missing_strategy="mode", remove_dupes=True)
    assert result.isnull().sum().sum() == 0
    assert len(result) <= len(df)


if __name__ == "__main__":
    test_missing_value_summary()
    test_handle_missing_values_mean()
    test_handle_missing_values_drop()
    test_find_and_remove_duplicates()
    test_clean_pipeline_runs_end_to_end()
    print("All Module 1 tests passed!")
