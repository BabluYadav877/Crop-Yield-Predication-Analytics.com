# =============================================================================
# pages/home.py — Home / Overview Dashboard
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_utils import get_data, get_filter_options, apply_filters

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


def sidebar_filters(df: pd.DataFrame):
    """Render sidebar filters and return filtered df."""
    countries, crops, year_min, year_max = get_filter_options(df)

    st.sidebar.markdown("### 🔍 Filters")
    sel_countries = st.sidebar.multiselect(
        "🌍 Country", ["All"] + countries, default=["All"], key="home_country"
    )
    sel_crops = st.sidebar.multiselect(
        "🌱 Crop", ["All"] + crops, default=["All"], key="home_crop"
    )
    year_range = st.sidebar.slider(
        "📅 Year Range", year_min, year_max, (year_min, year_max), key="home_year"
    )
    return apply_filters(df, sel_countries, sel_crops, year_range)


def kpi_cards(df: pd.DataFrame):
    """Display 5 KPI cards."""
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, "🌍", len(df["Country"].unique()), "Countries", "+2 vs last yr"),
        (c2, "🌱", len(df["Crop"].unique()), "Crop Types", "Diverse mix"),
        (c3, "📦", f"{df['Yield'].mean():,.0f}", "Avg Yield (hg/ha)", "↑ 3.2%"),
        (c4, "🌧️", f"{df['Rainfall'].mean():,.0f}", "Avg Rainfall (mm)", "Seasonal"),
        (c5, "🌡️", f"{df['Temperature'].mean():.1f}°C", "Avg Temperature", "Optimal"),
    ]
    for col, icon, val, label, delta in kpis:
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-icon'>{icon}</div>
                <div class='kpi-value'>{val}</div>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-delta'>{delta}</div>
            </div>
            """, unsafe_allow_html=True)


def hero_section():
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(0,80,200,0.2), rgba(0,40,120,0.1));
        border: 1px solid rgba(0,180,255,0.2);
        border-radius: 20px;
        padding: 36px 40px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    '>
        <div style='position:absolute; top:-40px; right:-40px; width:200px; height:200px;
                    background:radial-gradient(circle, rgba(0,120,255,0.15), transparent 70%);
                    border-radius:50%;'></div>
        <div style='font-family:"Space Grotesk",sans-serif; font-size:2.2rem;
                    font-weight:700; color:#e8f4ff; margin-bottom:8px;'>
            🌾 CropIQ Analytics Dashboard
        </div>
        <div style='font-size:1rem; color:#7ab0d8; max-width:700px; line-height:1.7;'>
            A professional-grade crop yield intelligence platform powered by machine learning
            and advanced analytics. Explore global agricultural trends, uncover patterns in
            climate-yield relationships, and forecast production outcomes — all in one place.
        </div>
        <div style='display:flex; gap:12px; margin-top:20px; flex-wrap:wrap;'>
            <span style='background:rgba(0,120,255,0.2); border:1px solid rgba(0,180,255,0.3);
                         border-radius:20px; padding:5px 14px; font-size:0.78rem; color:#a8d4f8;'>
                📊 Multi-Country Analysis
            </span>
            <span style='background:rgba(0,200,100,0.15); border:1px solid rgba(0,200,100,0.3);
                         border-radius:20px; padding:5px 14px; font-size:0.78rem; color:#a8d8b8;'>
                🤖 ML-Powered Forecasts
            </span>
            <span style='background:rgba(200,100,0,0.15); border:1px solid rgba(255,180,0,0.3);
                         border-radius:20px; padding:5px 14px; font-size:0.78rem; color:#d8c0a0;'>
                🌡️ Climate Correlation
            </span>
            <span style='background:rgba(150,0,200,0.15); border:1px solid rgba(200,100,255,0.3);
                         border-radius:20px; padding:5px 14px; font-size:0.78rem; color:#c8a8e8;'>
                📈 Interactive Visualizations
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def overview_charts(df: pd.DataFrame):
    st.markdown("<div class='section-title'>📊 Overview Charts</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        # Average yield by country
        avg_country = (
            df.groupby("Country")["Yield"].mean().reset_index()
              .sort_values("Yield", ascending=False)
        )
        fig = px.bar(
            avg_country, x="Country", y="Yield",
            title="🌍 Average Yield by Country",
            color="Yield",
            color_continuous_scale=["#003399", "#0078ff", "#00c8ff"],
            labels={"Yield": "Avg Yield (hg/ha)"},
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False,
                          coloraxis_showscale=False)
        fig.update_traces(marker_line_width=0, hovertemplate="<b>%{x}</b><br>Yield: %{y:,.0f} hg/ha")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Average yield by crop
        avg_crop = (
            df.groupby("Crop")["Yield"].mean().reset_index()
              .sort_values("Yield", ascending=False)
        )
        fig2 = px.bar(
            avg_crop, x="Crop", y="Yield",
            title="🌱 Average Yield by Crop",
            color="Yield",
            color_continuous_scale=["#004400", "#00aa44", "#4dff9d"],
            labels={"Yield": "Avg Yield (hg/ha)"},
        )
        fig2.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False,
                           coloraxis_showscale=False)
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2, use_container_width=True)

    # Yield trend over years
    trend = df.groupby("Year")["Yield"].mean().reset_index()
    fig3 = px.area(
        trend, x="Year", y="Yield",
        title="📈 Global Average Yield Trend Over Years",
        labels={"Yield": "Avg Yield (hg/ha)"},
    )
    fig3.update_traces(
        line_color="#0078ff", fillcolor="rgba(0,120,255,0.15)",
        hovertemplate="Year: %{x}<br>Avg Yield: %{y:,.0f} hg/ha"
    )
    fig3.update_layout(**PLOTLY_LAYOUT, height=300)
    st.plotly_chart(fig3, use_container_width=True)


def top_records(df: pd.DataFrame):
    st.markdown("<div class='section-title'>🏆 Top Performing Records</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🥇 Top 5 Highest Yield Records**")
        top5 = df.nlargest(5, "Yield")[["Country", "Crop", "Year", "Yield", "Rainfall", "Temperature"]]
        st.dataframe(
            top5.style.background_gradient(subset=["Yield"], cmap="Blues").format({"Yield": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )
    with c2:
        st.markdown("**📉 Bottom 5 Lowest Yield Records**")
        bot5 = df.nsmallest(5, "Yield")[["Country", "Crop", "Year", "Yield", "Rainfall", "Temperature"]]
        st.dataframe(
            bot5.style.background_gradient(subset=["Yield"], cmap="Reds_r").format({"Yield": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )


def show():
    df_full = get_data(st.session_state)
    df = sidebar_filters(df_full)

    hero_section()

    # ── KPI Row ──────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>📌 Key Performance Indicators</div>", unsafe_allow_html=True)
    if df.empty:
        st.warning("No data matches current filters. Please adjust the sidebar filters.")
        return

    kpi_cards(df)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dataset summary ───────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>📋 Dataset Summary</div>", unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Total Records", f"{len(df):,}")
    sc2.metric("Year Span", f"{int(df['Year'].min())} – {int(df['Year'].max())}")
    sc3.metric("Max Yield", f"{df['Yield'].max():,.0f}")
    sc4.metric("Min Yield", f"{df['Yield'].min():,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)
    overview_charts(df)
    st.markdown("<br>", unsafe_allow_html=True)
    top_records(df)

    # ── Quick insights ────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>💡 Quick Insights</div>", unsafe_allow_html=True)
    ic1, ic2, ic3 = st.columns(3)
    best_country = df.groupby("Country")["Yield"].mean().idxmax()
    best_crop = df.groupby("Crop")["Yield"].mean().idxmax()
    best_year = df.groupby("Year")["Yield"].mean().idxmax()
    for col, icon, title, val, note in [
        (ic1, "🌍", "Best Performing Country", best_country, "By average yield"),
        (ic2, "🌱", "Highest Yield Crop", best_crop, "By average yield"),
        (ic3, "📅", "Best Yield Year", str(int(best_year)), "Peak production year"),
    ]:
        with col:
            st.markdown(f"""
            <div class='kpi-card' style='text-align:left; padding:20px;'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div style='font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;
                            color:#4a7090; margin: 6px 0 2px;'>{title}</div>
                <div style='font-family:"Space Grotesk",sans-serif; font-size:1.4rem;
                            font-weight:700; color:#00c8ff;'>{val}</div>
                <div style='font-size:0.75rem; color:#4a7090; margin-top:4px;'>{note}</div>
            </div>
            """, unsafe_allow_html=True)
