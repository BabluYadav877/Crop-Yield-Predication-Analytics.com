# 🌾 CropIQ — Crop Yield Analytics Dashboard
### MCA / BCA Final Year Project | Professional Streamlit Application

---

## 📋 Project Overview

CropIQ is a professional-grade, multi-page data science dashboard built with Python and Streamlit.
It analyses global crop yield data across countries, crops, and years — combining advanced EDA,
12+ interactive visualizations, and machine learning predictions in a modern blue-themed UI.

---

## 🗂️ Project Structure

```
crop_yield_dashboard/
│
├── app.py                    ← Main entry point (run this)
├── crop_yield_data.csv       ← Bundled dataset
├── requirements.txt          ← Python dependencies
├── model.pkl                 ← Generated after first ML page visit
│
├── pages/
│   ├── __init__.py
│   ├── home.py               ← Page 1: Home & KPI Dashboard
│   ├── data_analysis.py      ← Page 2: Data Analysis & EDA
│   ├── visualizations.py     ← Page 3: Visualization Dashboard
│   ├── prediction.py         ← Page 4: ML Prediction
│   └── upload_settings.py    ← Page 5: Upload & Settings
│
└── utils/
    ├── __init__.py
    └── data_utils.py         ← Shared data helpers
```

---

## 🚀 How to Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the app
```bash
streamlit run app.py
```

### Step 3 — Open in browser
Streamlit will automatically open `http://localhost:8501`

---

## 📄 Pages

| # | Page | Description |
|---|------|-------------|
| 1 | 🏠 Home | KPI cards, overview charts, quick insights |
| 2 | 📊 Data Analysis | Dataset preview, cleaning, EDA charts |
| 3 | 📈 Visualizations | 8+ advanced Plotly charts with animation |
| 4 | 🤖 ML Prediction | Train LR & RF, predict yield, download model |
| 5 | 📂 Upload & Settings | Upload CSV, validate, reset, project info |

---

## 🔬 ML Models Trained

- **Linear Regression** — baseline, interpretable
- **Random Forest** (100 estimators) — higher accuracy, feature importance

**Input features:** Year, Rainfall (mm), Temperature (°C), Pesticides (tonnes)  
**Target:** Yield (hg/ha)

---

## 🎨 Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Streamlit | Web app framework |
| Plotly | Interactive charts |
| Matplotlib / Seaborn | Static charts |
| scikit-learn | Machine learning |
| pandas / numpy | Data processing |

---

## 👤 Developer

**Department of Computer Applications**  
MCA Final Year Project  
CropIQ Analytics Platform v2.0
