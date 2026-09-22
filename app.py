"""
AI-Powered Environmental Intelligence System
for Air Quality Prediction and Smart Mobility Recommendations

Landing Home Page — Light Theme
"""

import base64
import streamlit as st
from datetime import datetime
from pathlib import Path
from data.custom_dataset import (
    load_pune_data,
    LOCATIONS_DATA,
    HEALTH_PROFILES,
    get_aqi_category_info,
    get_system_services_status
)
from components.metrics import render_hero_aqi_card
from components.sidebar import render_sidebar

# ── Application Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="EcoAir Intelligence — Environmental AI Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Hero image encode ──────────────────────────────────────────────────────
def _img_b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()

hero_b64 = _img_b64("assets/hero_bg.jpg")

# ── Global Dark Stylesheet ─────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }}

    /* ── Global page background ── */
    .stApp {{
        background-color: #F8FAFC !important;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0;
    }}
    section[data-testid="stSidebar"] * {{
        color: #0F172A !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label {{
        color: #334155 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #334155 !important;
        text-align: left;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: #EFF6FF !important;
        border-color: #3B82F6 !important;
        color: #1D4ED8 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover p {{
        color: #1D4ED8 !important;
    }}

    /* ── Main container ── */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem;
        max-width: 1380px;
    }}

    /* ── Streamlit native widgets ── */
    [data-testid="stMetric"] {{
        background: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
        padding: 12px 14px;
    }}
    [data-testid="stMetricLabel"] {{ color: #0F172A !important; }}
    [data-testid="stMetricValue"] {{ color: #0F172A !important; }}

    .stButton > button {{
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.86rem;
        background: #FFFFFF !important;
        border: 1px solid #334155 !important;
        color: #334155 !important;
        transition: all 0.18s ease;
    }}
    .stButton > button:hover {{
        background: #F8FAFC !important;
        border-color: #3B82F6 !important;
        color: #1D4ED8 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(59,130,246,0.2);
    }}
    .stButton > button[kind="primary"] {{
        background: #1D4ED8 !important;
        border-color: #2563EB !important;
        color: white !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: #2563EB !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.35);
    }}

    /* Selectbox / Inputs */
    [data-baseweb="select"] > div {{
        background: #FFFFFF !important;
        border-color: #334155 !important;
        color: #0F172A !important;
    }}
    [data-baseweb="input"] > div {{
        background: #FFFFFF !important;
        border-color: #334155 !important;
        color: #0F172A !important;
    }}

    /* Expander */
    [data-testid="stExpander"] {{
        background: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 6px;
    }}
    details summary {{
        font-weight: 600;
        font-size: 0.88rem;
        color: #334155 !important;
    }}

    /* Info / Warning boxes */
    [data-testid="stAlert"] {{
        background: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        color: #1D4ED8 !important;
    }}

    /* Tables */
    [data-testid="stTable"] table {{
        background: #FFFFFF;
        color: #334155;
    }}
    [data-testid="stTable"] th {{
        background: #1E3A8A !important;
        color: #FFFFFF !important;
    }}
    [data-testid="stTable"] td {{
        border-color: #334155 !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: #FFFFFF;
        border-bottom: 1px solid #334155;
        gap: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: #0F172A;
        font-weight: 600;
        font-size: 0.84rem;
    }}
    .stTabs [aria-selected="true"] {{
        color: #60A5FA !important;
        border-bottom: 2px solid #3B82F6;
    }}

    /* Slider */
    [data-testid="stSlider"] > div > div > div {{
        background: #3B82F6 !important;
    }}

    /* Toggle */
    [data-testid="stToggle"] > label {{
        color: #334155 !important;
    }}

    /* Progress bar */
    [data-testid="stProgress"] > div {{
        background: #334155;
    }}
    [data-testid="stProgress"] > div > div {{
        background: linear-gradient(90deg, #2563EB, #7C3AED) !important;
    }}

    /* Spinner */
    [data-testid="stSpinner"] {{ color: #60A5FA !important; }}

    /* hr */
    hr {{ border-color: #334155 !important; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #F8FAFC; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #2D2D4A; }}

    /* Caption text */
    [data-testid="stCaptionContainer"] {{
        color: #0F172A !important;
    }}

    /* Markdown headings */
    h1, h2, h3, h4 {{ color: #0F172A !important; }}
    p {{ color: #0F172A; }}

    /* Subheader */
    [data-testid="stHeading"] {{ color: #0F172A !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ── Session State ──────────────────────────────────────────────────────────
if "selected_city"   not in st.session_state:
    st.session_state.selected_city   = list(LOCATIONS_DATA.keys())[0]
if "health_profile"  not in st.session_state:
    st.session_state.health_profile  = "General User"
if "alert_threshold" not in st.session_state:
    st.session_state.alert_threshold = 100

# ── Sidebar ────────────────────────────────────────────────────────────────
render_sidebar()

# ══════════════════════════════════════════════════════════════════════════
# HERO SECTION — fully inline, no CSS classes, no position:absolute
# Background image + dark gradient combined in one background property
# ══════════════════════════════════════════════════════════════════════════
hero_html = (
    f"<div style='"
    f"background: linear-gradient(110deg, rgba(5,5,15,0.50) 0%, rgba(7,10,30,0.50) 55%, rgba(5,10,20,0.50) 100%),"
    f" url(data:image/jpeg;base64,{hero_b64});"
    f"background-size: cover, cover;"
    f"background-position: center center, center 40%;"
    f"background-repeat: no-repeat, no-repeat;"
    f"padding: 56px 60px;"
    f"margin: -1rem -1rem 0 -1rem;"
    f"border-radius: 0;"
    f"min-height: 500px;"
    f"display: flex;"
    f"align-items: center;"
    f"'>"

    # inner content wrapper — no position needed
    f"<div style='max-width:820px;'>"

    # badge
    f"<div style='display:inline-block; background:rgba(37,99,235,0.22);"
    f"border:1px solid rgba(96,165,250,0.45); color:#60A5FA;"
    f"padding:4px 14px; border-radius:3px; font-size:0.72rem;"
    f"font-weight:700; letter-spacing:1.2px; margin-bottom:18px;'>"
    f"INFOSYS SPRINGBOARD INTERNSHIP PROJECT &nbsp;&mdash;&nbsp; ENVIRONMENTAL INTELLIGENCE"
    f"</div>"

    # h1
    f"<div style='font-size:2.55rem; font-weight:800; color:#FFFFFF;"
    f"line-height:1.22; margin:0 0 14px 0; letter-spacing:-0.5px; text-shadow: 0px 2px 6px rgba(0,0,0,0.8);'>"
    f"AI-Powered Environmental<br>Intelligence System"
    f"</div>"

    # subtitle
    f"<div style='font-size:1.05rem; color:#93C5FD; font-weight:600; margin:0 0 8px 0; text-shadow: 0px 1px 4px rgba(0,0,0,0.6);'>"
    f"Air Quality Prediction and Smart Mobility Recommendations"
    f"</div>"

    # description
    f"<div style='font-size:0.90rem; color:#F1F5F9; line-height:1.70;"
    f"margin:0 0 28px 0; max-width:680px; text-shadow: 0px 1px 3px rgba(0,0,0,0.5); font-weight:400;'>"
    f"Urban air pollution is one of the leading environmental health crises of the 21st century. "
    f"This system integrates real-time ambient sensor telemetry, deep recurrent neural network "
    f"forecasting, and route-level pollution exposure modelling to empower citizens and planners "
    f"with actionable, data-driven environmental intelligence."
    f"</div>"

    f"</div>"     # end content wrapper
    f"</div>"     # end hero div
)
st.markdown(hero_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# BODY CONTENT
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="body-section">', unsafe_allow_html=True)

st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)

# ── Problem Statement ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Problem Statement and Research Context")

ps_col1, ps_col2 = st.columns([1.55, 1.0])

with ps_col1:
    st.markdown(
        """
        <div style="font-size:0.90rem; color:#0F172A; line-height:1.80;">
            <p>
                India is home to <b style="color:#0F172A;">39 of the world's 50 most polluted cities</b>
                (IQ Air World Air Quality Report, 2023). Particulate matter (PM2.5) concentrations
                in cities such as Delhi NCR routinely exceed WHO safe limits by
                <b style="color:#F87171;">10 to 20 times</b>, contributing to over
                <b style="color:#F87171;">1.6 million premature deaths</b> annually.
            </p>
            <p>
                Existing air quality monitoring systems provide only
                <b style="color:#334155;">static historical snapshots</b> — they cannot predict
                near-future pollution spikes or guide citizens toward less-polluted travel routes.
                Vulnerable populations (asthmatics, the elderly, children) lack
                <b style="color:#334155;">personalized, proactive</b> environmental health guidance.
            </p>
            <p style="color:#0F172A; margin-bottom:6px;">
                This project addresses the gap by building an integrated AI system that:
            </p>
            <ul style="color:#0F172A;">
                <li>Ingests live multi-pollutant telemetry from OpenAQ, WAQI, and CPCB sensor networks.</li>
                <li>Forecasts future AQI 1–24 hours ahead using deep recurrent neural architectures (LSTM / GRU).</li>
                <li>Computes route-level cumulative pollution exposure and recommends clean-air corridors.</li>
                <li>Delivers proactive push notifications to citizens when AQI thresholds are breached.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

with ps_col2:
    stats = [
        ("39 / 50",  "#F87171", "World's Most Polluted Cities in India (IQ Air 2023)"),
        ("1.6 M",    "#F87171", "Premature Deaths Annually from Outdoor Air Pollution"),
        ("10–20x",   "#FBBF24", "Delhi PM2.5 Exceeds WHO Annual Guideline"),
        ("PM2.5",    "#60A5FA", "Primary Driver of Urban Health Impact"),
        ("5 ug/m3",  "#16A34A", "WHO Safe Annual PM2.5 Guideline"),
    ]
    for val, color, label in stats:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:14px; background:#FFFFFF;
                        border:1px solid #334155; border-left:4px solid {color};
                        border-radius:6px; padding:10px 14px; margin-bottom:8px;">
                <div style="font-size:1.20rem; font-weight:800; color:{color}; min-width:65px;">
                    {val}
                </div>
                <div style="font-size:0.78rem; color:#0F172A; line-height:1.4;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ── Live AQI Snapshot ──────────────────────────────────────────────────────
st.markdown("---")
city_data = LOCATIONS_DATA[st.session_state.selected_city]
now_str   = datetime.now().strftime("%d %b %Y, %H:%M IST")

st.markdown(f"## Live AQI Snapshot — {st.session_state.selected_city}")
render_hero_aqi_card(
    aqi_val=city_data["aqi"],
    dominant_pollutant=city_data["dominant_pollutant"],
    last_updated=now_str,
    data_source="Pune Smart City Sensor Network (Preprocessed Dataset)"
)

# ── Module Summary Cards ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Project Modules — Architecture and Scope")
st.markdown(
    "<p style='color:#0F172A; font-size:0.88rem; margin-top:-8px; margin-bottom:20px;'>"
    "Four sequential development modules, each corresponding to a distinct research and "
    "engineering milestone over an eight-week delivery timeline."
    "</p>",
    unsafe_allow_html=True
)

MODULE_DEFS = [
    {
        "number": "01", "weeks": "Weeks 1–2", "color": "#3B82F6",
        "title": "Location and AQI Real-Time Data Integration",
        "summary": (
            "Establishes the foundational data acquisition layer. Captures device geolocation "
            "via browser GPS or manual city selection, then ingests continuous multi-pollutant "
            "sensor telemetry from OpenAQ, WAQI, and CPCB monitoring networks."
        ),
        "deliverables": [
            "Real-time PM2.5, PM10, NO2, O3, CO, SO2 with CPCB sub-index calculations",
            "Interactive neighbourhood pollution map with station markers",
            "Meteorological fusion: temperature, humidity, wind, boundary layer height",
            "Health sensitivity profiles with configurable alert thresholds",
        ],
        "tech":      ["OpenAQ API", "WAQI API", "Folium Maps", "CPCB Standards"],
        "page":      "pages/1_Location_AQI_RealTime.py",
        "btn_key":   "nav_m1",
    },
    {
        "number": "02", "weeks": "Weeks 3–4", "color": "#8B5CF6",
        "title": "Predictive AQI Forecasting Model",
        "summary": (
            "Deploys a deep recurrent neural network model (GRU) for multi-step AQI "
            "forecasting with spatial Ordinary Kriging geostatistics between monitoring stations."
        ),
        "deliverables": [
            "GRU recurrent neural model trained on Pune dataset (103k+ records across 10 stations)",
            "Configurable prediction horizons: 1, 3, 6, 12, and 24 hours ahead",
            "95% Confidence Interval uncertainty quantification ribbon",
            "Spatial Ordinary Kriging interpolation with Gaussian semivariogram modeling",
        ],
        "tech":      ["PyTorch GRU", "Ordinary Kriging", "FastAPI", "Google Directions", "MLflow"],
        "page":      "pages/2_Predictive_AQI_Forecasting.py",
        "btn_key":   "nav_m2",
    },
    {
        "number": "03", "weeks": "Weeks 5–6", "color": "#22C55E",
        "title": "Route Advisory, Dashboard and Push Notifications",
        "summary": (
            "Integrates route-level pollution exposure modeling to recommend the clean-air "
            "corridor for a given journey. Dispatches proactive Firebase push notifications."
        ),
        "deliverables": [
            "Cumulative PM2.5 exposure scoring across waypoints for 5 transport modes",
            "Route A vs Route B comparison with exposure reduction percentages",
            "Firebase Cloud Messaging push notification dispatch engine",
            "Dynamic travel advisory generation based on AQI and health profile",
        ],
        "tech":      ["Google Directions API", "Firebase FCM", "Folium Routes", "Kriging"],
        "page":      "pages/3_Route_Advisory_Notifications.py",
        "btn_key":   "nav_m3",
    },
]


def _build_module_card(mod: dict) -> str:
    color = mod["color"]
    tag_pills = " ".join(
        "<span style='background:#E2E8F0; color:#0F172A; font-size:0.68rem; "
        "font-weight:600; padding:3px 9px; border-radius:3px; border:1px solid #334155;'>"
        + t + "</span>"
        for t in mod["tech"]
    )
    bullet_rows = "".join(
        "<div style='font-size:0.78rem; color:#0F172A; padding:5px 8px; "
        "background:#F1F5F9; border-radius:4px; border:1px solid #E2E8F0; line-height:1.4;'>"
        "<span style='color:" + color + "; font-weight:700; margin-right:6px;'>-</span>"
        + d + "</div>"
        for d in mod["deliverables"]
    )
    return (
        f"<div style='background:#FFFFFF; border:1px solid #334155; "
        f"border-left:4px solid {color}; border-radius:8px; "
        f"padding:22px 26px; margin-bottom:14px; "
        f"box-shadow:0 2px 12px rgba(0,0,0,0.35);'>"
        f"<div style='display:flex; justify-content:space-between; align-items:flex-start; "
        f"flex-wrap:wrap; gap:10px; margin-bottom:12px;'>"
        f"<div style='display:flex; align-items:center; gap:14px;'>"
        f"<div style='background:{color}18; border:1px solid {color}55; color:{color}; "
        f"font-size:0.72rem; font-weight:800; width:36px; height:36px; border-radius:6px; "
        f"display:flex; align-items:center; justify-content:center; flex-shrink:0;'>{mod['number']}</div>"
        f"<div>"
        f"<div style='font-size:0.70rem; font-weight:700; color:{color}; "
        f"text-transform:uppercase; letter-spacing:1px; margin-bottom:2px;'>"
        f"Module {mod['number']} &nbsp;&middot;&nbsp; {mod['weeks']}</div>"
        f"<div style='font-size:1.05rem; font-weight:700; color:#0F172A;'>{mod['title']}</div>"
        f"</div></div>"
        f"<div style='display:flex; gap:6px; flex-wrap:wrap;'>{tag_pills}</div>"
        f"</div>"
        f"<p style='font-size:0.86rem; color:#0F172A; line-height:1.60; margin:0 0 12px 0;'>"
        f"{mod['summary']}</p>"
        f"<div style='display:grid; grid-template-columns:1fr 1fr; gap:5px;'>{bullet_rows}</div>"
        f"</div>"
    )


for mod in MODULE_DEFS:
    st.markdown(_build_module_card(mod), unsafe_allow_html=True)
    if st.button(f"Open Module {mod['number']} — {mod['title']}", key=mod["btn_key"]):
        st.switch_page(mod["page"])

# ── System Architecture ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## System Architecture at a Glance")

arch_col1, arch_col2 = st.columns([1.4, 1.0])

with arch_col1:
    pipeline_steps = [
        ("01", "User Location Capture",      "Browser GPS + Reverse Geocoding",             "#3B82F6"),
        ("02", "AQI Data Ingestion",          "OpenAQ / WAQI / CPCB Real-Time Feeds",        "#0EA5E9"),
        ("03", "Meteorological Fusion",       "OpenWeatherMap — Wind, Humidity, PBLH",        "#06B6D4"),
        ("04", "Deep Learning Inference",     "PyTorch LSTM / GRU — 1 to 24h Forecast",       "#8B5CF6"),
        ("05", "Route Exposure Modeling",     "Waypoint Kriging Interpolation",               "#A855F7"),
        ("06", "Smart Travel Advisory",       "Health Profile-Aware Risk Classification",     "#EC4899"),
        ("07", "Push Notification Dispatch",  "Firebase Cloud Messaging (FCM)",               "#F97316"),
        ("08", "Citizen Dashboard",           "Streamlit Progressive Web App",                "#22C55E"),
    ]
    for num, title, detail, color in pipeline_steps:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:7px;">
                <div style="width:28px; height:28px; background:{color}22; border:1px solid {color}66;
                            color:{color}; border-radius:50%; font-size:0.66rem; font-weight:800;
                            display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                    {num}
                </div>
                <div style="flex:1; background:#FFFFFF; border:1px solid #334155; border-radius:6px;
                            padding:8px 14px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.83rem; font-weight:700; color:#334155;">{title}</span>
                    <span style="font-size:0.73rem; color:#0F172A;">{detail}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with arch_col2:
    st.markdown(
        "<div style='font-size:0.78rem; font-weight:700; color:#0F172A; "
        "text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;'>Technology Stack</div>",
        unsafe_allow_html=True
    )
    tech_stack = [
        ("Frontend",         "Python 3.13 + Streamlit 1.51",        "#3B82F6"),
        ("ML / Inference",   "PyTorch — LSTM / GRU Architectures",   "#8B5CF6"),
        ("Backend API",      "FastAPI (REST + WebSocket)",            "#0EA5E9"),
        ("Spatial Analysis", "Universal Kriging + IDW",               "#22C55E"),
        ("Data Sources",     "OpenAQ, WAQI, CPCB, OpenWeatherMap",   "#FBBF24"),
        ("Maps",             "Folium + Leaflet.js",                   "#16A34A"),
        ("Notifications",    "Firebase Cloud Messaging (FCM)",        "#F97316"),
        ("Time-Series DB",   "InfluxDB + PostgreSQL TimescaleDB",     "#0F172A"),
        ("Containers",       "Docker + Docker Compose",               "#0F172A"),
    ]
    for label, desc, color in tech_stack:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:10px; background:#FFFFFF;
                        border:1px solid #334155; border-radius:5px; padding:7px 12px;
                        margin-bottom:5px;">
                <div style="width:7px; height:7px; border-radius:50%;
                            background:{color}; flex-shrink:0;"></div>
                <span style="font-size:0.78rem; font-weight:700; color:#334155; min-width:115px;">
                    {label}
                </span>
                <span style="font-size:0.75rem; color:#0F172A;">{desc}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# ── Integration Status ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## Integration Status Summary")

services = get_system_services_status()
status_color_map = {
    "Active":           "#16A34A",
    "Operational":      "#60A5FA",
    "Pending Training": "#FBBF24",
    "Not Connected":    "#0F172A",
}

for s in services:
    color = status_color_map.get(s["status"], "#0F172A")
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:space-between; background:#FFFFFF;
                    border:1px solid #334155; border-radius:6px; padding:9px 16px;
                    margin-bottom:6px; flex-wrap:wrap; gap:8px;">
            <div style="display:flex; align-items:center; gap:10px; min-width:260px;">
                <div style="width:7px; height:7px; background:{color}; border-radius:50%; flex-shrink:0;"></div>
                <span style="font-size:0.84rem; font-weight:600; color:#334155;">{s['service']}</span>
                <span style="font-size:0.72rem; color:#334155;">{s['module']}</span>
            </div>
            <div style="flex:1; font-size:0.77rem; color:#334155; padding:0 10px; min-width:180px;">
                {s['endpoint']}
            </div>
            <span style="background:{color}18; border:1px solid {color}44; color:{color};
                  font-size:0.68rem; font-weight:700; padding:3px 10px; border-radius:3px;
                  white-space:nowrap;">{s['status']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; padding:12px 0; font-size:0.78rem; color:#334155; line-height:1.9;">
        <b style="color:#0F172A;">AI-Powered Environmental Intelligence System</b><br>
        Air Quality Prediction and Smart Mobility Recommendations<br>
        Infosys Springboard Internship Project &nbsp;|&nbsp; Built with Python and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
