"""
Module 4 — System Integration, Testing and Project Finalization — Dark Theme
"""

import streamlit as st
import time
from data.demo_data import get_system_services_status, get_demo_test_suite_results
from components.metrics import render_demo_banner
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Module 4 — System Integration and Testing | EcoAir Intelligence",
    page_icon=None, layout="wide"
)

# ── Dark CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #F8FAFC !important; }
section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
section[data-testid="stSidebar"] * { color: #64748B !important; }
.block-container { padding-top: 1.8rem; padding-bottom: 2rem; max-width: 1380px; }
[data-testid="stMetric"] { background: #FFFFFF !important; border: 1px solid #334155 !important; border-radius: 8px; }
[data-testid="stMetricLabel"] { color: #64748B !important; }
[data-testid="stMetricValue"] { color: #0F172A !important; }
.stButton > button { background: #FFFFFF !important; border: 1px solid #334155 !important; color: #334155 !important; border-radius: 5px; font-weight: 600; }
.stButton > button[kind="primary"] { background: #1D4ED8 !important; border-color: #2563EB !important; color: white !important; }
[data-testid="stExpander"] { background: #FFFFFF !important; border: 1px solid #334155 !important; border-radius: 6px; }
details summary { color: #334155 !important; font-weight: 600; font-size: 0.88rem; }
[data-testid="stProgress"] > div { background: #334155; }
[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, #2563EB, #7C3AED) !important; }
[data-testid="stTable"] table { background: #FFFFFF; color: #334155; }
[data-testid="stTable"] th { background: #334155 !important; color: #64748B !important; }
[data-testid="stTable"] td { border-color: #334155 !important; }
hr { border-color: #334155 !important; }
h1, h2, h3, h4 { color: #0F172A !important; }
[data-testid="stCaptionContainer"] { color: #64748B !important; }
[data-testid="stSpinner"] { color: #60A5FA !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #F8FAFC; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Page Header ────────────────────────────────────────────────────────────
render_sidebar()
st.markdown("## Module 4 — System Integration, Testing and Project Finalization")
st.caption(
    "End-to-end pipeline health monitoring, automated quality assurance, "
    "system architecture documentation, and Infosys Springboard internship project milestone tracking."
)
render_demo_banner("Module 4 — Integration and QA Dashboard")
st.markdown("---")

# ── 4.1 Service Status Matrix ──────────────────────────────────────────────
st.markdown("### 4.1  Subsystem Integration Status")
st.caption("Operational status across all platform services in the current development phase.")

services = get_system_services_status()

status_color_map = {
    "Active":           "#16A34A",
    "Demo Mode":        "#60A5FA",
    "Pending Training": "#FBBF24",
    "Not Connected":    "#64748B",
}

status_cols = st.columns(len(services))
for idx, s in enumerate(services):
    color = status_color_map.get(s["status"], "#64748B")
    with status_cols[idx]:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #334155;
                            border-top:3px solid {color}; border-radius:6px;
                            padding:10px 8px; text-align:center; min-height:130px;">
                <div style="font-size:0.72rem; font-weight:600; color:#64748B;
                            min-height:30px; line-height:1.3; margin-bottom:6px;">
                    {s['service']}
                </div>
                <span style="background:{color}18; border:1px solid {color}44; color:{color};
                      font-size:0.67rem; font-weight:700; padding:2px 7px; border-radius:3px;
                      display:inline-block;">{s['status']}</span>
                <div style="font-size:0.62rem; color:#334155; margin-top:6px;">{s['module']}</div>
            </div>""",
            unsafe_allow_html=True
        )

with st.expander("View Full Service Endpoint and Integration Details"):
    st.table([
        {
            "Subsystem": s["service"],
            "Module": s["module"],
            "Status": s["status"],
            "Endpoint / Provider": s["endpoint"],
            "Notes": s["notes"]
        }
        for s in services
    ])

# ── 4.2 Pipeline Flow ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 4.2  End-to-End System Dataflow Pipeline")
st.caption("Logical execution sequence from location capture through inference, advisory, and push delivery.")

pipeline_steps = [
    ("01", "User Location",     "GPS / Manual Input",       "#3B82F6"),
    ("02", "AQI Ingestion",     "OpenAQ / CPCB Feed",       "#0EA5E9"),
    ("03", "Weather & Traffic", "OWM + Speed Index",        "#06B6D4"),
    ("04", "AQI Prediction",    "LSTM / GRU Inference",     "#8B5CF6"),
    ("05", "Route Analysis",    "Exposure Scoring",         "#A855F7"),
    ("06", "Travel Advisory",   "Risk Classification",      "#EC4899"),
    ("07", "Push Notification", "FCM Broadcast",            "#F97316"),
    ("08", "Dashboard UI",      "Streamlit / PWA",          "#22C55E"),
]

pipe_cols = st.columns(len(pipeline_steps))
for i, (num, title, detail, color) in enumerate(pipeline_steps):
    with pipe_cols[i]:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:8px;
                            padding:12px 6px; text-align:center;">
                <div style="width:26px; height:26px; background:{color}22; border:1px solid {color}55;
                            color:{color}; border-radius:50%; font-size:0.68rem; font-weight:800;
                            display:flex; align-items:center; justify-content:center;
                            margin:0 auto 6px auto;">{num}</div>
                <div style="font-size:0.75rem; font-weight:700; color:#334155; line-height:1.3;">
                    {title}
                </div>
                <div style="font-size:0.62rem; color:#64748B; margin-top:3px;">{detail}</div>
            </div>""",
            unsafe_allow_html=True
        )

st.markdown(
    "<div style='text-align:center; margin-top:10px; font-size:0.80rem; color:#334155; line-height:2;'>"
    "User Location &rarr; AQI Ingestion &rarr; Weather + Traffic &rarr; AQI Prediction "
    "&rarr; Route Analysis &rarr; Travel Advisory &rarr; Push Notification &rarr; Dashboard"
    "</div>",
    unsafe_allow_html=True
)

# ── 4.3 Test Suite ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 4.3  Automated Test Suite and Quality Assurance")

t_col, runner_col = st.columns([1.6, 1.0])
test_results = get_demo_test_suite_results()

with t_col:
    for t in test_results:
        pass_color   = "#16A34A" if t["result"] == "PASS" else "#FBBF24"
        border_color = "#14532D" if t["result"] == "PASS" else "#78350F"
        bg           = "#0A1A0A" if t["result"] == "PASS" else "#1A1200"

        st.markdown(
            f"""<div style="background:{bg}; border:1px solid {border_color};
                            border-left:4px solid {pass_color}; border-radius:6px;
                            padding:10px 14px; margin-bottom:8px;
                            display:flex; justify-content:space-between; align-items:center; gap:12px;">
                <div style="flex:1;">
                    <span style="font-family:monospace; font-size:0.70rem; background:#F1F5F9;
                          padding:2px 6px; border-radius:3px; color:#64748B;">{t['id']}</span>
                    <b style="font-size:0.84rem; color:#0F172A; margin-left:8px;">{t['name']}</b>
                    <div style="font-size:0.74rem; color:#64748B; margin-top:3px;">
                        {t['component']} — {t['details']}
                    </div>
                </div>
                <div style="text-align:right; min-width:95px; flex-shrink:0;">
                    <span style="background:{pass_color}22; border:1px solid {pass_color}44;
                          color:{pass_color}; font-size:0.68rem; font-weight:800;
                          padding:3px 8px; border-radius:3px;">{t['result']}</span>
                    <div style="font-size:0.64rem; color:#334155; margin-top:3px;">{t['mode']}</div>
                </div>
            </div>""",
            unsafe_allow_html=True
        )

with runner_col:
    st.subheader("Test Runner")
    st.markdown(
        f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:6px; padding:14px;">
            <div style="font-size:0.85rem; font-weight:600; color:#334155; margin-bottom:6px;">
                Simulated Test Automation Engine
            </div>
            <p style="font-size:0.78rem; color:#64748B; margin:0 0 12px 0; line-height:1.5;">
                Executes synthetic validation sweeps across coordinate parsers,
                AQI sub-index calculations, and API response schemas.
            </p>
        </div>""",
        unsafe_allow_html=True
    )
    if st.button("Run Automated QA Test Suite", use_container_width=True, type="primary"):
        with st.spinner("Executing simulated test harnesses..."):
            time.sleep(1.0)
        st.success("4 PASSED, 2 PENDING model / FCM artifacts.")

    st.markdown("---")
    st.markdown("**Result Summary**")
    mc1, mc2, mc3 = st.columns(3)
    with mc1: st.metric("PASS",    "4")
    with mc2: st.metric("PENDING", "2")
    with mc3: st.metric("FAIL",    "0")

# ── 4.4 Project Progress ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 4.4  Project Implementation Progress and Roadmap")

milestones = [
    {"name": "Module 1 — Location and AQI Integration",  "weeks": "Weeks 1–2", "pct": 40, "phase": "UI and Schema Ready"},
    {"name": "Module 2 — Predictive AQI Forecasting",    "weeks": "Weeks 3–4", "pct": 25, "phase": "UI and Tensor Specs Ready"},
    {"name": "Module 3 — Route Advisory and Push Hub",   "weeks": "Weeks 5–6", "pct": 30, "phase": "Routing UI Ready"},
    {"name": "Module 4 — Integration and Documentation", "weeks": "Weeks 7–8", "pct": 45, "phase": "Pipeline and Docs Active"},
]

for m in milestones:
    c1, c2 = st.columns([1.5, 2.5])
    with c1:
        st.markdown(
            f"**{m['name']}**  \n"
            f"<span style='font-size:0.78rem; color:#334155;'>{m['weeks']} — {m['phase']}</span>",
            unsafe_allow_html=True
        )
    with c2:
        st.progress(m["pct"] / 100, text=f"{m['pct']}%  Initial UI Stage")

# ── 4.5 Documentation ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 4.5  Technical Project Documentation")

with st.expander("System Architecture Overview"):
    st.markdown("""
    ```
    ┌──────────────────────────────────────────────────────────────┐
    │          CLIENT APPLICATION  (Streamlit Web / PWA)           │
    │   Location Consent  |  Health Profile  |  Route Advisory UI  │
    └───────────────────────────┬──────────────────────────────────┘
                                │  HTTPS / WebSocket
    ┌───────────────────────────▼──────────────────────────────────┐
    │           FASTAPI ENVIRONMENTAL GATEWAY SERVER               │
    │  ┌───────────────────────┐   ┌────────────────────────────┐  │
    │  │  Data Ingestion        │   │  Spatial Kriging Service   │  │
    │  └──────────┬────────────┘   └──────────┬─────────────────┘  │
    │  ┌──────────▼────────────┐   ┌──────────▼─────────────────┐  │
    │  │  OpenAQ / CPCB Feed   │   │  PyTorch LSTM / GRU Engine  │  │
    │  └───────────────────────┘   └────────────────────────────┘  │
    └───────────────────────────┬──────────────────────────────────┘
                                │
    ┌───────────────────────────▼──────────────────────────────────┐
    │              STORAGE AND MESSAGING LAYER                     │
    │   InfluxDB (Time-series)  |  Redis (Cache)  |  Firebase FCM  │
    └──────────────────────────────────────────────────────────────┘
    ```
    """)

with st.expander("End-to-End Data Flow Pipeline"):
    st.markdown("""
    1. **Client Geo-Capture:** Browser GPS permission or manual coordinate entry.
    2. **Telemetry Ingestion:** Nearest stations from OpenAQ/WAQI via spatial lookup.
    3. **Meteorological Fusion:** Boundary layer height, temperature, humidity, wind from OpenWeatherMap.
    4. **Sequential Tensor Formation:** 24-hour lagged feature matrix for PyTorch LSTM.
    5. **Multi-Horizon Inference:** AQI forecasts for t+1h to t+24h with 95% CI.
    6. **Route Spatial Sampling:** Google Directions waypoints intersected against pollution grid.
    7. **Health Risk Optimization:** Clean air corridor recommendation via exposure scoring.
    8. **Push Dispatch:** Firebase Cloud Messaging notifies registered devices on threshold breach.
    """)

with st.expander("API Endpoint Documentation"):
    st.markdown("""
    | Method | Endpoint | Description |
    |---|---|---|
    | `GET`  | `/api/v1/aqi/realtime?lat={lat}&lon={lon}` | Nearest station readings and sub-index values |
    | `POST` | `/api/v1/forecast/predict`                 | LSTM prediction for a given feature tensor |
    | `POST` | `/api/v1/routes/analyze`                   | Comparative exposure analysis for Route A vs B |
    | `POST` | `/api/v1/notifications/subscribe`          | Register device FCM token for threshold alerts |
    """)

with st.expander("Model Evaluation and Benchmarking Methodology"):
    st.markdown("""
    **Evaluation Metrics:** RMSE, MAE, SMAPE, and Pearson R2.

    **Baselines:** ARIMA, Random Forest Regressor, Facebook Prophet.

    **Validation Protocol:** Temporal train / val / test split (80% / 10% / 10%)
    preserving chronological order to prevent lookahead data leakage.
    """)

with st.expander("Deployment and Containerization Guide"):
    st.markdown("""
    **Run Locally:**
    ```bash
    pip install -r requirements.txt
    streamlit run app.py
    ```

    **Docker:** Multi-stage Dockerfile targeting Python 3.11 slim.
    Streamlit frontend on port 8501, FastAPI backend on port 8000.

    **Environment Variables (Production):**
    `OPENAQ_API_KEY`, `OWM_API_KEY`, `GOOGLE_MAPS_API_KEY`, `FIREBASE_CREDENTIALS_JSON`, `INFLUX_TOKEN`
    """)

with st.expander("Known Limitations and Assumptions"):
    st.markdown("""
    - **Sensor Sparsity:** Monitoring stations concentrated in metro cores. Rural areas require satellite AOD corrections.
    - **Microclimate Inversions:** Extreme Delhi winter inversions require frequent model recalibration.
    - **Demo Stage:** Current UI runs on simulated datasets. All production APIs integrated across project milestones.
    """)
