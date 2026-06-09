# =============================================================================
# pages/upload_settings.py — Data Upload & Settings Page
# =============================================================================

import streamlit as st
import pandas as pd
import io, sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_utils import get_data, load_default_data, clean_data

REQUIRED_COLUMNS = {
    "Country": str,
    "Crop": str,
    "Year": "numeric",
    "Yield_hg_ha": "numeric",
    "Rainfall_mm": "numeric",
    "Temperature_C": "numeric",
    "Pesticides_tonnes": "numeric",
}

INTERNAL_NAMES = {
    "Yield_hg_ha": "Yield",
    "Rainfall_mm": "Rainfall",
    "Temperature_C": "Temperature",
    "Pesticides_tonnes": "Pesticides",
}


def validate_dataframe(df: pd.DataFrame):
    """Return (is_valid, list_of_issues, cleaned_df)."""
    issues = []
    df_check = df.copy()
    df_check.columns = df_check.columns.str.strip()

    # Check required columns (allow already-renamed internal names)
    required = list(REQUIRED_COLUMNS.keys())
    alt = {v: v for v in INTERNAL_NAMES.values()}  # already-renamed columns

    found = []
    missing = []
    for req in required:
        internal = INTERNAL_NAMES.get(req, req)
        if req in df_check.columns or internal in df_check.columns:
            found.append(req)
        else:
            missing.append(req)

    if missing:
        issues.append(f"Missing columns: {', '.join(missing)}")

    # Check for completely empty dataset
    if len(df_check) == 0:
        issues.append("Dataset is empty (0 rows).")

    # Check duplicates
    dups = df_check.duplicated().sum()
    if dups > 0:
        issues.append(f"⚠️ Found {dups} duplicate rows (will be removed automatically).")

    # Check null counts
    null_counts = df_check.isnull().sum()
    high_null = null_counts[null_counts > len(df_check) * 0.3]
    for col, cnt in high_null.items():
        issues.append(f"⚠️ Column '{col}' has {cnt} nulls ({cnt/len(df_check)*100:.0f}% missing).")

    if issues and any("Missing columns" in i for i in issues):
        return False, issues, None

    cleaned = clean_data(df_check)
    return True, issues, cleaned


def upload_section():
    st.markdown("<div class='section-title'>📤 Upload Dataset</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(0,40,100,0.2); border:1px solid rgba(0,180,255,0.2);
                border-radius:12px; padding:16px; margin-bottom:20px; font-size:0.9rem; color:#7ab0d8;'>
        <strong style='color:#e8f4ff;'>Expected CSV Format:</strong><br>
        <code style='color:#00c8ff; background:rgba(0,0,0,0.3); padding:2px 6px; border-radius:4px;'>
        Country, Crop, Year, Yield_hg_ha, Rainfall_mm, Temperature_C, Pesticides_tonnes
        </code><br><br>
        Columns are case-sensitive. Additional columns will be ignored.
        A sample file can be downloaded below.
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your CSV here or click to browse",
        type=["csv"],
        key="settings_uploader",
    )

    if uploaded:
        with st.spinner("Validating and processing..."):
            try:
                raw = pd.read_csv(uploaded)
                valid, issues, cleaned = validate_dataframe(raw)
            except Exception as e:
                st.error(f"❌ Could not read file: {e}")
                return

        if not valid:
            st.error("❌ Dataset validation failed:")
            for issue in issues:
                st.markdown(f"- {issue}")
            return

        # Warnings (non-blocking)
        if issues:
            st.warning("⚠️ Dataset loaded with warnings:")
            for issue in issues:
                st.markdown(f"- {issue}")
        else:
            st.success("✅ Dataset validated successfully! No issues found.")

        st.session_state["uploaded_df"] = cleaned

        # ── Dataset info cards ────────────────────────────────────────────────
        st.markdown("<div class='section-title'>📋 Dataset Information</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{len(cleaned):,}")
        c2.metric("Columns", len(cleaned.columns))
        c3.metric("Missing Values", cleaned.isnull().sum().sum())
        c4.metric("Duplicate Rows", "0 (removed)")

        col_df = pd.DataFrame({
            "Column": cleaned.columns,
            "Type": cleaned.dtypes.astype(str).values,
            "Non-Null": cleaned.notnull().sum().values,
            "Null %": (cleaned.isnull().mean() * 100).round(1).values,
        })
        st.dataframe(col_df, use_container_width=True, hide_index=True)

        st.markdown("**Preview (first 10 rows):**")
        st.dataframe(cleaned.head(10), use_container_width=True, hide_index=True)


def settings_section():
    st.markdown("<div class='section-title'>⚙️ Settings & Controls</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div style='background:rgba(0,40,100,0.2); border:1px solid rgba(0,180,255,0.15);
                    border-radius:12px; padding:20px;'>
            <div style='font-family:"Space Grotesk",sans-serif; font-size:1rem;
                        font-weight:600; color:#e8f4ff; margin-bottom:12px;'>🔄 Data Reset</div>
        """, unsafe_allow_html=True)

        if st.button("Reset to Default Dataset", key="reset_btn"):
            if "uploaded_df" in st.session_state:
                del st.session_state["uploaded_df"]
            st.success("✅ Reset to default dataset.")

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div style='background:rgba(0,40,100,0.2); border:1px solid rgba(0,180,255,0.15);
                    border-radius:12px; padding:20px;'>
            <div style='font-family:"Space Grotesk",sans-serif; font-size:1rem;
                        font-weight:600; color:#e8f4ff; margin-bottom:12px;'>🗑️ Clear All Session</div>
        """, unsafe_allow_html=True)

        if st.button("Clear All Cache & Filters", key="clear_btn"):
            for key in list(st.session_state.keys()):
                if key != "page":
                    del st.session_state[key]
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ All cache and session data cleared.")

        st.markdown("</div>", unsafe_allow_html=True)


def sample_download():
    st.markdown("<div class='section-title'>📥 Download Sample File</div>", unsafe_allow_html=True)
    sample = pd.DataFrame({
        "Country": ["India", "China", "USA"],
        "Crop": ["Rice", "Wheat", "Maize"],
        "Year": [2020, 2020, 2020],
        "Yield_hg_ha": [38000, 52000, 95000],
        "Rainfall_mm": [1500, 650, 850],
        "Temperature_C": [26.0, 16.0, 18.5],
        "Pesticides_tonnes": [65000, 118000, 81000],
    })
    csv = sample.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📄 Download Sample CSV Template",
        data=csv,
        file_name="sample_crop_yield.csv",
        mime="text/csv",
    )
    st.dataframe(sample, use_container_width=True, hide_index=True)


def current_dataset_info():
    st.markdown("<div class='section-title'>📊 Current Active Dataset</div>", unsafe_allow_html=True)
    df = get_data(st.session_state)
    source = "📤 User Uploaded" if "uploaded_df" in st.session_state else "📦 Default (Bundled)"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Source", source[:10])
    c2.metric("Total Rows", f"{len(df):,}")
    c3.metric("Columns", len(df.columns))
    c4.metric("Countries", df["Country"].nunique())
    c5.metric("Crops", df["Crop"].nunique())

    with st.expander("📋 View Full Column Summary"):
        summary = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Unique": [df[c].nunique() for c in df.columns],
        })
        st.dataframe(summary, use_container_width=True, hide_index=True)

    with st.expander("📐 Statistical Summary"):
        st.dataframe(df.describe().T, use_container_width=True)


def project_info():
    st.markdown("<div class='section-title'>ℹ️ Project Information</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:linear-gradient(135deg, rgba(0,80,200,0.15), rgba(0,40,120,0.08));
                border:1px solid rgba(0,180,255,0.2); border-radius:16px; padding:28px;'>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:24px;'>
            <div>
                <div style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px;
                            color:#4a7090; margin-bottom:4px;'>Project Title</div>
                <div style='font-family:"Space Grotesk",sans-serif; font-size:1.1rem;
                            font-weight:600; color:#e8f4ff;'>CropIQ Analytics Dashboard</div>
            </div>
            <div>
                <div style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px;
                            color:#4a7090; margin-bottom:4px;'>Technology Stack</div>
                <div style='font-size:0.9rem; color:#b8d4f0;'>Python · Streamlit · Plotly · scikit-learn</div>
            </div>
            <div>
                <div style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px;
                            color:#4a7090; margin-bottom:4px;'>Academic Level</div>
                <div style='font-size:0.9rem; color:#b8d4f0;'>MCA Final Year Project</div>
            </div>
            <div>
                <div style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px;
                            color:#4a7090; margin-bottom:4px;'>ML Models</div>
                <div style='font-size:0.9rem; color:#b8d4f0;'>Linear Regression · Random Forest</div>
            </div>
            <div>
                <div style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px;
                            color:#4a7090; margin-bottom:4px;'>Pages</div>
                <div style='font-size:0.9rem; color:#b8d4f0;'>5 (Home · Analysis · Viz · ML · Settings)</div>
            </div>
            <div>
                <div style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1.5px;
                            color:#4a7090; margin-bottom:4px;'>Chart Types</div>
                <div style='font-size:0.9rem; color:#b8d4f0;'>12+ interactive Plotly charts</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show():
    st.markdown("""
    <h2 style='font-family:"Space Grotesk",sans-serif; color:#e8f4ff; margin-bottom:4px;'>
        📂 Upload & Settings
    </h2>
    <p style='color:#7ab0d8; margin-bottom:24px;'>
        Manage your dataset, validate uploads, and configure application settings.
    </p>
    """, unsafe_allow_html=True)

    current_dataset_info()
    st.markdown("<br>", unsafe_allow_html=True)
    upload_section()
    st.markdown("<br>", unsafe_allow_html=True)
    sample_download()
    st.markdown("<br>", unsafe_allow_html=True)
    settings_section()
    st.markdown("<br>", unsafe_allow_html=True)
    project_info()
