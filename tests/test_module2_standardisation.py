"""
Standalone test for Module 2.
Run with:  pytest tests/test_module2_standardisation.py -v
"""

import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules import module2_standardisation as m2


def make_sample_df():
    return pd.DataFrame({
        "signup_date": ["2024-01-05", "05/02/2024", "March 3, 2024", None],
        "city": ["New York", "NY", "N.Y.", "Los Angeles"],
    })


def test_standardize_dates():
    df = make_sample_df()
    result = m2.standardize_dates(df, columns=["signup_date"])
    # All non-null values should now match YYYY-MM-DD pattern (10 chars, dashes at 4 and 7)
    valid = result["signup_date"].dropna()
    for value in valid:
        assert len(value) == 10
        assert value[4] == "-" and value[7] == "-"


def test_find_fuzzy_groups():
    df = make_sample_df()
    groups = m2.find_fuzzy_groups(df, "city", similarity_threshold=70)
    # "New York", "NY", "N.Y." should end up grouped together
    all_grouped_values = [v for values in groups.values() for v in values]
    assert "New York" in all_grouped_values
    assert "Los Angeles" in all_grouped_values


def test_apply_fuzzy_grouping():
    df = make_sample_df()
    mapping = {"New York": ["New York", "NY", "N.Y."], "Los Angeles": ["Los Angeles"]}
    result = m2.apply_fuzzy_grouping(df, "city", mapping)
    assert set(result["city"].unique()) == {"New York", "Los Angeles"}


def test_standardize_text_column():
    df = pd.DataFrame({"name": ["  john smith", "JANE DOE  ", "bob  jones"]})
    result = m2.standardize_text_column(df, "name", case="title")
    assert result["name"].iloc[0] == "John Smith"
    assert result["name"].iloc[1] == "Jane Doe"


if __name__ == "__main__":
    test_standardize_dates()
    test_find_fuzzy_groups()
    test_apply_fuzzy_grouping()
    test_standardize_text_column()
    print("All Module 2 tests passed!")
