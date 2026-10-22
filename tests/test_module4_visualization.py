"""
Standalone test for Module 4.
Run with:  pytest tests/test_module4_visualization.py -v

These tests just check that each function RETURNS a figure object without
crashing — they don't check pixel-perfect visuals (that's what your own
eyes are for when you run the Streamlit app).
"""

import pandas as pd
import numpy as np
import sys
import os
import matplotlib.figure
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules import module3_reduction as m3
from modules import module4_visualization as m4


def make_sample_df(n=30):
    rng = np.random.default_rng(1)
    df = pd.DataFrame({
        "a": rng.normal(0, 1, n),
        "b": rng.normal(5, 2, n),
        "c": rng.normal(-3, 1, n),
    })
    df.loc[0:3, "a"] = np.nan  # inject some missing values
    return df


def test_plot_missing_value_heatmap():
    df = make_sample_df()
    fig = m4.plot_missing_value_heatmap(df)
    assert isinstance(fig, matplotlib.figure.Figure)


def test_plot_correlation_matrix():
    df = make_sample_df()
    fig = m4.plot_correlation_matrix(df)
    assert isinstance(fig, matplotlib.figure.Figure)


def test_plot_distribution_comparison():
    df = make_sample_df()
    df_after = df.fillna(df.mean(numeric_only=True))
    fig = m4.plot_distribution_comparison(df, df_after, "a")
    assert isinstance(fig, matplotlib.figure.Figure)


def test_plot_pca_scatter_and_variance():
    df = make_sample_df().fillna(0)
    result = m3.apply_pca(df, n_components=2)
    scatter_fig = m4.plot_pca_scatter(result["transformed_df"])
    assert isinstance(scatter_fig, go.Figure)

    variance_fig = m4.plot_explained_variance(
        result["explained_variance"], result["cumulative_variance"]
    )
    assert isinstance(variance_fig, go.Figure)


if __name__ == "__main__":
    test_plot_missing_value_heatmap()
    test_plot_correlation_matrix()
    test_plot_distribution_comparison()
    test_plot_pca_scatter_and_variance()
    print("All Module 4 tests passed!")
