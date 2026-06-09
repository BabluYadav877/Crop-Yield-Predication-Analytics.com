# =============================================================================
# utils/data_utils.py — Shared data-loading and helper functions
# =============================================================================

import pandas as pd
import numpy as np
import streamlit as st
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crop_yield_data.csv")


@st.cache_data(show_spinner=False)
def load_default_data() -> pd.DataFrame:
    """Load the bundled crop-yield CSV and return a clean DataFrame."""
    df = pd.read_csv(DATA_PATH)
    df = clean_data(df)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply basic cleaning rules to any uploaded/default DataFrame."""
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Rename columns to standard internal names if they differ
    rename_map = {
        "Yield_hg_ha": "Yield",
        "Rainfall_mm": "Rainfall",
        "Temperature_C": "Temperature",
        "Pesticides_tonnes": "Pesticides",
    }
    df.rename(columns=rename_map, inplace=True)

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # Coerce numeric columns
    for col in ["Yield", "Rainfall", "Temperature", "Pesticides", "Year"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where critical columns are null
    df.dropna(subset=["Yield", "Year"], inplace=True)

    # Reset index
    df.reset_index(drop=True, inplace=True)
    return df


def get_data(session_state) -> pd.DataFrame:
    """Return uploaded data if available, otherwise default dataset."""
    if "uploaded_df" in session_state and session_state.uploaded_df is not None:
        return session_state.uploaded_df
    return load_default_data()


def apply_filters(df: pd.DataFrame, countries, crops, years) -> pd.DataFrame:
    """Filter DataFrame based on sidebar selections."""
    if countries and "All" not in countries:
        df = df[df["Country"].isin(countries)]
    if crops and "All" not in crops:
        df = df[df["Crop"].isin(crops)]
    if years:
        df = df[df["Year"].between(years[0], years[1])]
    return df


def get_filter_options(df: pd.DataFrame):
    """Return sorted unique values for filter widgets."""
    countries = sorted(df["Country"].dropna().unique().tolist())
    crops = sorted(df["Crop"].dropna().unique().tolist())
    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())
    return countries, crops, year_min, year_max
