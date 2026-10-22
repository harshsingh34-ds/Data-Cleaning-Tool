"""
Standalone test for Module 3.
Run with:  pytest tests/test_module3_reduction.py -v
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules import module3_reduction as m3


def make_sample_df(n=50):
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "height": rng.normal(170, 10, n),
        "weight": rng.normal(70, 15, n),
        "age": rng.normal(35, 12, n),
        "label": rng.choice(["A", "B"], n),
    })


def test_get_numeric_columns():
    df = make_sample_df()
    cols = m3.get_numeric_columns(df)
    assert set(cols) == {"height", "weight", "age"}


def test_apply_pca_shape():
    df = make_sample_df()
    result = m3.apply_pca(df, n_components=2)
    assert "PC1" in result["transformed_df"].columns
    assert "PC2" in result["transformed_df"].columns
    assert "label" in result["transformed_df"].columns  # non-numeric carried along
    assert len(result["explained_variance"]) == 2


def test_apply_pca_variance_sums_reasonably():
    df = make_sample_df()
    result = m3.apply_pca(df, n_components=3)
    # cumulative variance of all 3 components (using all 3 numeric cols) should be ~100%
    assert result["cumulative_variance"][-1] > 95


def test_apply_pca_raises_with_too_few_columns():
    df = pd.DataFrame({"only_one_col": [1, 2, 3]})
    try:
        m3.apply_pca(df)
        assert False, "Expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_get_numeric_columns()
    test_apply_pca_shape()
    test_apply_pca_variance_sums_reasonably()
    test_apply_pca_raises_with_too_few_columns()
    print("All Module 3 tests passed!")
