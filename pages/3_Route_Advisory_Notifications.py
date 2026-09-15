"""
Module 3 — Route Advisory, Dashboard and Push Notifications — Dark Theme
"""

import streamlit as st
from datetime import datetime, date
from data.custom_dataset import load_pune_data
from data.demo_data import get_demo_notifications, HEALTH_PROFILES
from ml.route_exposure import RoutePollutionEstimator
from components.metrics import render_demo_banner
from components.maps import render_route_map
from components.alerts import render_travel_advisory_card, render_notification_center
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Module 3 — Route Advisory and Push Notifications | EcoAir Intelligence",
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
.stButton > button { background: #FFFFFF !important; border: 1px solid #334155 !important; color: #334155 !important; border-radius: 5px; font-weight: 600; }
.stButton > button[kind="primary"] { background: #1D4ED8 !important; border-color: #2563EB !important; color: white !important; }
[data-baseweb="select"] > div { background: #FFFFFF !important; border-color: #334155 !important; color: #0F172A !important; }
[data-baseweb="input"] > div { background: #FFFFFF !important; border-color: #334155 !important; color: #0F172A !important; }
[data-testid="stExpander"] { background: #FFFFFF !important; border: 1px solid #334155 !important; border-radius: 6px; }
details summary { color: #334155 !important; font-weight: 600; font-size: 0.88rem; }
[data-testid="stToggle"] > label { color: #334155 !important; }
[data-testid="stSlider"] > div > div > div { background: #3B82F6 !important; }
hr { border-color: #334155 !important; }
h1, h2, h3, h4 { color: #0F172A !important; }
[data-testid="stCaptionContainer"] { color: #64748B !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #F8FAFC; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

if "health_profile" not in st.session_state:  st.session_state.health_profile  = "General User"
if "enable_push"    not in st.session_state:  st.session_state.enable_push     = True
if "push_threshold" not in st.session_state:  st.session_state.push_threshold  = 100

# ── Page Header ────────────────────────────────────────────────────
render_sidebar()
st.markdown("## Module 3 — Route Advisory, Dashboard and Push Notifications")
st.caption(
    "Pollution-aware smart mobility: minimizing cumulative particulate exposure "
    "through route optimization and proactive health alerts."
)
render_demo_banner("Module 3 — Routing and Advisory Prototype")
st.markdown("---")

# ── 3.1 Travel Plan ────────────────────────────────────────────────
st.markdown("### 3.1  Travel Journey Configuration")

pune_stations = list(load_pune_data().keys())
dropdown_options = pune_stations + ["Type Custom Landmark / Address..."]

m3_c1, m3_c2 = st.columns(2)
with m3_c1:
    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#0F172A; margin-bottom:4px;'>Origin Landmark / Station</div>", unsafe_allow_html=True)
    orig_pick = st.selectbox(
        "Origin Landmark / Station",
        options=dropdown_options,
        index=dropdown_options.index("Hadapsar_Gadital_01") if "Hadapsar_Gadital_01" in dropdown_options else 0,
        key="m3_orig_select",
        label_visibility="collapsed"
    )
    if orig_pick == "Type Custom Landmark / Address...":
        source_loc = st.text_input("Type Origin Landmark", value="Shivajinagar, Pune", key="m3_custom_origin")
    else:
        source_loc = orig_pick

with m3_c2:
    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#0F172A; margin-bottom:4px;'>Destination Landmark / Station</div>", unsafe_allow_html=True)
    dest_pick = st.selectbox(
        "Destination Landmark / Station",
        options=dropdown_options,
        index=dropdown_options.index("BopadiSquare_65") if "BopadiSquare_65" in dropdown_options else 1,
        key="m3_dest_select",
        label_visibility="collapsed"
    )
    if dest_pick == "Type Custom Landmark / Address...":
        dest_loc = st.text_input("Type Destination Landmark", value="Viman Nagar, Pune", key="m3_custom_dest")
    else:
        dest_loc = dest_pick

m3_c3, m3_c4, m3_c5 = st.columns([1.0, 1.0, 1.3])
with m3_c3: travel_date = st.date_input("Travel Date", value=date.today())
with m3_c4: travel_time = st.time_input("Departure Time", value=datetime.now().time())
with m3_c5:
    transport_mode = st.selectbox(
        "Transport Mode", ["Car", "Public Transport", "Motorcycle", "Cycling", "Walking"]
    )

st.button("Analyze Route and Compute Exposure", type="primary", use_container_width=True)

_estimator = RoutePollutionEstimator()
route_data = _estimator.estimate_exposure(
    origin=source_loc, destination=dest_loc,
    transport_mode=transport_mode, health_profile=st.session_state.health_profile
)

render_travel_advisory_card(
    advisory_text=route_data["advisory"],
    risk_level=route_data["route_a"]["risk_level"],
    risk_color=route_data["route_a"]["risk_color"],
    reduction_pct=route_data["reduction_pct"]
)

# ── 3.2 Route Comparison ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 3.2  Route Exposure Analysis and Comparison")
ra = route_data["route_a"]
rb = route_data["route_b"]
card_a, card_b = st.columns(2)

with card_a:
    st.markdown(
        f"""<div style="background:#FFFFFF; border:1px solid #7F1D1D; border-top:3px solid #EF4444;
                        border-radius:10px; padding:18px 20px; min-height:230px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <b style="font-size:0.98rem; color:#0F172A;">{ra['name']}</b>
                <span style="background:rgba(239,68,68,0.15); border:1px solid #7F1D1D; color:#F87171;
                      font-size:0.70rem; font-weight:700; padding:3px 10px; border-radius:3px;">
                    {ra['risk_level']}
                </span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
                <div style="background:#F1F5F9; padding:9px; border-radius:5px; border:1px solid #334155;">
                    <div style="font-size:0.70rem; color:#64748B;">Distance</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">{ra['distance_km']} km</div>
                </div>
                <div style="background:#F1F5F9; padding:9px; border-radius:5px; border:1px solid #334155;">
                    <div style="font-size:0.70rem; color:#64748B;">Est. Travel Time</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">{ra['duration_mins']} min</div>
                </div>
                <div style="background:#1A0808; padding:9px; border-radius:5px; border:1px solid #7F1D1D;">
                    <div style="font-size:0.70rem; color:#B91C1C;">Average AQI</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#F87171;">{ra['avg_aqi']}</div>
                </div>
                <div style="background:#1A0808; padding:9px; border-radius:5px; border:1px solid #7F1D1D;">
                    <div style="font-size:0.70rem; color:#B91C1C;">Exposure Score</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#F87171;">{ra['exposure_score']} / 100</div>
                </div>
            </div>
            <div style="font-size:0.78rem; color:#64748B;">
                Passes through 2 severe congestion zones. Peak AQI: <b style="color:#F87171;">{ra.get('max_aqi', ra.get('avg_aqi', 'N/A'))}</b>.
            </div>
        </div>""",
        unsafe_allow_html=True
    )

with card_b:
    st.markdown(
        f"""<div style="background:#0A1A0A; border:1px solid #14532D; border-top:3px solid #22C55E;
                        border-radius:10px; padding:18px 20px; min-height:230px;
                        box-shadow:0 2px 16px rgba(34,197,94,0.10);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <b style="font-size:0.98rem; color:#16A34A;">{rb['name']}</b>
                <span style="background:rgba(34,197,94,0.15); border:1px solid #14532D; color:#16A34A;
                      font-size:0.70rem; font-weight:700; padding:3px 10px; border-radius:3px;">
                    RECOMMENDED
                </span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px;">
                <div style="background:#0A140A; padding:9px; border-radius:5px; border:1px solid #1A2E1A;">
                    <div style="font-size:0.70rem; color:#64748B;">Distance</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">{rb['distance_km']} km</div>
                </div>
                <div style="background:#0A140A; padding:9px; border-radius:5px; border:1px solid #1A2E1A;">
                    <div style="font-size:0.70rem; color:#64748B;">Est. Travel Time</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#0F172A;">{rb['duration_mins']} min</div>
                </div>
                <div style="background:#0A1A0A; padding:9px; border-radius:5px; border:1px solid #14532D;">
                    <div style="font-size:0.70rem; color:#166534;">Average AQI</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#16A34A;">{rb['avg_aqi']}</div>
                </div>
                <div style="background:#0A1A0A; padding:9px; border-radius:5px; border:1px solid #14532D;">
                    <div style="font-size:0.70rem; color:#166534;">Exposure Score</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#16A34A;">{rb['exposure_score']} / 100</div>
                </div>
            </div>
            <div style="font-size:0.78rem; color:#166534;">
                <b style="color:#16A34A;">{route_data['reduction_pct']}% lower PM2.5 inhalation</b> vs Route A.
            </div>
        </div>""",
        unsafe_allow_html=True
    )

# ── 3.3 Route Map ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 3.3  Geospatial Route and Pollution Hotspot Map")
st.caption("Displaying the optimized Best Route (solid green): lowest cumulative particulate exposure corridor. Red circles: localized high-pollution hotspots avoided.")
render_route_map(route_data)

# ── 3.4 Notifications ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 3.4  Push Notification Engine and Alert Preferences")

pref_col, feed_col = st.columns([1.2, 1.8])

with pref_col:
    st.subheader("Alert Preferences")
    push_enabled = st.toggle("Enable Real-Time Push Notifications", value=st.session_state.enable_push)
    st.session_state.enable_push = push_enabled

    alert_th = st.slider(
        "AQI Breach Alert Threshold", min_value=50, max_value=300,
        value=st.session_state.push_threshold, step=10
    )
    st.session_state.push_threshold = alert_th

    st.checkbox("Enable Proactive Travel Advisory Alerts", value=True)
    st.checkbox("Auto-suggest Clean Route when 25% lower exposure", value=True)

    if st.button("Save Notification Preferences", use_container_width=True):
        st.toast("Notification preferences saved.")

with feed_col:
    render_notification_center(get_demo_notifications())

with st.expander("Future Backend Integration — Module 3 Roadmap (Weeks 5–6)"):
    st.markdown("""
    - **Routing Engine:** Google Directions API with polyline waypoint decoding.
    - **Exposure Engine:** Numerical integration of predicted spatial AQI along route waypoints.
    - **Push Notifications:** Firebase Cloud Messaging (FCM) topic-based subscriptions.
    - **Progressive Web App:** Service worker registration for offline and background alerts.
    """)
