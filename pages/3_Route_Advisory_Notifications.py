"""
Module 3 — Route Advisory, Dashboard and Push Notifications — Dark Theme
"""

import streamlit as st
from datetime import datetime, date
from data.custom_dataset import load_pune_data, get_pune_notifications
from ml.route_exposure import RoutePollutionEstimator
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
section[data-testid="stSidebar"] * { color: #0F172A !important; }
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
[data-testid="stCaptionContainer"] { color: #0F172A !important; }
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
st.markdown("---")

# ── 3.1 Travel Plan ────────────────────────────────────────────────
st.markdown("### 3.1  Travel Journey Configuration")

pune_data_map = load_pune_data()
pune_stations = list(pune_data_map.keys())
clean_names = {k: k.replace("_", " ") for k in pune_stations}
dropdown_options = [f"{clean_names[k]} [{k}]" for k in pune_stations]
stn_lookup = {f"{clean_names[k]} [{k}]": k for k in pune_stations}

m3_c1, m3_c2 = st.columns(2)
with m3_c1:
    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#0F172A; margin-bottom:4px;'>Origin Station (10 Pune Regions)</div>", unsafe_allow_html=True)
    orig_idx = 3 if len(dropdown_options) > 3 else 0  # Hadapsar
    orig_pick = st.selectbox(
        "Origin Station",
        options=dropdown_options,
        index=orig_idx,
        key="m3_orig_select",
        label_visibility="collapsed"
    )
    source_loc = stn_lookup[orig_pick]

with m3_c2:
    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#0F172A; margin-bottom:4px;'>Destination Station (10 Pune Regions)</div>", unsafe_allow_html=True)
    dest_idx = 0  # Bopodi
    dest_pick = st.selectbox(
        "Destination Station",
        options=dropdown_options,
        index=dest_idx,
        key="m3_dest_select",
        label_visibility="collapsed"
    )
    dest_loc = stn_lookup[dest_pick]

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
rc = route_data.get("route_c", route_data.get("recommended_route", rb))
card_a, card_b, card_c = st.columns(3)

with card_a:
    st.markdown(
        f"""<div style="background:#FFFFFF; border:1px solid #7F1D1D; border-top:3px solid #EF4444;
                        border-radius:10px; padding:16px 18px; min-height:250px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <b style="font-size:0.92rem; color:#0F172A;">{ra['name']}</b>
                <span style="background:rgba(239,68,68,0.15); border:1px solid #7F1D1D; color:#DC2626;
                      font-size:0.68rem; font-weight:700; padding:2px 8px; border-radius:3px;">
                    🔴 {ra.get('tag', 'HIGH EXPOSURE')}
                </span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:8px;">
                <div style="background:#F1F5F9; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                    <div style="font-size:0.68rem; color:#0F172A;">Distance</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{ra['distance_km']} km</div>
                </div>
                <div style="background:#F1F5F9; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                    <div style="font-size:0.68rem; color:#0F172A;">Est. Travel Time</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{ra['duration_mins']} min</div>
                </div>
                <div style="background:#FEF2F2; padding:8px; border-radius:5px; border:1px solid #FECACA;">
                    <div style="font-size:0.68rem; color:#991B1B;">Average AQI</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#DC2626;">{ra['avg_aqi']}</div>
                </div>
                <div style="background:#FEF2F2; padding:8px; border-radius:5px; border:1px solid #FECACA;">
                    <div style="font-size:0.68rem; color:#991B1B;">Exposure Score</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#DC2626;">{ra['exposure_score']} / 100</div>
                </div>
            </div>
            <div style="font-size:0.75rem; color:#0F172A;">
                Passes through congested urban arteries. Peak AQI: <b style="color:#DC2626;">{ra.get('max_aqi', ra.get('avg_aqi', 'N/A'))}</b>.
            </div>
        </div>""",
        unsafe_allow_html=True
    )

with card_b:
    st.markdown(
        f"""<div style="background:#FFFFFF; border:1px solid #1E3A8A; border-top:3px solid #2563EB;
                        border-radius:10px; padding:16px 18px; min-height:250px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <b style="font-size:0.92rem; color:#0F172A;">{rb['name']}</b>
                <span style="background:rgba(37,99,235,0.15); border:1px solid #1E3A8A; color:#2563EB;
                      font-size:0.68rem; font-weight:700; padding:2px 8px; border-radius:3px;">
                    🔵 {rb.get('tag', 'ALTERNATIVE')}
                </span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:8px;">
                <div style="background:#F1F5F9; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                    <div style="font-size:0.68rem; color:#0F172A;">Distance</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{rb['distance_km']} km</div>
                </div>
                <div style="background:#F1F5F9; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                    <div style="font-size:0.68rem; color:#0F172A;">Est. Travel Time</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{rb['duration_mins']} min</div>
                </div>
                <div style="background:#EFF6FF; padding:8px; border-radius:5px; border:1px solid #BFDBFE;">
                    <div style="font-size:0.68rem; color:#1E40AF;">Average AQI</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#2563EB;">{rb['avg_aqi']}</div>
                </div>
                <div style="background:#EFF6FF; padding:8px; border-radius:5px; border:1px solid #BFDBFE;">
                    <div style="font-size:0.68rem; color:#1E40AF;">Exposure Score</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#2563EB;">{rb['exposure_score']} / 100</div>
                </div>
            </div>
            <div style="font-size:0.75rem; color:#1E40AF;">
                Secondary transit corridor. Peak AQI: <b style="color:#2563EB;">{rb.get('max_aqi', rb.get('avg_aqi', 'N/A'))}</b>.
            </div>
        </div>""",
        unsafe_allow_html=True
    )

with card_c:
    st.markdown(
        f"""<div style="background:#FFFFFF; border:1px solid #14532D; border-top:3px solid #16A34A;
                        border-radius:10px; padding:16px 18px; min-height:250px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <b style="font-size:0.92rem; color:#0F172A;">{rc['name']}</b>
                <span style="background:rgba(22,163,74,0.15); border:1px solid #14532D; color:#16A34A;
                      font-size:0.68rem; font-weight:700; padding:2px 8px; border-radius:3px;">
                    🟢 ★ RECOMMENDED
                </span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:8px;">
                <div style="background:#F1F5F9; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                    <div style="font-size:0.68rem; color:#0F172A;">Distance</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{rc['distance_km']} km</div>
                </div>
                <div style="background:#F1F5F9; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                    <div style="font-size:0.68rem; color:#0F172A;">Est. Travel Time</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{rc['duration_mins']} min</div>
                </div>
                <div style="background:#F0FDF4; padding:8px; border-radius:5px; border:1px solid #BBF7D0;">
                    <div style="font-size:0.68rem; color:#166534;">Average AQI</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#16A34A;">{rc['avg_aqi']}</div>
                </div>
                <div style="background:#F0FDF4; padding:8px; border-radius:5px; border:1px solid #BBF7D0;">
                    <div style="font-size:0.68rem; color:#166534;">Exposure Score</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#16A34A;">{rc['exposure_score']} / 100</div>
                </div>
            </div>
            <div style="font-size:0.75rem; color:#166534;">
                <b style="color:#16A34A;">{route_data['reduction_pct']}% lower PM2.5 inhalation</b> vs Direct Arterial Route.
            </div>
        </div>""",
        unsafe_allow_html=True
    )

# ── 3.3 Route Map ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 3.3  Geospatial Route and Pollution Hotspot Map")
st.caption("Displaying 3 routes: 🟢 Clean-Air Corridor (Green, Recommended), 🔴 Direct Arterial Route (Red, High Exposure), 🔵 Alternative Corridor (Blue). Red circles indicate localized high-pollution hotspots avoided.")
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
    render_notification_center(get_pune_notifications())

with st.expander("Future Backend Integration — Module 3 Roadmap (Weeks 5–6)"):
    st.markdown("""
    - **Routing Engine:** Google Directions API with polyline waypoint decoding.
    - **Exposure Engine:** Numerical integration of predicted spatial AQI along route waypoints.
    - **Push Notifications:** Firebase Cloud Messaging (FCM) topic-based subscriptions.
    - **Progressive Web App:** Service worker registration for offline and background alerts.
    """)
