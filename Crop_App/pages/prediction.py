# =============================================================================
# pages/prediction.py — Machine Learning Prediction Page
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle, os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_utils import get_data

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(5,14,31,0.6)",
    font_color="#b8d4f0",
    font_family="DM Sans",
    title_font_family="Space Grotesk",
    title_font_color="#e8f4ff",
    xaxis=dict(gridcolor="rgba(0,180,255,0.1)", zerolinecolor="rgba(0,180,255,0.2)"),
    yaxis=dict(gridcolor="rgba(0,180,255,0.1)", zerolinecolor="rgba(0,180,255,0.2)"),
)

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")


@st.cache_resource(show_spinner=False)
def train_models(df: pd.DataFrame):
    """Train Linear Regression and Random Forest on the dataset."""
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    features = ["Year", "Rainfall", "Temperature", "Pesticides"]
    present = [f for f in features if f in df.columns]
    target = "Yield"

    data = df[present + [target]].dropna()
    X = data[present]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_r2 = r2_score(y_test, lr_pred)
    lr_mae = mean_absolute_error(y_test, lr_pred)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))

    # Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_r2 = r2_score(y_test, rf_pred)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))

    # Feature importance
    feat_imp = pd.DataFrame({
        "Feature": present,
        "Importance": rf.feature_importances_,
    }).sort_values("Importance", ascending=False)

    # Actual vs Predicted (RF)
    avp = pd.DataFrame({"Actual": y_test.values, "RF Predicted": rf_pred,
                         "LR Predicted": lr.predict(X_test)})

    metrics = {
        "LR": {"r2": lr_r2, "mae": lr_mae, "rmse": lr_rmse},
        "RF": {"r2": rf_r2, "mae": rf_mae, "rmse": rf_rmse},
    }

    # Save best model
    best_model = rf if rf_r2 >= lr_r2 else lr
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": best_model, "features": present}, f)

    return lr, rf, metrics, feat_imp, avp, present


def model_metrics_cards(metrics):
    st.markdown("<div class='section-title'>📐 Model Performance Metrics</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    for col, model_name, color, bg in [
        (c1, "LR", "#0078ff", "rgba(0,120,255,0.12)"),
        (c2, "RF", "#4dff9d", "rgba(0,200,100,0.10)"),
    ]:
        m = metrics[model_name]
        label = "Linear Regression" if model_name == "LR" else "Random Forest"
        with col:
            st.markdown(f"""
            <div style='background:{bg}; border:1px solid {color}44;
                        border-radius:16px; padding:22px; position:relative; overflow:hidden;'>
                <div style='position:absolute;top:0;left:0;right:0;height:3px;
                            background:linear-gradient(90deg,{color},{color}aa);'></div>
                <div style='font-family:"Space Grotesk",sans-serif; font-size:1.1rem;
                            font-weight:600; color:#e8f4ff; margin-bottom:16px;'>
                    {'🔵' if model_name=='LR' else '🌲'} {label}
                </div>
                <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;'>
                    <div style='text-align:center;'>
                        <div style='font-family:"Space Grotesk",sans-serif; font-size:1.6rem;
                                    font-weight:700; color:{color};'>{m['r2']:.4f}</div>
                        <div style='font-size:0.7rem; color:#7ab0d8; text-transform:uppercase;
                                    letter-spacing:1px; margin-top:2px;'>R² Score</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-family:"Space Grotesk",sans-serif; font-size:1.6rem;
                                    font-weight:700; color:{color};'>{m['mae']:,.0f}</div>
                        <div style='font-size:0.7rem; color:#7ab0d8; text-transform:uppercase;
                                    letter-spacing:1px; margin-top:2px;'>MAE</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-family:"Space Grotesk",sans-serif; font-size:1.6rem;
                                    font-weight:700; color:{color};'>{m['rmse']:,.0f}</div>
                        <div style='font-size:0.7rem; color:#7ab0d8; text-transform:uppercase;
                                    letter-spacing:1px; margin-top:2px;'>RMSE</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def feature_importance_chart(feat_imp):
    fig = px.bar(
        feat_imp, x="Importance", y="Feature", orientation="h",
        title="🌲 Random Forest — Feature Importance",
        color="Importance",
        color_continuous_scale=["#003399", "#0078ff", "#4dff9d"],
    )
    fig.update_layout(**BASE, height=300, showlegend=False, coloraxis_showscale=False)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)


def actual_vs_predicted_chart(avp):
    fig = go.Figure()
    # Scatter: actual vs RF predicted
    fig.add_trace(go.Scatter(
        x=avp["Actual"], y=avp["RF Predicted"],
        mode="markers", name="RF Predicted",
        marker=dict(color="#4dff9d", size=6, opacity=0.7),
        hovertemplate="Actual: %{x:,.0f}<br>RF Pred: %{y:,.0f}",
    ))
    fig.add_trace(go.Scatter(
        x=avp["Actual"], y=avp["LR Predicted"],
        mode="markers", name="LR Predicted",
        marker=dict(color="#0078ff", size=5, opacity=0.6),
        hovertemplate="Actual: %{x:,.0f}<br>LR Pred: %{y:,.0f}",
    ))
    # Perfect fit line
    mn, mx = avp["Actual"].min(), avp["Actual"].max()
    fig.add_trace(go.Scatter(
        x=[mn, mx], y=[mn, mx], mode="lines", name="Perfect Fit",
        line=dict(color="#ffb347", dash="dash", width=1.5),
    ))
    fig.update_layout(
        **BASE, title="🎯 Actual vs Predicted Yield",
        xaxis_title="Actual Yield (hg/ha)",
        yaxis_title="Predicted Yield (hg/ha)",
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)


def prediction_form(rf_model, features, df):
    st.markdown("<div class='section-title'>🔮 Predict Crop Yield</div>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#7ab0d8;'>
        Enter environmental parameters below and click <strong>Predict</strong>
        to get the estimated crop yield.
    </p>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        year = st.number_input("📅 Year", min_value=1990, max_value=2050,
                                value=2024, step=1, key="pred_year")
        rainfall = st.number_input("🌧️ Rainfall (mm)", min_value=0.0, max_value=5000.0,
                                    value=float(df["Rainfall"].mean()),
                                    step=10.0, key="pred_rain")
    with c2:
        temperature = st.number_input("🌡️ Temperature (°C)", min_value=-10.0, max_value=50.0,
                                       value=float(df["Temperature"].mean()),
                                       step=0.5, key="pred_temp")
        pesticides = st.number_input("🧪 Pesticides (tonnes)", min_value=0.0, max_value=500000.0,
                                      value=float(df["Pesticides"].mean()),
                                      step=100.0, key="pred_pest")

    # Model selection
    model_choice = st.radio(
        "🤖 Select Model", ["Random Forest (Recommended)", "Linear Regression"],
        horizontal=True, key="pred_model",
    )

    if st.button("🚀 Predict Yield", key="pred_btn"):
        input_map = {"Year": year, "Rainfall": rainfall,
                     "Temperature": temperature, "Pesticides": pesticides}
        input_vals = [[input_map[f] for f in features]]
        model = rf_model  # already chosen above; we have both from cache

        with st.spinner("Calculating prediction..."):
            prediction = model.predict(input_vals)[0]

        # ── Result ────────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='pred-box'>
            <div style='font-size:1rem; color:#7ab0d8; margin-bottom:8px; letter-spacing:1px;'>
                PREDICTED CROP YIELD
            </div>
            <div class='pred-value'>{prediction:,.0f}</div>
            <div class='pred-label'>hg/ha (hectograms per hectare)</div>
            <div style='margin-top:12px; font-size:0.85rem; color:#a8d8b8;'>
                ≈ {prediction/10000:.2f} tonnes/ha &nbsp;|&nbsp;
                ≈ {prediction/100:.0f} kg/ha
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Comparison bar
        avg_yield = df["Yield"].mean()
        pct_diff = ((prediction - avg_yield) / avg_yield) * 100
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Your Prediction", f"{prediction:,.0f} hg/ha")
        c2.metric("Dataset Average", f"{avg_yield:,.0f} hg/ha")
        c3.metric("vs. Average", f"{pct_diff:+.1f}%",
                  delta=f"{'Above' if pct_diff>0 else 'Below'} average")

    # ── Download model ────────────────────────────────────────────────────────
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model_bytes = f.read()
        st.download_button(
            "💾 Download Trained Model (model.pkl)",
            data=model_bytes,
            file_name="model.pkl",
            mime="application/octet-stream",
        )


def show():
    df = get_data(st.session_state)

    st.markdown("""
    <h2 style='font-family:"Space Grotesk",sans-serif; color:#e8f4ff; margin-bottom:4px;'>
        🤖 Machine Learning Prediction
    </h2>
    <p style='color:#7ab0d8; margin-bottom:24px;'>
        Trained on historical yield data. Predict future crop yields from environmental parameters.
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("🔄 Training models — please wait..."):
        try:
            lr, rf, metrics, feat_imp, avp, features = train_models(df)
        except Exception as e:
            st.error(f"Model training failed: {e}")
            return

    st.success("✅ Models trained successfully on the dataset!")

    # ── Metrics ───────────────────────────────────────────────────────────────
    model_metrics_cards(metrics)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 2])
    with c1:
        feature_importance_chart(feat_imp)
    with c2:
        actual_vs_predicted_chart(avp)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Prediction form (use best model = RF) ─────────────────────────────────
    prediction_form(rf, features, df)

    # ── Model explanation ─────────────────────────────────────────────────────
    with st.expander("📖 How the Models Work"):
        st.markdown("""
        ### 🔵 Linear Regression
        Fits a straight-line relationship between input features and yield.
        Fast and interpretable — best when relationships are roughly linear.

        **Formula:**  
        `Yield = β₀ + β₁×Year + β₂×Rainfall + β₃×Temperature + β₄×Pesticides`

        ---

        ### 🌲 Random Forest Regressor
        An ensemble of 100 decision trees. Each tree is trained on a random
        bootstrap sample of data. Final prediction = average of all trees.
        Captures non-linear interactions between features.

        **Key advantages:**
        - Handles outliers well
        - Provides feature importance
        - Resistant to overfitting
        - Higher accuracy on complex datasets

        ---

        ### 📐 Evaluation Metrics
        | Metric | Meaning |
        |---|---|
        | **R²** | Proportion of variance explained (1.0 = perfect) |
        | **MAE** | Average absolute error in hg/ha |
        | **RMSE** | Root mean squared error — penalises large errors more |
        """)
