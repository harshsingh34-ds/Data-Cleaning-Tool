"""
Module 2: Standardisation
--------------------------
Purpose:
    1. Convert messy date columns (many formats) into one standard datetime format.
    2. Group similar-but-not-identical text values together using fuzzy matching
       (e.g. "NY", "N.Y.", "New York" -> all become "New York").

Design rule: functions take a DataFrame in, return a DataFrame out. No printing,
no UI code here — that lives in Module 5.
"""

import pandas as pd
from dateutil import parser as date_parser
from rapidfuzz import fuzz, process


def standardize_dates(
    df: pd.DataFrame,
    columns: list,
    output_format: str = "%Y-%m-%d",
    errors: str = "coerce",
) -> pd.DataFrame:
    """
    Convert one or more messy date columns into a single, consistent
    string date format.

    Parameters
    ----------
    df : pandas DataFrame
    columns : list of str
        Names of the columns that contain dates.
    output_format : str
        strftime format string for the final output, e.g. "%Y-%m-%d".
    errors : str
        "coerce" -> unparseable dates become NaT / blank (safe default)
        "raise"  -> stop and raise an error on the first bad date

    Returns
    -------
    A new DataFrame where the given columns are re-written as clean,
    consistently formatted date strings.
    """
    result = df.copy()

    def _parse_one(value):
        if pd.isna(value):
            return pd.NaT
        try:
            return date_parser.parse(str(value), dayfirst=False, fuzzy=True)
        except (ValueError, OverflowError, TypeError):
            if errors == "raise":
                raise
            return pd.NaT

    for col in columns:
        if col not in result.columns:
            continue
        parsed = result[col].apply(_parse_one)
        result[col] = parsed.apply(
            lambda d: d.strftime(output_format) if pd.notna(d) else None
        )

    return result


def find_fuzzy_groups(
    df: pd.DataFrame,
    column: str,
    similarity_threshold: int = 85,
) -> dict:
    """
    Look at all unique values in a text column and group ones that are
    very similar to each other. Does NOT change the DataFrame — this is
    a "preview" function so the user can see the proposed grouping first.

    Returns
    -------
    A dictionary like:
        {
            "New York": ["New York", "NY", "N.Y."],
            "Los Angeles": ["Los Angeles", "LA"],
        }
    The dictionary key is the "canonical" (most common) spelling chosen
    for each group.
    """
    unique_values = [v for v in df[column].dropna().unique().tolist()]
    if not unique_values:
        return {}

    value_counts = df[column].value_counts()
    groups: dict[str, list[str]] = {}
    assigned: set[str] = set()

    # Process most-frequent values first so the canonical name tends to
    # be the spelling people actually used most often.
    for value in sorted(unique_values, key=lambda v: -value_counts.get(v, 0)):
        if value in assigned:
            continue

        matches = process.extract(
            value,
            [v for v in unique_values if v not in assigned],
            scorer=fuzz.token_sort_ratio,
            limit=None,
        )
        similar = [m[0] for m in matches if m[1] >= similarity_threshold]
        if value not in similar:
            similar.append(value)

        groups[value] = similar
        assigned.update(similar)

    return groups


def apply_fuzzy_grouping(
    df: pd.DataFrame,
    column: str,
    mapping: dict,
) -> pd.DataFrame:
    """
    Apply a grouping dictionary (as produced by find_fuzzy_groups, and
    possibly edited by the user in the UI) to actually replace values
    in the DataFrame.

    `mapping` format: {canonical_name: [list, of, variants]}
    """
    result = df.copy()
    reverse_map = {}
    for canonical, variants in mapping.items():
        for variant in variants:
            reverse_map[variant] = canonical

    result[column] = result[column].map(lambda v: reverse_map.get(v, v))
    return result


def standardize_text_column(
    df: pd.DataFrame,
    column: str,
    strip_whitespace: bool = True,
    case: str = "title",
) -> pd.DataFrame:
    """
    Simple, non-fuzzy text cleanup: trims extra spaces and fixes casing.

    case: "title" | "upper" | "lower" | "none"
    """
    result = df.copy()
    series = result[column].astype(str)

    if strip_whitespace:
        series = series.str.strip().str.replace(r"\s+", " ", regex=True)

    if case == "title":
        series = series.str.title()
    elif case == "upper":
        series = series.str.upper()
    elif case == "lower":
        series = series.str.lower()

    result[column] = series
    return result
