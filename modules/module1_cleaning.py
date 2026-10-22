"""
Module 1: Data Cleaning
------------------------
Purpose:
    Handle missing values and duplicate rows in a pandas DataFrame.

Design rule (important for beginners):
    Every function here takes a DataFrame in and returns a NEW DataFrame out.
    Nothing is printed, nothing is displayed on screen. That job belongs to
    Module 5 (the Streamlit app). Keeping "logic" and "display" separate
    makes each piece easy to test on its own.
"""

import pandas as pd
import numpy as np


def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a small summary table showing how many values are missing
    in each column, and what percentage that represents.

    Example output:
        column      missing_count   missing_percent
        age         12              4.0
        city        3               1.0
    """
    missing_count = df.isnull().sum()
    missing_percent = (missing_count / len(df)) * 100 if len(df) > 0 else missing_count * 0

    summary = pd.DataFrame({
        "column": df.columns,
        "missing_count": missing_count.values,
        "missing_percent": missing_percent.round(2).values,
    })
    return summary.sort_values("missing_count", ascending=False).reset_index(drop=True)


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "mean",
    columns: list | None = None,
) -> pd.DataFrame:
    """
    Fill in missing values using one of several strategies.

    Parameters
    ----------
    df : pandas DataFrame
        The data to clean.
    strategy : str
        One of:
          "mean"   -> fill numeric columns with the column mean
          "median" -> fill numeric columns with the column median
          "mode"   -> fill any column (numeric or text) with the most frequent value
          "drop"   -> drop any row that has at least one missing value
          "zero"   -> fill numeric columns with 0
    columns : list of str, optional
        If given, only these columns are touched. If None, every column
        that matches the strategy's data type is touched.

    Returns
    -------
    A new, cleaned DataFrame. The original df is not changed.
    """
    result = df.copy()
    target_columns = columns if columns is not None else list(result.columns)

    if strategy == "drop":
        return result.dropna(subset=target_columns).reset_index(drop=True)

    for col in target_columns:
        if col not in result.columns:
            continue

        is_numeric = pd.api.types.is_numeric_dtype(result[col])

        if strategy == "mean" and is_numeric:
            result[col] = result[col].fillna(result[col].mean())
        elif strategy == "median" and is_numeric:
            result[col] = result[col].fillna(result[col].median())
        elif strategy == "zero" and is_numeric:
            result[col] = result[col].fillna(0)
        elif strategy == "mode":
            mode_values = result[col].mode()
            if not mode_values.empty:
                result[col] = result[col].fillna(mode_values.iloc[0])
        # If strategy doesn't apply to this column's type (e.g. "mean" on
        # a text column), we simply leave that column untouched.

    return result


def find_duplicates(df: pd.DataFrame, subset: list | None = None) -> pd.DataFrame:
    """
    Return only the rows that are duplicates (keeps the first occurrence
    hidden, shows the repeats), so the user can preview what will be removed.
    """
    return df[df.duplicated(subset=subset, keep="first")]


def remove_duplicates(
    df: pd.DataFrame,
    subset: list | None = None,
    keep: str = "first",
) -> pd.DataFrame:
    """
    Remove duplicate rows.

    Parameters
    ----------
    subset : list of str, optional
        Columns to consider when identifying duplicates. If None, all
        columns are compared.
    keep : str
        "first" -> keep the first occurrence (default)
        "last"  -> keep the last occurrence
        False   -> drop every row that has any duplicate at all
    """
    return df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)


def clean_pipeline(
    df: pd.DataFrame,
    missing_strategy: str = "mean",
    remove_dupes: bool = True,
) -> pd.DataFrame:
    """
    Convenience function that runs the full Module 1 pipeline in one call:
    1. Fill missing values
    2. Remove duplicate rows

    This is what Module 5 (the UI) will usually call.
    """
    result = handle_missing_values(df, strategy=missing_strategy)
    if remove_dupes:
        result = remove_duplicates(result)
    return result
