"""
Module 1 — Location and AQI Real-Time Data Integration — Dark Theme
"""

import streamlit as st
from datetime import datetime
from data.custom_dataset import load_pune_data

# Direct Pune Smart City Dataset Ingestion
LOCATIONS_DATA = load_pune_data()

from data.custom_dataset import (
    HEALTH_PROFILES, get_traffic_data,
    get_aqi_category_info, calculate_corridor_route_aqi
)
from components.metrics import (
    render_hero_aqi_card, render_pollutant_cards, render_weather_cards
)
from components.maps import render_pollution_map
from components.alerts import render_health_profile_card
from components.charts import render_station_comparison_barchart, render_traffic_aqi_correlation_chart
from components.sidebar import render_sidebar
import math

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in kilometers between two points on the earth."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_nearest_region(lat, lon, locations_dict):
    nearest_region = list(locations_dict.keys())[0] if locations_dict else "Error"
    min_dist = float('inf')
    for region, data in locations_dict.items():
        if "lat" in data and "lon" in data:
            dist = haversine(lat, lon, data["lat"], data["lon"])
            if dist < min_dist:
                min_dist = dist
                nearest_region = region
    return nearest_region

st.set_page_config(
    page_title="Module 1 — Real-Time AQI Integration | EcoAir Intelligence",
    page_icon=None, layout="wide"
)

# ── Dark theme CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #F8FAFC !important; }
section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
section[data-testid="stSidebar"] * { color: #0F172A !important; }
.block-container { padding-top: 1.8rem; padding-bottom: 2rem; max-width: 1380px; }
[data-testid="stMetric"] { background: #FFFFFF !important; border: 1px solid #334155 !important; border-radius: 8px; }
[data-testid="stMetricLabel"] { color: #0F172A !important; }
[data-testid="stMetricValue"] { color: #0F172A !important; }
.stButton > button { background: #FFFFFF !important; border: 1px solid #334155 !important; color: #334155 !important; border-radius: 5px; font-weight: 600; }
.stButton > button:hover { background: #EFF6FF !important; border-color: #3B82F6 !important; color: #1D4ED8 !important; }
.stButton > button:hover p { color: #1D4ED8 !important; }
.stButton > button[kind="primary"] { background: #1D4ED8 !important; border-color: #2563EB !important; color: white !important; }
[data-baseweb="select"] > div { background: #FFFFFF !important; border-color: #334155 !important; color: #0F172A !important; }
[data-testid="stExpander"] { background: #FFFFFF !important; border: 1px solid #334155 !important; border-radius: 6px; }
details summary { color: #334155 !important; font-weight: 600; font-size: 0.88rem; }
[data-testid="stAlert"] { background: #EFF6FF !important; border: 1px solid #BFDBFE !important; color: #1D4ED8 !important; }
hr { border-color: #334155 !important; }
h1, h2, h3, h4 { color: #0F172A !important; }
[data-testid="stCaptionContainer"] { color: #0F172A !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #F8FAFC; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────
if "selected_city"   not in st.session_state: st.session_state.selected_city   = list(LOCATIONS_DATA.keys())[0]
if "health_profile"  not in st.session_state: st.session_state.health_profile  = "General User"
if "alert_threshold" not in st.session_state: st.session_state.alert_threshold = 100
if "gps_status"      not in st.session_state: st.session_state.gps_status      = "Ready — Browser GPS Hook Active"
if "live_lat"        not in st.session_state: st.session_state.live_lat        = None
if "live_lon"        not in st.session_state: st.session_state.live_lon        = None
if "use_live_data"   not in st.session_state: st.session_state.use_live_data   = False
_city_keys = list(LOCATIONS_DATA.keys())
if "route_source"      not in st.session_state: st.session_state.route_source      = _city_keys[0] if _city_keys else ""
if "route_destination" not in st.session_state: st.session_state.route_destination = _city_keys[1] if len(_city_keys) > 1 else _city_keys[0] if _city_keys else ""

# ── Page Header ────────────────────────────────────────────────────────────
render_sidebar()
st.markdown("## Module 1 — Location and AQI Real-Time Data Integration")
st.caption(
    "Continuous localized air quality telemetry, meteorological parameter fusion, "
    "and health sensitivity management powered directly by the Pune Smart City sensor network."
)

st.markdown("---")

# ── 1.1 Location Management ────────────────────────────────────────────────
st.markdown("### 1.1  Location and Sensor Feed Configuration")
st.caption("Select a Source and Destination region from the Pune dataset to load AQI telemetry and visualise the route on the map.")

col_src, col_dst, col_gps, col_coords = st.columns([1.8, 1.8, 1.2, 1.2])
city_options = list(LOCATIONS_DATA.keys())

with col_src:
    src_idx = city_options.index(st.session_state.route_source) if st.session_state.route_source in city_options else 0
    chosen_source = st.selectbox(
        "📍 Source Region", options=city_options, index=src_idx,
        help="Starting point for AQI monitoring and route display.",
        disabled=st.session_state.use_live_data,
        key="src_select"
    )
    if not st.session_state.use_live_data:
        st.session_state.route_source = chosen_source
        st.session_state.selected_city = chosen_source

with col_dst:
    dst_idx = city_options.index(st.session_state.route_destination) if st.session_state.route_destination in city_options else (1 if len(city_options) > 1 else 0)
    chosen_destination = st.selectbox(
        "🏁 Destination Region", options=city_options, index=dst_idx,
        help="Endpoint region — route and AQI comparison will be shown on the map.",
        key="dst_select"
    )
    st.session_state.route_destination = chosen_destination

with col_gps:
    if st.button("📡 Device GPS", type="primary", use_container_width=True):
        with st.spinner("Acquiring coordinates..."):
            try:
                import requests
                res = requests.get("http://ip-api.com/json", timeout=3).json()
                st.session_state.live_lat = res['lat']
                st.session_state.live_lon = res['lon']
                st.session_state.use_live_data = True
                st.session_state.gps_status = "Active — Live Location Locked"
                nearest = get_nearest_region(st.session_state.live_lat, st.session_state.live_lon, LOCATIONS_DATA)
                st.session_state.selected_city = nearest
                st.session_state.route_source  = nearest
            except Exception:
                st.error("Could not fetch location. Check internet connection.")
    if st.session_state.use_live_data:
        if st.button("Reset GPS", use_container_width=True):
            st.session_state.use_live_data = False
            st.session_state.gps_status = "Ready — Browser GPS Hook Active"
            st.rerun()
    st.markdown(
        f"<div style='font-size:0.75rem; color:#0F172A; margin-top:5px;'>"
        f"Status: <b style='color:#16A34A;'>{st.session_state.gps_status}</b></div>",
        unsafe_allow_html=True
    )

# Resolve data dicts for source and destination
d = LOCATIONS_DATA.get(st.session_state.route_source, list(LOCATIONS_DATA.values())[0] if LOCATIONS_DATA else {})
d_dst = LOCATIONS_DATA.get(st.session_state.route_destination, d)

with col_coords:
    st.markdown("**Route Coordinates**")
    st.markdown(
        f"""<div style="background:#F1F5F9; border:1px solid #334155; padding:10px 12px;
                        border-radius:6px; font-family:monospace; font-size:0.78rem; line-height:1.9;
                        color:#334155;">
            <span style="color:#16A34A; font-weight:700;">SRC</span>&nbsp;
            {d['lat']:.4f} N, {d['lon']:.4f} E<br>
            <span style="color:#DC2626; font-weight:700;">DST</span>&nbsp;
            {d_dst['lat']:.4f} N, {d_dst['lon']:.4f} E
        </div>""",
        unsafe_allow_html=True
    )

# ── 1.2 AQI and Pollutant Telemetry ──────────────────────────────────────
st.markdown("---")
st.markdown("### 1.2  Air Quality Index and Chemical Pollutant Telemetry")

now_str = datetime.now().strftime("%d %b %Y, %H:%M IST")
data_source_label = "Pune Smart City Custom Dataset"
render_hero_aqi_card(
    aqi_val=d["aqi"],
    dominant_pollutant=d["dominant_pollutant"],
    last_updated=now_str,
    data_source=data_source_label
)
st.markdown("**Pollutant Sub-index Breakdown**")
render_pollutant_cards(d["pm25"], d["pm10"], d["no2"], d["o3"], d["co"], d["so2"])

# ── 1.3 Meteorology ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 1.3  Meteorological and Weather Conditions")
render_weather_cards(d["temp"], d["humidity"], d["wind_speed"], d["wind_deg"], d["weather_desc"])

# ── 1.4 Pollution Map ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 1.4  Regional Pollution Monitoring Map")
st.caption(
    "Blue dashed line = straight-line route between Source and Destination. "
    "Click any pin for AQI details. Use the button below to open turn-by-turn navigation."
)

# ── Route summary card ────────────────────────────────────────────────────
same_location = (st.session_state.route_source == st.session_state.route_destination)
if not same_location:
    route_info = calculate_corridor_route_aqi(
        st.session_state.route_source,
        st.session_state.route_destination,
        LOCATIONS_DATA
    )
    _src_cat = get_aqi_category_info(d['aqi'])
    _dst_cat = get_aqi_category_info(d_dst['aqi'])

    import textwrap
    waypoint_html = ""
    if route_info.get("intermediate_stations"):
        waypoint_list = ", ".join(f"{s['name']} (AQI {int(s['aqi'])})" for s in route_info['intermediate_stations'])
        waypoint_html = f"<div style='margin-top:5px; font-size:0.72rem; color:#0284C7;'>📡 <b>Corridor Waypoints Detected:</b> {waypoint_list}</div>"

    cards_html = textwrap.dedent(f"""
<div style="display:flex; gap:10px; margin-bottom:12px; flex-wrap:wrap;">
<div style="flex:1; min-width:170px; background:#FFFFFF; border:1px solid #334155; border-left:4px solid #16A34A; border-radius:6px; padding:10px 14px;">
<div style="font-size:0.65rem; font-weight:700; color:#0F172A; text-transform:uppercase; letter-spacing:0.8px;">Origin Station</div>
<div style="font-size:0.88rem; font-weight:700; color:#0F172A; margin:3px 0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{st.session_state.route_source}</div>
<div style="font-size:0.75rem; color:{_src_cat['color']}; font-weight:600;">AQI {int(d['aqi'])} — {_src_cat['label']}</div>
</div>
<div style="flex:1; min-width:170px; background:#FFFFFF; border:1px solid #334155; border-left:4px solid #DC2626; border-radius:6px; padding:10px 14px;">
<div style="font-size:0.65rem; font-weight:700; color:#0F172A; text-transform:uppercase; letter-spacing:0.8px;">Destination Station</div>
<div style="font-size:0.88rem; font-weight:700; color:#0F172A; margin:3px 0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{st.session_state.route_destination}</div>
<div style="font-size:0.75rem; color:{_dst_cat['color']}; font-weight:600;">AQI {int(d_dst['aqi'])} — {_dst_cat['label']}</div>
</div>
<div style="flex:1.4; min-width:240px; background:{route_info['bg_color']}; border:2px solid {route_info['color']}; border-radius:6px; padding:10px 16px;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:0.68rem; font-weight:800; color:{route_info['color']}; text-transform:uppercase; letter-spacing:0.9px;">🛣️ COMPOSITE ROUTE AQI</span>
<span style="background:{route_info['color']}22; color:{route_info['color']}; border:1px solid {route_info['color']}66; font-size:0.65rem; font-weight:700; padding:1px 6px; border-radius:3px;">{route_info['category']}</span>
</div>
<div style="display:flex; align-items:baseline; gap:8px; margin:3px 0;">
<span style="font-size:1.60rem; font-weight:900; color:{route_info['color']}; line-height:1;">{route_info['route_aqi']}</span>
<span style="font-size:0.72rem; color:#1E293B; font-weight:500;">Dominant: <b>{route_info['dominant_pollutant']}</b></span>
</div>
<div style="font-size:0.70rem; color:#0F172A;">Corridor Length: <b>{route_info['distance_km']} km</b> &nbsp;•&nbsp; Traffic: <b>{route_info['congestion_level']}</b></div>
</div>
</div>
<div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:6px; padding:10px 14px; margin-bottom:12px; font-size:0.75rem; color:#334155;">
<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
<div>
<b>📐 Corridor Multi-Factor Fusion:</b>&nbsp;
Base Chemical Pollutants (<span style="color:#0369A1; font-weight:700;">{route_info['base_aqi']}</span>)
<span style="color:#0F172A;">×</span>
Traffic Penalty (<span style="color:#EA580C; font-weight:700;">+{route_info['traffic_penalty_pct']}%</span>)
<span style="color:#0F172A;">×</span>
Weather Trapping (<span style="color:#7C3AED; font-weight:700;">{route_info['weather_impact_pct']:+.1f}%</span>)
<span style="color:#0F172A;">=</span>
<b style="color:{route_info['color']}; font-size:0.85rem;">{route_info['route_aqi']} AQI</b>
</div>
<div style="font-size:0.70rem; color:#0F172A;">Corridor Flow: {route_info['avg_speed_kmh']} km/h &nbsp;|&nbsp; RH: {route_info['avg_humidity']}% &nbsp;|&nbsp; Temp: {route_info['avg_temp']}°C</div>
</div>
{waypoint_html}
</div>
""").strip()

    st.markdown(cards_html, unsafe_allow_html=True)

map_col, chart_col = st.columns([1.7, 1.3])
with map_col:
    render_pollution_map(
        d, d.get("stations", []),
        source_data      = None if same_location else d,
        destination_data = None if same_location else d_dst,
        source_name      = st.session_state.route_source,
        destination_name = st.session_state.route_destination,
        route_info       = None if same_location else route_info,
    )
    # ── Google Maps navigation ─────────────────────────────────────────────
    if not same_location:
        gmaps_url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={d['lat']},{d['lon']}"
            f"&destination={d_dst['lat']},{d_dst['lon']}"
            f"&travelmode=driving"
        )
        st.link_button("🗺️ Open Route in Google Maps", gmaps_url, type="primary")
with chart_col:
    render_station_comparison_barchart(d.get("stations", []))

# ── 1.5 Health Profile ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 1.5  Health Sensitivity Profile and Alert Configuration")

hp_col, guidance_col = st.columns([1.2, 1.8])

with hp_col:
    hp_options = list(HEALTH_PROFILES.keys())
    selected_hp = st.selectbox(
        "Health Sensitivity Profile", options=hp_options,
        index=hp_options.index(st.session_state.health_profile)
            if st.session_state.health_profile in hp_options else 0,
        help="Adjusts thresholds and advisory guidance."
    )
    st.session_state.health_profile = selected_hp

    thresh = st.slider(
        "Custom AQI Alert Threshold",
        min_value=30, max_value=300,
        value=HEALTH_PROFILES[selected_hp]["recommended_threshold"],
        step=5
    )
    st.session_state.alert_threshold = thresh

with guidance_col:
    render_health_profile_card(selected_hp, d["aqi"])

# ── 1.6 Traffic Details ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 1.6  Traffic Conditions and Vehicular Emission Correlation")
st.caption(
    "Real-time traffic congestion data fused with AQI telemetry to quantify vehicular emission loading. "
    "Congestion level directly amplifies PM2.5, NO\u2082, and CO concentrations via the emission multiplier."
)

traffic = get_traffic_data(st.session_state.selected_city)

# ── Congestion Level Banner ────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="background:{traffic['level_bg']}; border:1px solid {traffic['level_color']}60;
                border-left:5px solid {traffic['level_color']}; border-radius:8px;
                padding:16px 22px; margin-bottom:16px;
                display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
        <div>
            <div style="font-size:0.70rem; font-weight:700; color:{traffic['level_color']};
                        text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
                Live Traffic Congestion Level
            </div>
            <div style="font-size:1.65rem; font-weight:800; color:{traffic['level_color']}; line-height:1;">
                {traffic['congestion_level']}
            </div>
            <div style="font-size:0.76rem; color:#0F172A; margin-top:4px;">
                Source: {traffic['api_source']}
            </div>
        </div>
        <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
            <div style="font-size:0.72rem; color:#0F172A;">Congestion Score</div>
            <div style="font-size:2.0rem; font-weight:800; color:{traffic['level_color']}; line-height:1;">
                {traffic['congestion_score']}<span style="font-size:0.9rem; font-weight:500;">/100</span>
            </div>
            <div style="font-size:0.70rem; color:#0F172A;">Peak Hours: {traffic['peak_hour']}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ── Traffic Metrics Grid ───────────────────────────────────────────────────
traf_m1, traf_m2, traf_m3, traf_m4 = st.columns(4)
traffic_metrics = [
    (traf_m1, "Avg. Vehicle Speed",     f"{traffic['avg_speed_kmh']} km/h", "Road flow velocity",        "#0369A1"),
    (traf_m2, "Vehicles per Hour",      f"{traffic['vehicle_count_per_hr']:,}", "Passage count (est.)",  "#7C3AED"),
    (traf_m3, "Emission Multiplier",    f"\u00d7{traffic['emission_multiplier']}", "vs. free-flow baseline", traffic['level_color']),
    (traf_m4, "Dominant Pollutant",     d["dominant_pollutant"],            "Traffic-driven species",    "#EA580C"),
]
for col, title, value, sub, color in traffic_metrics:
    with col:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #334155; border-top:3px solid {color};
                        border-radius:8px; padding:14px 16px;">
                <div style="font-size:0.68rem; font-weight:700; color:#0F172A;
                            text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px;">
                    {title}
                </div>
                <div style="font-size:1.45rem; font-weight:800; color:{color}; margin-bottom:2px;">
                    {value}
                </div>
                <div style="font-size:0.70rem; color:#0F172A;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Road Segment Breakdown + Correlation Chart ─────────────────────────────
seg_col, chart_col = st.columns([1.0, 1.8])

with seg_col:
    st.markdown(
        "<div style='font-size:0.75rem; font-weight:700; color:#0F172A; "
        "text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;'>Road Segment Status</div>",
        unsafe_allow_html=True
    )
    for seg in traffic["road_segments"]:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; justify-content:space-between;
                        background:#FFFFFF; border:1px solid #334155; border-radius:5px;
                        padding:9px 14px; margin-bottom:6px;">
                <span style="font-size:0.79rem; color:#334155; font-weight:500;">{seg['segment']}</span>
                <span style="background:{seg['color']}18; border:1px solid {seg['color']}55;
                      color:{seg['color']}; font-size:0.68rem; font-weight:700;
                      padding:2px 9px; border-radius:3px; white-space:nowrap;">
                    {seg['congestion']}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

with chart_col:
    render_traffic_aqi_correlation_chart(traffic, d)

# ── Traffic Roadmap ────────────────────────────────────────────────────────
with st.expander("Traffic API Backend Integration — Roadmap"):
    st.markdown("""
    - **TomTom Traffic API v5:** `/trafficModelData`, `/flowSegmentData` — real-time congestion index, jam factor (0–10), average speed per road segment.
    - **HERE Traffic v7:** Incident feed, flow data and historical speed profiles for Pune arterial roads.
    - **Google Maps Platform — Routes API:** `computeRoutes` with traffic-aware travel durations for emission exposure modelling.
    - **Emission Model:** MOVES (EPA) / HBEFA v4 speed-emission factors mapped to congestion score to derive hourly PM2.5 / NO\u2082 / CO loading.
    - **Integration Point:** Emission multiplier will feed directly into Module 3 route exposure scoring.
    """)

# ── Roadmap ────────────────────────────────────────────────────────────────
with st.expander("Future Backend Integration — Module 1 Roadmap (Weeks 1–2)"):
    st.markdown("""
    - **Geolocation:** HTML5 `navigator.geolocation` with Google Maps reverse geocoding.
    - **AQI Ingestion:** OpenAQ REST API v2, WAQI API, CPCB sensor feeds via scheduled pipeline.
    - **Meteorology:** OpenWeatherMap API v3.0 for temperature inversions, PBLH, wind vectors.
    - **Persistence:** InfluxDB / PostgreSQL TimescaleDB for time-series sensor telemetry archival.
    """)
