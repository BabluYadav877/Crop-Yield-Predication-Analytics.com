# =============================================================================
# pages/visualizations.py — Advanced Visualization Dashboard
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_utils import get_data, get_filter_options, apply_filters

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(5,14,31,0.6)",
    font_color="#b8d4f0",
    font_family="DM Sans",
    title_font_family="Space Grotesk",
    title_font_color="#e8f4ff",
    colorway=["#0078ff", "#00c8ff", "#4dff9d", "#ffb347", "#ff6b6b", "#c084fc", "#f97316"],
    legend=dict(bgcolor="rgba(0,20,60,0.6)", bordercolor="rgba(0,180,255,0.2)", borderwidth=1),
    xaxis=dict(gridcolor="rgba(0,180,255,0.1)", zerolinecolor="rgba(0,180,255,0.2)"),
    yaxis=dict(gridcolor="rgba(0,180,255,0.1)", zerolinecolor="rgba(0,180,255,0.2)"),
)


def sidebar_filters(df):
    countries, crops, year_min, year_max = get_filter_options(df)
    st.sidebar.markdown("### 🔍 Filters")
    sel_c = st.sidebar.multiselect("🌍 Country", ["All"] + countries, default=["All"], key="viz_country")
    sel_cr = st.sidebar.multiselect("🌱 Crop", ["All"] + crops, default=["All"], key="viz_crop")
    yr = st.sidebar.slider("📅 Year Range", year_min, year_max, (year_min, year_max), key="viz_year")
    return apply_filters(df, sel_c, sel_cr, yr)


def multi_line_chart(df):
    """Yield trend per crop over years."""
    trend = df.groupby(["Year", "Crop"])["Yield"].mean().reset_index()
    fig = px.line(
        trend, x="Year", y="Yield", color="Crop",
        title="📈 Yield Trend by Crop Over Years",
        markers=True,
        labels={"Yield": "Avg Yield (hg/ha)"},
    )
    fig.update_traces(line_width=2.2)
    fig.update_layout(**BASE, height=400)
    st.plotly_chart(fig, use_container_width=True)


def column_chart(df):
    """Grouped bar — crop yield per country."""
    avg = df.groupby(["Country", "Crop"])["Yield"].mean().reset_index()
    fig = px.bar(
        avg, x="Country", y="Yield", color="Crop",
        barmode="group",
        title="📊 Crop Yield by Country (Grouped)",
        labels={"Yield": "Avg Yield (hg/ha)"},
    )
    fig.update_layout(**BASE, height=420)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)


def area_chart(df):
    """Stacked area chart — yield by country over time."""
    trend = df.groupby(["Year", "Country"])["Yield"].mean().reset_index()
    fig = px.area(
        trend, x="Year", y="Yield", color="Country",
        title="🗺️ Yield by Country — Stacked Area Chart",
        labels={"Yield": "Avg Yield (hg/ha)"},
    )
    fig.update_layout(**BASE, height=420)
    st.plotly_chart(fig, use_container_width=True)


def donut_chart(df):
    """Donut — share of yield per country."""
    country_share = df.groupby("Country")["Yield"].sum().reset_index()
    fig = px.pie(
        country_share, values="Yield", names="Country",
        title="🌍 Country Share of Total Yield",
        hole=0.52,
    )
    fig.update_layout(**BASE, height=400)
    fig.update_traces(textfont_color="#e8f4ff",
                      hovertemplate="%{label}<br>Total: %{value:,.0f}<br>Share: %{percent}")
    st.plotly_chart(fig, use_container_width=True)


def scatter_matrix(df):
    """Scatter matrix of numeric variables."""
    cols = [c for c in ["Yield", "Rainfall", "Temperature", "Pesticides"] if c in df.columns]
    fig = px.scatter_matrix(
        df, dimensions=cols, color="Crop",
        title="🔵 Scatter Matrix — Numeric Variables",
        opacity=0.65,
    )
    fig.update_traces(diagonal_visible=False, marker_size=4)
    fig.update_layout(**BASE, height=550)
    st.plotly_chart(fig, use_container_width=True)


def box_plot(df):
    """Box plot — yield distribution by crop."""
    fig = px.box(
        df, x="Crop", y="Yield", color="Crop",
        title="📦 Yield Distribution by Crop (Box Plot)",
        labels={"Yield": "Yield (hg/ha)"},
    )
    fig.update_layout(**BASE, height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def violin_plot(df):
    """Violin — yield distribution by country."""
    fig = px.violin(
        df, x="Country", y="Yield", color="Country",
        box=True, points="outliers",
        title="🎻 Yield Distribution by Country (Violin)",
        labels={"Yield": "Yield (hg/ha)"},
    )
    fig.update_layout(**BASE, height=440, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def bubble_chart(df):
    """Bubble — Temperature vs Yield, bubble = Rainfall."""
    fig = px.scatter(
        df, x="Temperature", y="Yield",
        size="Rainfall", color="Crop",
        hover_data=["Country", "Year"],
        title="🌡️ Temperature vs Yield (Bubble = Rainfall)",
        labels={"Yield": "Yield (hg/ha)", "Temperature": "Temperature (°C)"},
        opacity=0.8,
    )
    fig.update_layout(**BASE, height=440)
    st.plotly_chart(fig, use_container_width=True)


def funnel_chart(df):
    """Funnel — top countries ranked by avg yield."""
    top = (
        df.groupby("Country")["Yield"].mean().reset_index()
          .sort_values("Yield", ascending=False).head(8)
    )
    fig = px.funnel(
        top, x="Yield", y="Country",
        title="🏆 Country Yield Rankings (Funnel View)",
        color_discrete_sequence=["#0078ff"],
    )
    fig.update_layout(**BASE, height=380)
    st.plotly_chart(fig, use_container_width=True)


def animated_scatter(df):
    """Animated scatter — Rainfall vs Yield over years."""
    fig = px.scatter(
        df, x="Rainfall", y="Yield", color="Crop",
        animation_frame="Year", animation_group="Country",
        size="Pesticides", hover_name="Country",
        title="🎬 Animated: Rainfall vs Yield Over Years",
        labels={"Yield": "Yield (hg/ha)", "Rainfall": "Rainfall (mm)"},
        range_x=[df["Rainfall"].min() - 50, df["Rainfall"].max() + 50],
        range_y=[df["Yield"].min() - 2000, df["Yield"].max() + 5000],
        opacity=0.8,
    )
    fig.update_layout(**BASE, height=480)
    st.plotly_chart(fig, use_container_width=True)


def show():
    df_full = get_data(st.session_state)

    st.markdown("""
    <h2 style='font-family:"Space Grotesk",sans-serif; color:#e8f4ff; margin-bottom:4px;'>
        📈 Visualization Dashboard
    </h2>
    <p style='color:#7ab0d8; margin-bottom:24px;'>
        Advanced interactive charts with dynamic filters. Every chart updates in real-time.
    </p>
    """, unsafe_allow_html=True)

    df = sidebar_filters(df_full)
    if df.empty:
        st.warning("No data matches current filters.")
        return

    # ── Summary mini-KPIs ─────────────────────────────────────────────────────
    kc = st.columns(4)
    kc[0].metric("Records", f"{len(df):,}")
    kc[1].metric("Countries", df["Country"].nunique())
    kc[2].metric("Crops", df["Crop"].nunique())
    kc[3].metric("Year Span", f"{int(df['Year'].min())}–{int(df['Year'].max())}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs for chart categories ─────────────────────────────────────────────
    t1, t2, t3, t4 = st.tabs(["📈 Trends", "📊 Comparisons", "🔵 Distributions", "🎬 Animation"])

    with t1:
        multi_line_chart(df)
        st.markdown("<br>", unsafe_allow_html=True)
        area_chart(df)

    with t2:
        column_chart(df)
        c1, c2 = st.columns(2)
        with c1: donut_chart(df)
        with c2: funnel_chart(df)

    with t3:
        c1, c2 = st.columns(2)
        with c1: box_plot(df)
        with c2: violin_plot(df)
        st.markdown("<br>", unsafe_allow_html=True)
        bubble_chart(df)
        st.markdown("<br>", unsafe_allow_html=True)
        scatter_matrix(df)

    with t4:
        st.info("▶️ Use the play button below the chart to animate through years.")
        animated_scatter(df)

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Chart Data as CSV", csv, "viz_export.csv", "text/csv")
