# =============================================================================
# pages/data_analysis.py — Data Analysis & EDA Page
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_utils import get_data, get_filter_options, apply_filters, clean_data

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(5,14,31,0.6)",
    font_color="#b8d4f0",
    font_family="DM Sans",
    title_font_family="Space Grotesk",
    title_font_color="#e8f4ff",
    colorway=["#0078ff", "#00c8ff", "#4dff9d", "#ffb347", "#ff6b6b", "#c084fc"],
    xaxis=dict(gridcolor="rgba(0,180,255,0.1)", zerolinecolor="rgba(0,180,255,0.2)"),
    yaxis=dict(gridcolor="rgba(0,180,255,0.1)", zerolinecolor="rgba(0,180,255,0.2)"),
)


def sidebar_filters(df):
    countries, crops, year_min, year_max = get_filter_options(df)
    st.sidebar.markdown("### 🔍 Filters")
    sel_c = st.sidebar.multiselect("🌍 Country", ["All"] + countries, default=["All"], key="da_country")
    sel_cr = st.sidebar.multiselect("🌱 Crop", ["All"] + crops, default=["All"], key="da_crop")
    yr = st.sidebar.slider("📅 Year Range", year_min, year_max, (year_min, year_max), key="da_year")
    return apply_filters(df, sel_c, sel_cr, yr)


def dataset_preview(df):
    st.markdown("<div class='section-title'>🗂️ Dataset Preview</div>", unsafe_allow_html=True)
    rows = st.slider("Rows to display", 5, min(100, len(df)), 10, key="da_rows")
    st.dataframe(df.head(rows), use_container_width=True, hide_index=True)

    with st.expander("📐 Dataset Info"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", len(df.columns))
        c3.metric("Missing Values", df.isnull().sum().sum())
        c4.metric("Duplicate Rows", df.duplicated().sum())

        st.markdown("**Column Data Types:**")
        dtype_df = pd.DataFrame({"Column": df.dtypes.index, "Type": df.dtypes.values.astype(str)})
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    with st.expander("📊 Descriptive Statistics"):
        st.dataframe(df.describe().T.style.background_gradient(cmap="Blues"), use_container_width=True)


def data_upload_section():
    st.markdown("<div class='section-title'>📤 Upload Custom Dataset</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload a CSV with columns: Country, Crop, Year, Yield_hg_ha, Rainfall_mm, Temperature_C, Pesticides_tonnes",
        type=["csv"],
        key="da_uploader",
    )
    if uploaded:
        try:
            with st.spinner("Processing uploaded file..."):
                raw = pd.read_csv(uploaded)
                cleaned = clean_data(raw)
                st.session_state["uploaded_df"] = cleaned
            st.success(f"✅ Dataset uploaded successfully! {len(cleaned):,} records loaded.")
            st.dataframe(cleaned.head(10), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")


def top_bottom_records(df):
    st.markdown("<div class='section-title'>🏆 Top & Bottom Records</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cols = ["Country", "Crop", "Year", "Yield", "Rainfall", "Temperature"]
    with c1:
        st.markdown("**🥇 Top 5 Highest Yield**")
        top5 = df.nlargest(5, "Yield")[cols]
        st.dataframe(
            top5.style.background_gradient(subset=["Yield"], cmap="Blues").format({"Yield": "{:,.0f}"}),
            use_container_width=True, hide_index=True,
        )
    with c2:
        st.markdown("**📉 Bottom 5 Lowest Yield**")
        bot5 = df.nsmallest(5, "Yield")[cols]
        st.dataframe(
            bot5.style.background_gradient(subset=["Yield"], cmap="Reds_r").format({"Yield": "{:,.0f}"}),
            use_container_width=True, hide_index=True,
        )


def line_chart(df):
    trend = df.groupby("Year")["Yield"].mean().reset_index()
    fig = px.line(
        trend, x="Year", y="Yield",
        title="📈 Yield Trend Over Years",
        markers=True,
        labels={"Yield": "Avg Yield (hg/ha)"},
    )
    fig.update_traces(line=dict(color="#0078ff", width=2.5), marker=dict(size=7, color="#00c8ff"))
    fig.update_layout(**PLOTLY_LAYOUT, height=350)
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(df):
    avg = df.groupby("Crop")["Yield"].mean().reset_index().sort_values("Yield", ascending=False)
    fig = px.bar(
        avg, x="Crop", y="Yield",
        title="🌱 Average Yield by Crop",
        color="Crop",
        labels={"Yield": "Avg Yield (hg/ha)"},
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=350, showlegend=False)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)


def pie_chart(df):
    dist = df.groupby("Crop")["Yield"].sum().reset_index()
    fig = px.pie(
        dist, values="Yield", names="Crop",
        title="🥧 Crop Distribution by Total Yield",
        hole=0.45,
        color_discrete_sequence=["#0078ff", "#00c8ff", "#4dff9d", "#ffb347", "#ff6b6b"],
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=380)
    fig.update_traces(textfont_color="#e8f4ff", hovertemplate="%{label}<br>Total: %{value:,.0f}<br>%{percent}")
    st.plotly_chart(fig, use_container_width=True)


def scatter_plot(df):
    fig = px.scatter(
        df, x="Rainfall", y="Yield", color="Crop", size="Pesticides",
        title="🌧️ Rainfall vs Yield (bubble size = Pesticides)",
        hover_data=["Country", "Year", "Temperature"],
        labels={"Rainfall": "Rainfall (mm)", "Yield": "Yield (hg/ha)"},
        opacity=0.75,
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=400)
    st.plotly_chart(fig, use_container_width=True)


def heatmap(df):
    num_cols = ["Yield", "Rainfall", "Temperature", "Pesticides", "Year"]
    present = [c for c in num_cols if c in df.columns]
    corr = df[present].corr()

    # Use Plotly heatmap for theme consistency
    fig = px.imshow(
        corr,
        title="🔥 Correlation Heatmap",
        color_continuous_scale=["#001a4d", "#0078ff", "#00c8ff", "#4dff9d"],
        zmin=-1, zmax=1,
        text_auto=".2f",
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=420)
    fig.update_traces(textfont=dict(color="#e8f4ff"))
    st.plotly_chart(fig, use_container_width=True)


def show():
    df_full = get_data(st.session_state)

    st.markdown("""
    <h2 style='font-family:"Space Grotesk",sans-serif; color:#e8f4ff; margin-bottom:4px;'>
        📊 Data Analysis
    </h2>
    <p style='color:#7ab0d8; margin-bottom:24px;'>
        Explore, clean, and analyse the crop yield dataset with interactive charts.
    </p>
    """, unsafe_allow_html=True)

    data_upload_section()
    st.markdown("<br>", unsafe_allow_html=True)

    df = sidebar_filters(df_full)
    if df.empty:
        st.warning("No data matches current filters.")
        return

    # ── Cleaning log ──────────────────────────────────────────────────────────
    with st.expander("🧹 Data Cleaning Steps Applied"):
        st.markdown("""
        The following cleaning operations are applied automatically:
        - ✅ **Column standardisation** — renamed to internal schema
        - ✅ **Duplicate removal** — exact duplicate rows dropped
        - ✅ **Type coercion** — numeric columns cast to float
        - ✅ **Null handling** — rows with missing Yield or Year dropped
        - ✅ **Index reset** — clean sequential index
        """)

    dataset_preview(df)
    st.markdown("<br>", unsafe_allow_html=True)
    top_bottom_records(df)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>📈 Interactive Charts</div>", unsafe_allow_html=True)

    tabs = st.tabs(["📈 Line", "📊 Bar", "🥧 Pie", "🔵 Scatter", "🔥 Heatmap"])
    with tabs[0]: line_chart(df)
    with tabs[1]: bar_chart(df)
    with tabs[2]: pie_chart(df)
    with tabs[3]: scatter_plot(df)
    with tabs[4]: heatmap(df)

    # ── Download section ──────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>⬇️ Download Filtered Data</div>", unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Filtered Dataset as CSV",
        data=csv,
        file_name="crop_yield_filtered.csv",
        mime="text/csv",
    )
