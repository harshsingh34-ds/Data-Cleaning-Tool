"""
Module 5: Integration (Streamlit UI)
--------------------------------------
This is the ONLY file that should contain UI code (st.something calls).
It imports the logic from Modules 1-4 and wires it together into a
step-by-step web app:

    Upload -> Clean -> Standardise -> Reduce -> Visualize -> Download

Run it with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from modules import module1_cleaning as m1
from modules import module2_standardisation as m2
from modules import module3_reduction as m3
from modules import module4_visualization as m4


st.set_page_config(page_title="Data Cleaning & Exploration Tool", layout="wide")


# ---------------------------------------------------------------------------
# Helper: keep the working DataFrame in Streamlit's session_state so it
# survives between button clicks and page reruns (Streamlit reruns the
# whole script top-to-bottom on every interaction).
# ---------------------------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "original_df" not in st.session_state:
    st.session_state.original_df = None


def load_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError("Please upload a .csv or .xlsx file.")


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("🧹 Data Cleaning Tool")
step = st.sidebar.radio(
    "Steps",
    [
        "1. Upload Data",
        "2. Clean (Missing/Duplicates)",
        "3. Standardise (Dates/Text)",
        "4. Reduce Dimensions (PCA)",
        "5. Visualize",
        "6. Download Result",
    ],
)

if st.session_state.df is not None:
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Current shape: {st.session_state.df.shape[0]} rows x {st.session_state.df.shape[1]} cols")
    if st.sidebar.button("Reset to original upload"):
        st.session_state.df = st.session_state.original_df.copy()
        st.sidebar.success("Reset done.")


# ---------------------------------------------------------------------------
# STEP 1: Upload
# ---------------------------------------------------------------------------
if step == "1. Upload Data":
    st.title("Step 1: Upload your data")
    st.write("Upload a CSV or Excel file to get started.")

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df = load_file(uploaded_file)
            st.session_state.df = df
            st.session_state.original_df = df.copy()
            st.success(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
        except Exception as e:
            st.error(f"Could not read that file: {e}")

    if st.session_state.df is not None:
        st.subheader("Preview")
        st.dataframe(st.session_state.df.head(20))


# ---------------------------------------------------------------------------
# STEP 2: Clean
# ---------------------------------------------------------------------------
elif step == "2. Clean (Missing/Duplicates)":
    st.title("Step 2: Handle missing values & duplicates")

    if st.session_state.df is None:
        st.warning("Please upload data first (Step 1).")
    else:
        df = st.session_state.df

        st.subheader("Missing value summary")
        st.dataframe(m1.get_missing_value_summary(df))

        strategy = st.selectbox(
            "How should missing values be filled?",
            ["mean", "median", "mode", "zero", "drop"],
            help="mean/median/zero apply to numeric columns; mode works on any column; "
                 "drop removes rows that have any missing value.",
        )

        if st.button("Apply missing-value fix"):
            st.session_state.df = m1.handle_missing_values(df, strategy=strategy)
            st.success("Missing values handled.")
            st.dataframe(st.session_state.df.head(20))

        st.markdown("---")
        st.subheader("Duplicate rows")
        dupes = m1.find_duplicates(st.session_state.df)
        st.write(f"Found {len(dupes)} duplicate row(s).")
        if len(dupes) > 0:
            st.dataframe(dupes.head(20))

        if st.button("Remove duplicates"):
            st.session_state.df = m1.remove_duplicates(st.session_state.df)
            st.success("Duplicates removed.")
            st.dataframe(st.session_state.df.head(20))


# ---------------------------------------------------------------------------
# STEP 3: Standardise
# ---------------------------------------------------------------------------
elif step == "3. Standardise (Dates/Text)":
    st.title("Step 3: Standardise dates & text")

    if st.session_state.df is None:
        st.warning("Please upload data first (Step 1).")
    else:
        df = st.session_state.df

        st.subheader("Date columns")
        date_cols = st.multiselect("Select column(s) that contain dates", df.columns.tolist())
        if date_cols and st.button("Standardise selected date columns"):
            st.session_state.df = m2.standardize_dates(df, date_cols)
            st.success("Dates standardised to YYYY-MM-DD.")
            st.dataframe(st.session_state.df[date_cols].head(20))

        st.markdown("---")
        st.subheader("Fuzzy text grouping")
        text_cols = [c for c in df.columns if df[c].dtype == object]
        if not text_cols:
            st.info("No text columns found.")
        else:
            chosen_col = st.selectbox("Select a text column to group", text_cols)
            threshold = st.slider("Similarity threshold (higher = stricter matching)", 50, 100, 85)

            if st.button("Preview groups"):
                groups = m2.find_fuzzy_groups(st.session_state.df, chosen_col, threshold)
                st.session_state["_fuzzy_groups"] = groups
                st.write(f"Found {len(groups)} group(s):")
                for canonical, variants in groups.items():
                    if len(variants) > 1:
                        st.write(f"**{canonical}** ← {', '.join(variants)}")

            if "_fuzzy_groups" in st.session_state and st.button("Apply grouping"):
                st.session_state.df = m2.apply_fuzzy_grouping(
                    st.session_state.df, chosen_col, st.session_state["_fuzzy_groups"]
                )
                st.success("Grouping applied.")
                st.dataframe(st.session_state.df.head(20))


# ---------------------------------------------------------------------------
# STEP 4: PCA
# ---------------------------------------------------------------------------
elif step == "4. Reduce Dimensions (PCA)":
    st.title("Step 4: Dimensionality reduction (PCA)")

    if st.session_state.df is None:
        st.warning("Please upload data first (Step 1).")
    else:
        df = st.session_state.df
        numeric_cols = m3.get_numeric_columns(df)

        if len(numeric_cols) < 2:
            st.warning("Need at least 2 numeric columns for PCA.")
        else:
            selected_cols = st.multiselect(
                "Numeric columns to include", numeric_cols, default=numeric_cols
            )

            max_components = min(5, len(selected_cols)) if selected_cols else 2

            if len(selected_cols) < 2:
                st.info("Select at least 2 numeric columns to run PCA.")
                n_components = 2
            elif max_components <= 2:
                # Only 2 columns available -- nothing to choose, skip the slider
                n_components = 2
                st.caption("Using 2 components (max possible with 2 selected columns).")
            else:
                n_components = st.slider("Number of components", 2, max_components, 2)

            if st.button("Run PCA") and len(selected_cols) >= 2:
                try:
                    result = m3.apply_pca(df, columns=selected_cols, n_components=n_components)
                    st.session_state["pca_result"] = result
                    st.success("PCA complete.")

                    st.subheader("Explained variance")
                    for i, (ev, cv) in enumerate(
                        zip(result["explained_variance"], result["cumulative_variance"])
                    ):
                        st.write(f"PC{i+1}: {ev}% (cumulative {cv}%)")

                    st.subheader("Component loadings")
                    st.dataframe(result["loadings"])

                    st.subheader("Transformed data (preview)")
                    st.dataframe(result["transformed_df"].head(20))
                except ValueError as e:
                    st.error(str(e))


# ---------------------------------------------------------------------------
# STEP 5: Visualize
# ---------------------------------------------------------------------------
elif step == "5. Visualize":
    st.title("Step 5: Visualize")

    if st.session_state.df is None:
        st.warning("Please upload data first (Step 1).")
    else:
        df = st.session_state.df

        tab1, tab2, tab3 = st.tabs(["Missing Values", "Correlation", "PCA Scatter"])

        with tab1:
            st.pyplot(m4.plot_missing_value_heatmap(df))

        with tab2:
            numeric_cols = m3.get_numeric_columns(df)
            if len(numeric_cols) < 2:
                st.info("Need at least 2 numeric columns for a correlation matrix.")
            else:
                st.pyplot(m4.plot_correlation_matrix(df))

        with tab3:
            if "pca_result" not in st.session_state:
                st.info("Run PCA in Step 4 first.")
            else:
                result = st.session_state["pca_result"]
                pca_df = result["transformed_df"]
                non_numeric = [c for c in pca_df.columns if not c.startswith("PC")]
                color_by = st.selectbox("Color points by", [None] + non_numeric)
                st.plotly_chart(
                    m4.plot_pca_scatter(pca_df, color_by=color_by),
                    width="stretch",
                )
                st.plotly_chart(
                    m4.plot_explained_variance(
                        result["explained_variance"], result["cumulative_variance"]
                    ),
                    width="stretch",
                )


# ---------------------------------------------------------------------------
# STEP 6: Download
# ---------------------------------------------------------------------------
elif step == "6. Download Result":
    st.title("Step 6: Download your cleaned data")

    if st.session_state.df is None:
        st.warning("Please upload data first (Step 1).")
    else:
        df = st.session_state.df
        st.dataframe(df.head(20))

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download as CSV",
            data=csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv",
        )
