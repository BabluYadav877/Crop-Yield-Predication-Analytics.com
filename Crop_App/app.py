# =============================================================================
# CROP YIELD ANALYTICS DASHBOARD - Main Application Entry Point
# Professional Multi-Page Streamlit App
# =============================================================================

import streamlit as st

# ── Page config must be FIRST Streamlit call ──────────────────────────────────
st.set_page_config(
    page_title="CropIQ — Crop Yield Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS injected once from main app ────────────────────────────────────
def inject_global_css():
    st.markdown("""
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* ── App Background ── */
    .stApp {
        background: linear-gradient(135deg, #050e1f 0%, #0a1628 50%, #0d1f3c 100%);
        min-height: 100vh;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071223 0%, #0a1e3d 100%) !important;
        border-right: 1px solid rgba(0,180,255,0.15);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #a8c8e8 !important;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0f0ff !important;
    }

    /* ── Headers ── */
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #e8f4ff !important;
    }
    p, li, span, label {
        color: #b8d4f0 !important;
    }

    /* ── KPI Card ── */
    .kpi-card {
        background: linear-gradient(135deg, rgba(0,120,255,0.12), rgba(0,60,160,0.08));
        border: 1px solid rgba(0,180,255,0.25);
        border-radius: 16px;
        padding: 22px 20px;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0078ff, #00c8ff, #0078ff);
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,120,255,0.25);
    }
    .kpi-icon { font-size: 2rem; margin-bottom: 6px; }
    .kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #00c8ff !important;
        line-height: 1;
    }
    .kpi-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #7ab0d8 !important;
        margin-top: 4px;
    }
    .kpi-delta {
        font-size: 0.75rem;
        color: #4dff9d !important;
        margin-top: 6px;
    }

    /* ── Section title ── */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #e8f4ff !important;
        border-left: 4px solid #0078ff;
        padding-left: 12px;
        margin: 24px 0 16px 0;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    .dataframe { color: #b8d4f0 !important; }

    /* ── Metric widget overrides ── */
    [data-testid="metric-container"] {
        background: rgba(0,80,200,0.1);
        border: 1px solid rgba(0,180,255,0.2);
        border-radius: 12px;
        padding: 12px;
    }
    [data-testid="metric-container"] label {
        color: #7ab0d8 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00c8ff !important;
        font-family: 'Space Grotesk', sans-serif;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0,40,100,0.4);
        border-radius: 10px;
        padding: 4px;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        color: #7ab0d8 !important;
        border-radius: 8px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0055cc, #0078ff) !important;
        color: #ffffff !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #0055cc, #0078ff) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 28px !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 15px rgba(0,120,255,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,120,255,0.5) !important;
    }

    /* ── Select boxes & inputs ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(0,40,100,0.3) !important;
        border: 1px solid rgba(0,180,255,0.3) !important;
        border-radius: 10px !important;
        color: #e8f4ff !important;
    }
    .stNumberInput input, .stTextInput input {
        background: rgba(0,40,100,0.3) !important;
        border: 1px solid rgba(0,180,255,0.3) !important;
        border-radius: 10px !important;
        color: #e8f4ff !important;
    }

    /* ── Success / Info / Warning boxes ── */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(0,180,255,0.15) !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: rgba(0,40,100,0.2) !important;
        border: 2px dashed rgba(0,180,255,0.35) !important;
        border-radius: 14px !important;
    }

    /* ── Prediction result box ── */
    .pred-box {
        background: linear-gradient(135deg, rgba(0,200,100,0.12), rgba(0,120,255,0.08));
        border: 1px solid rgba(0,200,100,0.35);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
    }
    .pred-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #4dff9d !important;
    }
    .pred-label {
        font-size: 1rem;
        color: #a8d8b8 !important;
        margin-top: 6px;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 40px;
        border-top: 1px solid rgba(0,180,255,0.15);
        color: #4a7090 !important;
        font-size: 0.82rem;
    }
    .footer a { color: #0078ff !important; text-decoration: none; }

    /* ── Scroll bar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #050e1f; }
    ::-webkit-scrollbar-thumb { background: #0055cc; border-radius: 3px; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(0,40,100,0.3) !important;
        border-radius: 10px !important;
        color: #b8d4f0 !important;
    }

    /* ── Hide default menu / footer ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


inject_global_css()

# ── Navigation state ─────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# ── Sidebar brand + nav ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <div style='font-size:2.8rem;'>🌾</div>
        <div style='font-family:"Space Grotesk",sans-serif; font-size:1.4rem;
                    font-weight:700; color:#e8f4ff; letter-spacing:1px;'>CropIQ</div>
        <div style='font-size:0.72rem; color:#4a7090; letter-spacing:2px;
                    text-transform:uppercase; margin-top:2px;'>Yield Analytics Platform</div>
    </div>
    <hr style='margin: 8px 0 20px 0;'>
    """, unsafe_allow_html=True)

    pages = [
        "🏠 Home",
        "📊 Data Analysis",
        "📈 Visualizations",
        "🤖 ML Prediction",
        "📂 Upload & Settings",
    ]
    for pg in pages:
        active = st.session_state.page == pg
        if st.button(
            pg,
            key=f"nav_{pg}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.page = pg
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.72rem; color:#3a5f7f; text-align:center; padding:8px 0;'>
        Version 2.0 &nbsp;|&nbsp; Academic Edition<br>
        <span style='color:#0078ff;'>MCA Final Year Project</span>
    </div>
    """, unsafe_allow_html=True)

# ── Route to pages ────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "🏠 Home":
    from pages.home import show
    show()
elif page == "📊 Data Analysis":
    from pages.data_analysis import show
    show()
elif page == "📈 Visualizations":
    from pages.visualizations import show
    show()
elif page == "🤖 ML Prediction":
    from pages.prediction import show
    show()
elif page == "📂 Upload & Settings":
    from pages.upload_settings import show
    show()

# ── Global footer ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='footer'>
    🌾 <strong>CropIQ Analytics Dashboard</strong> &nbsp;|&nbsp;
    Built with Streamlit &amp; Python &nbsp;|&nbsp;
    MCA Final Year Project &nbsp;|&nbsp;
    <a href='#'>Department of Computer Applications</a>
</div>
""", unsafe_allow_html=True)
