"""
Module 4: Visualization
-------------------------
Purpose:
    Turn cleaned / processed data into charts:
      - a heatmap showing where missing values are
      - a correlation matrix (matplotlib/seaborn, static)
      - an interactive PCA scatter plot (plotly)

Design rule: every function RETURNS a figure object. Nothing calls
plt.show() and nothing calls st.pyplot() in this file — Module 5
decides how and where to actually display the figure.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # safe backend, no GUI needed
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


def plot_missing_value_heatmap(df: pd.DataFrame):
    """
    Return a matplotlib Figure showing a heatmap of missing values.
    Rows = data rows, columns = your columns, colored cells = missing.

    Always shows a colorbar/legend, and adds a text note when there are
    zero missing values, so a solid-color result isn't mistaken for a bug.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    missing_mask = df.isnull()
    total_missing = int(missing_mask.sum().sum())

    sns.heatmap(
        missing_mask,
        cbar=True,
        cbar_kws={"ticks": [0, 1], "label": "0 = present, 1 = missing"},
        cmap="rocket_r",
        vmin=0,
        vmax=1,
        ax=ax,
    )
    ax.set_title("Missing Value Heatmap (colored = missing)")

    if total_missing == 0:
        ax.text(
            0.5, -0.08,
            "No missing values found in this data.",
            transform=ax.transAxes,
            ha="center", fontsize=10, color="green",
        )

    fig.tight_layout()
    return fig


def plot_correlation_matrix(df: pd.DataFrame, columns: list | None = None):
    """
    Return a matplotlib Figure showing a correlation heatmap between
    numeric columns. Values range from -1 (opposite) to 1 (move together).
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if columns is not None:
        numeric_df = numeric_df[[c for c in columns if c in numeric_df.columns]]

    corr = numeric_df.corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Matrix")
    fig.tight_layout()
    return fig


def plot_distribution_comparison(before_df: pd.DataFrame, after_df: pd.DataFrame, column: str):
    """
    Return a matplotlib Figure comparing a column's distribution
    before vs. after cleaning — useful to sanity-check that cleaning
    didn't distort the data too much.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)

    sns.histplot(before_df[column].dropna(), kde=True, ax=axes[0], color="tomato")
    axes[0].set_title(f"Before: {column}")

    sns.histplot(after_df[column].dropna(), kde=True, ax=axes[1], color="seagreen")
    axes[1].set_title(f"After: {column}")

    fig.tight_layout()
    return fig


def plot_pca_scatter(
    pca_result_df: pd.DataFrame,
    color_by: str | None = None,
    x: str = "PC1",
    y: str = "PC2",
):
    """
    Return an interactive plotly Figure scatter-plotting the PCA output.

    Parameters
    ----------
    pca_result_df : the "transformed_df" produced by module3_reduction.apply_pca
    color_by : optional column name to color points by (e.g. a category column)
    x, y : which principal components to plot on each axis
    """
    fig = px.scatter(
        pca_result_df,
        x=x,
        y=y,
        color=color_by if color_by in pca_result_df.columns else None,
        title=f"PCA Scatter Plot ({x} vs {y})",
        hover_data=pca_result_df.columns,
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_explained_variance(explained_variance: list, cumulative_variance: list):
    """
    Return a plotly Figure showing how much variance each principal
    component explains, plus the running cumulative total.
    """
    components = [f"PC{i+1}" for i in range(len(explained_variance))]

    fig = px.bar(
        x=components,
        y=explained_variance,
        labels={"x": "Principal Component", "y": "Explained Variance (%)"},
        title="Explained Variance by Component",
    )
    fig.add_scatter(
        x=components,
        y=cumulative_variance,
        mode="lines+markers",
        name="Cumulative %",
        yaxis="y",
    )
    fig.update_layout(template="plotly_white")
    return fig
