"""
Module 3: Dimensionality Reduction
------------------------------------
Purpose:
    Compress many numeric columns into a smaller number of "principal
    components" using PCA (Principal Component Analysis), so the data
    is easier to visualize and analyze.

Why scale before PCA?
    PCA is sensitive to the scale of each column. A column measured in
    thousands (like "salary") would dominate a column measured in single
    digits (like "age") purely because of its scale, not because it's
    actually more important. StandardScaler fixes this by putting every
    column on the same scale (mean 0, standard deviation 1) before PCA runs.

Design rule: functions take a DataFrame in, return data out. No printing,
no UI code here — that lives in Module 5.
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def get_numeric_columns(df: pd.DataFrame) -> list:
    """Return the names of columns that PCA can actually be run on."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def apply_pca(
    df: pd.DataFrame,
    columns: list | None = None,
    n_components: int = 2,
) -> dict:
    """
    Run PCA on the numeric columns of a DataFrame.

    Parameters
    ----------
    df : pandas DataFrame
    columns : list of str, optional
        Which numeric columns to include. If None, all numeric columns
        are used.
    n_components : int
        How many principal components to keep (2 or 3 is typical for
        plotting purposes).

    Returns
    -------
    A dictionary with:
        "transformed_df"     -> DataFrame with columns PC1, PC2, ... plus
                                 any non-numeric columns from the original
                                 data (kept as-is, for labeling points)
        "explained_variance" -> list of floats, % variance explained by
                                 each component
        "cumulative_variance"-> running total of explained variance
        "loadings"           -> DataFrame showing how much each original
                                 column contributes to each component
    """
    numeric_cols = columns if columns is not None else get_numeric_columns(df)
    numeric_cols = [c for c in numeric_cols if c in df.columns]

    if len(numeric_cols) < 2:
        raise ValueError(
            "PCA needs at least 2 numeric columns to run. "
            f"Found: {numeric_cols}"
        )

    # Drop rows with missing values in the columns we're about to use —
    # PCA cannot handle NaNs. (Run Module 1 first to avoid losing rows here.)
    working_data = df[numeric_cols].dropna()

    n_components = min(n_components, len(numeric_cols), len(working_data))

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(working_data)

    pca = PCA(n_components=n_components)
    transformed_values = pca.fit_transform(scaled_values)

    component_names = [f"PC{i+1}" for i in range(n_components)]
    transformed_df = pd.DataFrame(
        transformed_values, columns=component_names, index=working_data.index
    )

    # Bring along any non-numeric columns (e.g. names, categories) so
    # the scatter plot in Module 4 can color/label points meaningfully.
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]
    if non_numeric_cols:
        transformed_df = pd.concat(
            [transformed_df, df.loc[working_data.index, non_numeric_cols]],
            axis=1,
        )

    explained_variance = (pca.explained_variance_ratio_ * 100).round(2).tolist()
    cumulative_variance = np.cumsum(explained_variance).round(2).tolist()

    loadings = pd.DataFrame(
        pca.components_.T,
        columns=component_names,
        index=numeric_cols,
    ).round(4)

    return {
        "transformed_df": transformed_df,
        "explained_variance": explained_variance,
        "cumulative_variance": cumulative_variance,
        "loadings": loadings,
    }
