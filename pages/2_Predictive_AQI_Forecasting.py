"""
Module 2 — Predictive AQI Forecasting Model & Spatial Geostatistics
EcoAir Intelligence System
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

from data.demo_data import get_aqi_category_info
from data.custom_dataset import load_pune_data, get_pune_historical_timeseries
from components.metrics import render_demo_banner
from components.charts import render_aqi_forecast_chart, render_pollutant_forecast_chart
from components.sidebar import render_sidebar
from ml.models import AQIPredictor
from ml.spatial_interpolation import get_spatial_interpolator
from ml.retrain_pipeline import RetrainingPipeline
from ml.route_exposure import RoutePollutionEstimator
from components.maps import render_route_map
from components.alerts import render_travel_advisory_card

st.set_page_config(
    page_title="Module 2 — Predictive AQI Forecasting | EcoAir Intelligence",
    page_icon=None, layout="wide"
)

# ── Styling ──────────────────────────────────────────────────────────────────
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
[data-testid="stMetricDelta"] { color: #64748B !important; }
.stButton > button { background: #FFFFFF !important; border: 1px solid #334155 !important; border-radius: 5px; font-weight: 600; }
.stButton > button[kind="primary"] { background: #1D4ED8 !important; border-color: #2563EB !important; color: white !important; }
[data-baseweb="select"] > div { background: #FFFFFF !important; border-color: #334155 !important; color: #0F172A !important; }
[data-testid="stExpander"] { background: #FFFFFF !important; border: 1px solid #334155 !important; border-radius: 6px; }
details summary { color: #334155 !important; font-weight: 600; font-size: 0.88rem; }
[data-testid="stAlert"] { background: #EFF6FF !important; border: 1px solid #BFDBFE !important; color: #1D4ED8 !important; }
hr { border-color: #334155 !important; }
h1, h2, h3, h4 { color: #0F172A !important; }
[data-testid="stCaptionContainer"] { color: #64748B !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #F8FAFC; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# Strictly load real preprocessed Pune dataset
pune_data = load_pune_data()
ALL_LOCATIONS = pune_data

if "selected_city" not in st.session_state or st.session_state.selected_city not in ALL_LOCATIONS:
    st.session_state.selected_city = list(ALL_LOCATIONS.keys())[0] if ALL_LOCATIONS else "Hadapsar_Gadital_01"

render_sidebar()

# Initialize ML services
predictor = AQIPredictor()
interpolator = get_spatial_interpolator(ALL_LOCATIONS)
pipeline = RetrainingPipeline()

# ── Page Header ────────────────────────────────────────────────────────────
st.markdown("## Module 2 — Predictive AQI Forecasting & Spatial Geostatistics")
st.caption(
    "Multi-step recurrent time-series forecasting (PyTorch GRU), spatial geostatistical interpolation (IDW / Ordinary Kriging), "
    "and automated continuous learning pipelines trained on Pune SmartCity telemetry."
)

meta = predictor.model_meta
trained_status = meta.get("last_trained_timestamp", "Active (Pre-trained Checkpoint)")
arch_metrics = meta.get("architectures", {})

st.markdown(
    f"""<div style="background:#FFFFFF; border:1px solid #334155; border-left:4px solid #10B981;
                    padding:12px 18px; border-radius:6px; margin-bottom:18px; display:flex;
                    justify-content:space-between; align-items:center;">
        <div>
            <b style="color:#0F172A; font-size:0.92rem;">Operational ML Engine Status: ACTIVE</b>
            <div style="color:#64748B; font-size:0.78rem;">
                Trained Architecture: PyTorch GRU (Gated Recurrent Unit) | Input Lags: 24h (10 features) | Last Retrained: {trained_status}
            </div>
        </div>
        <div style="text-align:right;">
            <span style="background:#ECFDF5; border:1px solid #10B981; color:#065F46;
                         font-size:0.75rem; font-weight:700; padding:4px 10px; border-radius:4px;">
                GRU Checkpoint Ready
            </span>
        </div>
    </div>""",
    unsafe_allow_html=True
)

tab_forecast, tab_spatial, tab_route, tab_fastapi_retrain = st.tabs([
    "📈 1. GRU Forecasting (1–24h)",
    "🗺️ 2. Ordinary Kriging Geostatistics",
    "🚗 3. Route Pollution Exposure Estimator",
    "⚡ 4 & 5. FastAPI Prediction Service & Retraining"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: 1-24h Recurrent Forecasting
# ═════════════════════════════════════════════════════════════════════════════
with tab_forecast:
    st.markdown("### 2.1  Recurrent Forecasting Configuration")
    c1, c2, c3, c4 = st.columns([1.8, 1.2, 1.4, 1.0])

    with c1:
        city_keys = list(ALL_LOCATIONS.keys())
        default_idx = city_keys.index(st.session_state.selected_city) if st.session_state.selected_city in city_keys else 0
        selected_loc = st.selectbox("Target Location / Station", options=city_keys, index=default_idx)
        st.session_state.selected_city = selected_loc

    with c2:
        horizon_map = {"1 Hour": 1, "3 Hours": 3, "6 Hours": 6, "12 Hours": 12, "24 Hours": 24}
        chosen_label = st.selectbox("Prediction Horizon", list(horizon_map.keys()), index=4)
        horizon_hours = horizon_map[chosen_label]

    with c3:
        st.markdown(
            """<div style="padding-top:4px;">
                <div style="font-size:0.78rem; color:#64748B; font-weight:600; margin-bottom:4px;">Inference Neural Architecture</div>
                <div style="background:#FFFFFF; border:1px solid #334155; border-radius:5px; padding:7px 12px; font-weight:700; color:#1D4ED8; font-size:0.86rem; display:flex; align-items:center; gap:8px;">
                    <span style="height:8px; width:8px; background:#10B981; border-radius:50%; display:inline-block;"></span>
                    PyTorch GRU Forecaster
                </div>
            </div>""",
            unsafe_allow_html=True
        )

    with c4:
        st.write(" "); st.write(" ")
        run_btn = st.button("Run Forecast", use_container_width=True, type="primary")

    station_data = ALL_LOCATIONS.get(selected_loc, {})

    # Execute GRU inference
    arch_type = "GRU"
    pred_res = predictor.predict(
        current_data=station_data,
        architecture="GRU",
        horizon=horizon_hours
    )

    hist_df = get_pune_historical_timeseries(selected_loc, 24)

    # Build forecast dataframe from real model output
    start_time = pd.Timestamp.now().floor("h")
    future_times = [start_time + pd.Timedelta(hours=i) for i in range(1, horizon_hours + 1)]

    forecast_df = pd.DataFrame({
        "timestamp": future_times,
        "aqi": pred_res["aqi_trajectory"],
        "lower_bound": pred_res["lower_bound"],
        "upper_bound": pred_res["upper_bound"],
        "pm25": pred_res["pm25_trajectory"],
        "pm10": pred_res["pm10_trajectory"],
        "no2": pred_res["no2_trajectory"]
    })

    current_aqi = float(station_data.get("aqi", pred_res["current_aqi"]))
    final_pred_aqi = float(forecast_df["aqi"].iloc[-1])
    aqi_delta = final_pred_aqi - current_aqi
    trend_label = "Worsening" if aqi_delta > 0 else "Improving"
    pred_cat = get_aqi_category_info(final_pred_aqi)

    # ── Summary Metrics ──
    st.markdown("---")
    st.markdown("### 2.2  Forecast Summary & Horizon Projection")
    mc1, mc2, mc3, mc4 = st.columns(4)

    with mc1:
        st.metric("Current Observed AQI", f"{int(current_aqi)}")
    with mc2:
        st.metric(
            f"Predicted AQI ({chosen_label})", f"{int(final_pred_aqi)}",
            delta=f"{aqi_delta:+.1f}  ({trend_label})", delta_color="inverse"
        )
    with mc3:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:#64748B; font-weight:600; margin-bottom:4px;">
                    Predicted Severity Category
                </div>
                <div style="font-size:1.1rem; font-weight:700; color:{pred_cat['color']};">
                    {pred_cat['label']}
                </div>
                <div style="font-size:0.72rem; color:#64748B;">{pred_cat['severity']}</div>
            </div>""",
            unsafe_allow_html=True
        )
    with mc4:
        low_b = forecast_df["lower_bound"].iloc[-1]
        up_b  = forecast_df["upper_bound"].iloc[-1]
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:#64748B; font-weight:600; margin-bottom:4px;">
                    95% Confidence Interval
                </div>
                <div style="font-size:1.1rem; font-weight:700; color:#818CF8;">
                    {int(low_b)} — {int(up_b)} AQI
                </div>
                <div style="font-size:0.72rem; color:#64748B;">Margin: +/- {(up_b-low_b)/2:.1f}</div>
            </div>""",
            unsafe_allow_html=True
        )

    # ── Forecast Chart ──
    st.markdown("---")
    st.markdown("### 2.3  Continuous Multi-Step Predictive Trajectory")
    st.caption("Historical 24-hour sensor observations transitioning into neural network forecast curve with 95% Confidence Interval ribbon.")
    render_aqi_forecast_chart(hist_df, forecast_df, horizon_hours)

    # ── Pollutant Forecast ──
    st.markdown("---")
    st.markdown("### 2.4  Multi-Pollutant Endpoint Breakdown")
    pc1, pc2 = st.columns([1.7, 1.0])

    with pc1:
        render_pollutant_forecast_chart(forecast_df)

    with pc2:
        st.markdown("**Endpoint Pollutant Concentrations**")
        st.caption(f"Projected at horizon +{horizon_hours} hours.")
        poll_rows = [
            {"label": "PM2.5 Particulate", "val": f"{forecast_df['pm25'].iloc[-1]:.1f} ug/m3"},
            {"label": "PM10 Inhalable",    "val": f"{forecast_df['pm10'].iloc[-1]:.1f} ug/m3"},
            {"label": "NO2 Nitrogen Oxide","val": f"{forecast_df['no2'].iloc[-1]:.1f} ppb"},
        ]
        for row in poll_rows:
            st.markdown(
                f"""<div style="display:flex; justify-content:space-between; align-items:center;
                                background:#FFFFFF; padding:8px 12px; border-radius:5px;
                                border:1px solid #334155; margin-bottom:6px;">
                    <span style="font-weight:600; color:#334155; font-size:0.86rem;">{row['label']}</span>
                    <span style="font-weight:700; color:#0369A1; font-size:0.86rem;">{row['val']}</span>
                </div>""",
                unsafe_allow_html=True
            )

        st.info(f"**CPCB Recommendation:** {pred_res['recommendation']}")

    # Model Architecture metadata
    with st.expander("PyTorch GRU Architecture & Evaluation Metrics", expanded=False):
        m_info = arch_metrics.get("GRU", {})
        st.markdown(fr"""
        - **Architecture:** `PyTorch GRU (Gated Recurrent Unit)` (2-layer Stacked Recurrence with Dropout & Linear Multi-Horizon Projection)
        - **Hidden Dimensions:** 64 hidden units per GRU cell, recurrent dropout rate: 0.2
        - **Input Sequence Length:** 24 timesteps ($t-23 \dots t$)
        - **Input Features (10):** Lagged AQI, PM2.5, PM10, NO2, O3, CO, SO2, Ambient Temperature, Humidity, Traffic Congestion Index
        - **Validation RMSE:** `{m_info.get('rmse', '35.35')}` AQI
        - **Validation MAE:** `{m_info.get('mae', '30.40')}` AQI
        - **R² Score:** `{m_info.get('r2_score', '0.70')}`
        """)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: Spatial Interpolation (Ordinary Kriging)
# ═════════════════════════════════════════════════════════════════════════════
with tab_spatial:
    st.markdown("### 2.5  Spatial AQI Interpolation (Ordinary Kriging)")
    st.caption(
        "Estimate localized ambient air quality at arbitrary geographic coordinates between physical monitoring stations using "
        "the **Best Linear Unbiased Estimator (Ordinary Kriging with Gaussian Semivariogram)**, continuous dispersion surfaces, "
        "and spatial estimation variance."
    )

    # ── Region Metadata for all 10 Pune Dataset Stations ──
    PUNE_REGIONS_META = {
        "BopadiSquare_65": {"name": "Bopodi Square", "area": "North Pune (Old Mumbai Hwy)", "lat": 18.55943, "lon": 73.82866},
        "Karve Statue Square_5": {"name": "Karve Statue Square", "area": "Kothrud (West Pune)", "lat": 18.50173, "lon": 73.81360},
        "Lullanagar_Square_14": {"name": "Lullanagar Square", "area": "Kondhwa / South-East Pune", "lat": 18.48731, "lon": 73.88565},
        "Hadapsar_Gadital_01": {"name": "Hadapsar Gadital", "area": "Hadapsar (East Industrial)", "lat": 18.50183, "lon": 73.94148},
        "PMPML_Bus_Depot_Deccan_15": {"name": "PMPML Depot Deccan", "area": "Deccan Gymkhana / Swargate", "lat": 18.45172, "lon": 73.85617},
        "Goodluck Square_Cafe_23": {"name": "Goodluck Square Cafe", "area": "FC Road / Shivajinagar", "lat": 18.53436, "lon": 73.82606},
        "Chitale Bandhu Corner_41": {"name": "Chitale Bandhu Corner", "area": "Bajirao Road / Sadashiv Peth", "lat": 18.51557, "lon": 73.82439},
        "Pune Railway Station_28": {"name": "Pune Railway Station", "area": "Central Pune (Transit Hub)", "lat": 18.52507, "lon": 73.79293},
        "Rajashri_Shahu_Bus_stand_19": {"name": "Rajashri Shahu Bus Stand", "area": "Katraj (South Pune)", "lat": 18.48224, "lon": 73.85809},
        "Dr Baba Saheb Ambedkar Sethu Junction_60": {"name": "Babasaheb Ambedkar Sethu", "area": "Aundh / Khadki Corridor", "lat": 18.55176, "lon": 73.83065},
    }

    # Station coordinates dict from dataset
    pune_stn_coords = {
        name: (s_data["lat"], s_data["lon"])
        for name, s_data in ALL_LOCATIONS.items()
    }

    # Format options nicely for selectbox
    dropdown_map = {}
    for stn_id, meta in PUNE_REGIONS_META.items():
        if stn_id in ALL_LOCATIONS:
            s_aqi = int(ALL_LOCATIONS[stn_id].get("aqi", 0))
            label = f"📍 {meta['name']} — {meta['area']} [{stn_id}] (Observed AQI: {s_aqi})"
            dropdown_map[label] = (pune_stn_coords.get(stn_id, (meta["lat"], meta["lon"])))

    # Additional intermediate / arbitrary corridor test points
    dropdown_map["Arbitrary Point: Deccan–Hadapsar Corridor (Between Stations)"] = (18.5130, 73.8830)
    dropdown_map["Arbitrary Point: Bopodi–Station Corridor (Between Stations)"] = (18.5440, 73.8510)
    dropdown_map["Arbitrary Point: Katraj–Swargate Corridor (Between Stations)"] = (18.4796, 73.8631)
    dropdown_map["Custom Coordinates (Type Below)"] = (18.5204, 73.8567)

    dropdown_labels = list(dropdown_map.keys())

    # Initialize lat/lon session state if missing
    if "kriging_lat_val" not in st.session_state:
        st.session_state["kriging_lat_val"] = float(dropdown_map[dropdown_labels[0]][0])
    if "kriging_lon_val" not in st.session_state:
        st.session_state["kriging_lon_val"] = float(dropdown_map[dropdown_labels[0]][1])

    # Region change handler
    def _handle_region_selection():
        selected = st.session_state.get("kriging_region_choice")
        if selected in dropdown_map and not selected.startswith("Custom"):
            c_lat, c_lon = dropdown_map[selected]
            st.session_state["kriging_lat_val"] = float(c_lat)
            st.session_state["kriging_lon_val"] = float(c_lon)

    sc1, sc2, sc3, sc4 = st.columns([2.0, 1.3, 1.3, 1.0])

    with sc1:
        st.selectbox(
            "📍 Select Pune Dataset Region / Physical Monitoring Station",
            dropdown_labels,
            index=0,
            key="kriging_region_choice",
            on_change=_handle_region_selection,
            help="Select any of the 10 real monitoring regions from the preprocessed Pune dataset to focus interpolation."
        )

    with sc2:
        target_lat = st.number_input("Target Latitude (°N)", format="%.5f", step=0.005, key="kriging_lat_val")

    with sc3:
        target_lon = st.number_input("Target Longitude (°E)", format="%.5f", step=0.005, key="kriging_lon_val")

    with sc4:
        st.write(" "); st.write(" ")
        st.button("Interpolate AQI", use_container_width=True, type="primary")

    # ── Quick-Select Region Pills ──
    st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#64748B; margin:6px 0 4px 0;'>QUICK-SELECT PUNE DATASET REGION:</div>", unsafe_allow_html=True)
    pill_cols = st.columns(5)
    for idx, (stn_id, meta) in enumerate(PUNE_REGIONS_META.items()):
        col_idx = idx % 5
        s_data = ALL_LOCATIONS.get(stn_id, {})
        s_aqi = int(s_data.get("aqi", 0))
        s_cat = get_aqi_category_info(s_aqi)
        with pill_cols[col_idx]:
            btn_label = f"{meta['name']} ({s_aqi})"
            if st.button(btn_label, key=f"quick_reg_{stn_id}", use_container_width=True):
                st.session_state["kriging_lat_val"] = float(s_data.get("lat", meta["lat"]))
                st.session_state["kriging_lon_val"] = float(s_data.get("lon", meta["lon"]))
                st.rerun()

    # Run Ordinary Kriging directly
    interp_result = interpolator.kriging(target_lat, target_lon)
    est_aqi = interp_result["estimated_aqi"]
    cat_info = get_aqi_category_info(est_aqi)

    st.markdown("---")
    res_c1, res_c2, res_c3, res_c4 = st.columns(4)

    with res_c1:
        st.metric("Estimated Localized AQI", f"{int(est_aqi)}", delta=cat_info["label"])
    with res_c2:
        st.metric("Nearest Physical Station", f"{interp_result.get('nearest_station', 'N/A')[:18]}",
                  delta=f"{interp_result.get('distance_km', 0.0)} km away")
    with res_c3:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:#64748B; font-weight:600; margin-bottom:4px;">
                    Spatial Confidence Score
                </div>
                <div style="font-size:1.1rem; font-weight:700; color:#10B981;">
                    {int(interp_result.get('confidence', 0.85) * 100)}%
                </div>
                <div style="font-size:0.72rem; color:#64748B;">Algorithm: Ordinary Kriging (Gaussian)</div>
            </div>""",
            unsafe_allow_html=True
        )
    with res_c4:
        var_score = interp_result.get("kriging_variance") or interp_result.get("uncertainty_score", 3.2)
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:#64748B; font-weight:600; margin-bottom:4px;">
                    Spatial Estimation Variance
                </div>
                <div style="font-size:1.1rem; font-weight:700; color:#F59E0B;">
                    {var_score:.2f}
                </div>
                <div style="font-size:0.72rem; color:#64748B;">Uncertainty Margin: +/- {np.sqrt(var_score):.1f} AQI</div>
            </div>""",
            unsafe_allow_html=True
        )

    # ── Interactive Spatial Folium Map with Visible Region Markers ──
    map_ctrl1, map_ctrl2 = st.columns([2.5, 1.5])
    with map_ctrl1:
        st.markdown("#### Geographic Interpolation Map & 10 Pune Monitoring Regions")
    with map_ctrl2:
        show_dispersion_heatmap = st.checkbox("Show Kriging Continuous Dispersion Surface", value=True)

    m = folium.Map(
        location=[18.515, 73.850],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # Add continuous Ordinary Kriging dispersion heatmap across Pune regions
    if show_dispersion_heatmap:
        try:
            kriging_grid = interpolator.generate_grid(
                lat_min=18.445, lat_max=18.570,
                lon_min=73.785, lon_max=73.950,
                grid_steps=12,
                method="kriging"
            )
            heat_pts = [[pt["lat"], pt["lon"], float(pt["aqi"])] for pt in kriging_grid]
            HeatMap(
                heat_pts,
                radius=32,
                blur=22,
                min_opacity=0.35,
                max_zoom=13
            ).add_to(m)
        except Exception:
            pass

    # Add interpolated target marker
    folium.Marker(
        [target_lat, target_lon],
        popup=f"<b>🎯 Interpolated Target:</b><br>AQI: <b>{int(est_aqi)}</b> ({cat_info['label']})<br>Lat: {target_lat:.4f}, Lon: {target_lon:.4f}",
        tooltip=f"Interpolated Target: {int(est_aqi)} AQI",
        icon=folium.Icon(color="red", icon="screenshot", prefix="glyphicon")
    ).add_to(m)

    # Add 3km interpolation influence radius
    folium.Circle(
        [target_lat, target_lon],
        radius=3000,
        color="#2563EB",
        fill=True,
        fill_opacity=0.08,
        weight=1.5,
        dash_array="5 5",
        tooltip="Interpolation Estimation Radius (3 km)"
    ).add_to(m)

    # Add ALL 10 Pune monitoring stations with CircleMarker AND permanent region labels
    for s_name, s_info in ALL_LOCATIONS.items():
        if "lat" in s_info and "lon" in s_info:
            s_lat = s_info["lat"]
            s_lon = s_info["lon"]
            s_aqi = s_info.get("aqi", 70)
            s_cat = get_aqi_category_info(s_aqi)
            reg_meta = PUNE_REGIONS_META.get(s_name, {"name": s_name, "area": "Pune"})
            reg_display_name = reg_meta["name"]

            # Station Circle Marker
            folium.CircleMarker(
                [s_lat, s_lon],
                radius=11,
                color="#0F172A",
                fill=True,
                fill_color=s_cat["color"],
                fill_opacity=0.92,
                weight=2,
                tooltip=f"Region: {reg_display_name} ({s_name}) | AQI: {int(s_aqi)}",
                popup=f"""<div style='font-size:12px; line-height:1.4; min-width:180px;'>
                    <b style='color:#0F172A; font-size:13px;'>{reg_display_name}</b><br>
                    <span style='color:#64748B; font-size:11px;'>ID: {s_name} | {reg_meta['area']}</span><br>
                    <div style='margin-top:4px; padding:3px 6px; background:{s_cat['color']}22; border:1px solid {s_cat['color']}; border-radius:3px;'>
                        <b>Observed AQI:</b> <span style='color:{s_cat['color']}; font-weight:800;'>{int(s_aqi)} ({s_cat['label']})</span>
                    </div>
                    <b>Dominant Pollutant:</b> {s_info.get('dominant_pollutant', 'PM2.5')}<br>
                    <b>PM2.5:</b> {s_info.get('pm25', 0.0):.1f} µg/m³ &nbsp;|&nbsp; <b>PM10:</b> {s_info.get('pm10', 0.0):.1f} µg/m³<br>
                    <b>NO2:</b> {s_info.get('no2', 0.0):.1f} µg/m³ &nbsp;|&nbsp; <b>CO:</b> {s_info.get('co', 0.0):.1f} µg/m³<br>
                    <b>GPS:</b> ({s_lat:.4f}, {s_lon:.4f})
                </div>"""
            ).add_to(m)

            # Permanent text badge displaying region name & AQI directly on the map
            folium.Marker(
                [s_lat, s_lon],
                icon=folium.DivIcon(
                    html=f"""<div style="font-family:'Inter',system-ui,sans-serif; font-size:10px; font-weight:700; color:#0F172A;
                                background:#FFFFFF; border:1px solid #334155; border-radius:4px; padding:2px 6px;
                                white-space:nowrap; box-shadow:0 1px 4px rgba(0,0,0,0.22); transform:translate(-50%, -26px); pointer-events:none;">
                                📍 {reg_display_name} <span style="color:{s_cat['color']}; font-weight:800;">({int(s_aqi)})</span>
                            </div>"""
                )
            ).add_to(m)

    # Frame bounds to encompass all 10 Pune monitoring stations
    m.fit_bounds([[18.44, 73.78], [18.57, 73.95]])

    st_folium(m, use_container_width=True, height=440, returned_objects=[], key="kriging_spatial_folium_map")

    # Contributing station weights
    if "contributing_stations" in interp_result and interp_result["contributing_stations"]:
        st.markdown("**Top Contributing Stations (Ordinary Kriging Weights λ)**")
        w_cols = st.columns(len(interp_result["contributing_stations"]))
        for idx, (st_name, st_w) in enumerate(interp_result["contributing_stations"].items()):
            reg_disp = PUNE_REGIONS_META.get(st_name, {}).get("name", st_name[:16])
            with w_cols[idx]:
                st.markdown(
                    f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:6px; padding:8px 12px; text-align:center;">
                        <div style="font-size:0.75rem; color:#0F172A; font-weight:700;">{reg_disp}</div>
                        <div style="font-size:0.68rem; color:#64748B;">{st_name[:14]}</div>
                        <div style="font-size:1.05rem; font-weight:800; color:#1D4ED8; margin-top:2px;">{st_w:+.3f}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

    # ── Cards Grid Displaying All 10 Pune Dataset Regions ──
    st.markdown("#### 📍 All 10 Preprocessed Pune Dataset Monitoring Regions")
    st.caption("Real telemetry aggregated across all rows from the preprocessed Pune sensor network.")

    card_cols = st.columns(5)
    for idx, (stn_id, meta) in enumerate(PUNE_REGIONS_META.items()):
        c_idx = idx % 5
        s_data = ALL_LOCATIONS.get(stn_id, {})
        s_aqi = int(s_data.get("aqi", 0))
        s_cat = get_aqi_category_info(s_aqi)
        with card_cols[c_idx]:
            st.markdown(
                f"""<div style="background:#FFFFFF; border:1px solid #334155; border-radius:8px; padding:12px; margin-bottom:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <div style="font-size:0.84rem; font-weight:700; color:#0F172A; line-height:1.2;">{meta['name']}</div>
                    <div style="font-size:0.70rem; color:#64748B; margin-bottom:6px;">{meta['area']}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-size:1.35rem; font-weight:800; color:{s_cat['color']};">{s_aqi}</span>
                        <span style="font-size:0.70rem; font-weight:700; color:{s_cat['color']}; background:{s_cat['color']}18; padding:2px 6px; border-radius:3px; border:1px solid {s_cat['color']}44;">
                            {s_cat['label']}
                        </span>
                    </div>
                    <div style="font-size:0.70rem; color:#475569; line-height:1.4;">
                        <b>PM2.5:</b> {s_data.get('pm25', 0.0):.1f} µg/m³<br>
                        <b>PM10:</b> {s_data.get('pm10', 0.0):.1f} µg/m³<br>
                        <b>Dominant:</b> {s_data.get('dominant_pollutant', 'PM2.5')}<br>
                        <b>GPS:</b> {s_data.get('lat', meta['lat']):.4f}, {s_data.get('lon', meta['lon']):.4f}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

    # ── Display Directory Table of all 10 Pune Dataset Regions ──
    with st.expander("📊 Detailed Telemetry Table (All 10 Monitoring Stations)", expanded=False):
        st_rows = []
        for idx, (s_name, s_data) in enumerate(ALL_LOCATIONS.items(), 1):
            s_cat = get_aqi_category_info(s_data.get("aqi", 0))
            meta = PUNE_REGIONS_META.get(s_name, {"name": s_name, "area": "Pune"})
            st_rows.append({
                "#": idx,
                "Region Name": meta["name"],
                "Station Sensor ID": s_name,
                "Geographic Area": meta["area"],
                "Latitude": f"{s_data.get('lat', 0.0):.5f}",
                "Longitude": f"{s_data.get('lon', 0.0):.5f}",
                "Observed AQI": f"{int(s_data.get('aqi', 0))}",
                "Category": s_cat["label"],
                "Dominant Pollutant": s_data.get("dominant_pollutant", "PM2.5"),
                "PM2.5 (ug/m3)": f"{s_data.get('pm25', 0.0):.1f}",
                "PM10 (ug/m3)": f"{s_data.get('pm10', 0.0):.1f}",
                "NO2 (ug/m3)": f"{s_data.get('no2', 0.0):.1f}",
            })
        st.dataframe(pd.DataFrame(st_rows), use_container_width=True, hide_index=True)



# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: Travel Route Pollution Exposure Estimator (Item 3)
# ═════════════════════════════════════════════════════════════════════════════
with tab_route:
    st.markdown("### 2.6  Travel Route Pollution Exposure Estimator")
    st.caption(
        "Calculates expected cumulative particulate AQI exposure along planned travel routes using "
        "Google Directions API waypoint discretization and **Ordinary Kriging** spatial interpolation."
    )

    pune_stns = list(ALL_LOCATIONS.keys())
    dropdown_options = pune_stns + ["Type Custom Landmark / Address..."]

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#0F172A; margin-bottom:4px;'>Origin Landmark / Station</div>", unsafe_allow_html=True)
        orig_choice = st.selectbox(
            "Origin Landmark / Station",
            options=dropdown_options,
            index=dropdown_options.index("Hadapsar_Gadital_01") if "Hadapsar_Gadital_01" in dropdown_options else 0,
            key="m2_orig_station_select",
            label_visibility="collapsed"
        )
        if orig_choice == "Type Custom Landmark / Address...":
            route_origin = st.text_input("Type Origin Landmark", value="Swargate, Pune", key="m2_custom_origin_input")
        else:
            route_origin = orig_choice

    with r_col2:
        st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#0F172A; margin-bottom:4px;'>Destination Landmark / Station</div>", unsafe_allow_html=True)
        dest_choice = st.selectbox(
            "Destination Landmark / Station",
            options=dropdown_options,
            index=dropdown_options.index("BopadiSquare_65") if "BopadiSquare_65" in dropdown_options else 1,
            key="m2_dest_station_select",
            label_visibility="collapsed"
        )
        if dest_choice == "Type Custom Landmark / Address...":
            route_dest = st.text_input("Type Destination Landmark", value="Viman Nagar, Pune", key="m2_custom_dest_input")
        else:
            route_dest = dest_choice

    r_col3, r_col4 = st.columns(2)
    with r_col3:
        route_mode = st.selectbox(
            "Transport Mode",
            ["Car", "Public Transport", "Motorcycle", "Cycling", "Walking"],
            index=0,
            key="m2_route_mode"
        )
    with r_col4:
        route_health = st.selectbox(
            "User Health Profile",
            ["General User", "Asthmatic / Respiratory", "Elderly", "Child / Sensitive"],
            index=1,
            key="m2_route_health"
        )

    calc_route_btn = st.button("Calculate Cumulative Route Exposure", type="primary", use_container_width=True)

    route_estimator = RoutePollutionEstimator(interpolator)
    route_analysis = route_estimator.estimate_exposure(
        origin=route_origin,
        destination=route_dest,
        transport_mode=route_mode,
        health_profile=route_health
    )

    # Advisory banner
    render_travel_advisory_card(
        advisory_text=route_analysis["advisory"],
        risk_level=route_analysis["route_a"]["risk_level"],
        risk_color=route_analysis["route_a"]["risk_color"],
        reduction_pct=route_analysis["reduction_pct"]
    )

    # Route Comparison Cards
    st.markdown("#### Route Comparison & Particulate Exposure Score")
    ra = route_analysis["route_a"]
    rb = route_analysis["route_b"]
    c_card_a, c_card_b = st.columns(2)

    with c_card_a:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #7F1D1D; border-top:3px solid #EF4444;
                            border-radius:8px; padding:16px 18px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <b style="font-size:0.95rem; color:#0F172A;">{ra['name']}</b>
                    <span style="background:rgba(239,68,68,0.15); border:1px solid #7F1D1D; color:#DC2626;
                                 font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:3px;">
                        {ra['risk_level']}
                    </span>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:8px;">
                    <div style="background:#F8FAFC; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                        <div style="font-size:0.70rem; color:#64748B;">Distance</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{ra['distance_km']} km</div>
                    </div>
                    <div style="background:#F8FAFC; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                        <div style="font-size:0.70rem; color:#64748B;">Est. Travel Time</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{ra['duration_mins']} min</div>
                    </div>
                    <div style="background:#FEF2F2; padding:8px; border-radius:5px; border:1px solid #FECACA;">
                        <div style="font-size:0.70rem; color:#991B1B;">Average AQI</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#DC2626;">{ra['avg_aqi']}</div>
                    </div>
                    <div style="background:#FEF2F2; padding:8px; border-radius:5px; border:1px solid #FECACA;">
                        <div style="font-size:0.70rem; color:#991B1B;">Exposure Score</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#DC2626;">{ra['exposure_score']} / 100</div>
                    </div>
                </div>
                <div style="font-size:0.75rem; color:#64748B;">
                    Passes through congested urban arteries. Peak segment: <b style="color:#DC2626;">{ra.get('max_aqi', ra.get('avg_aqi', 'N/A'))} AQI</b>.
                </div>
            </div>""",
            unsafe_allow_html=True
        )

    with c_card_b:
        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #14532D; border-top:3px solid #16A34A;
                            border-radius:8px; padding:16px 18px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <b style="font-size:0.95rem; color:#0F172A;">{rb['name']}</b>
                    <span style="background:rgba(22,163,74,0.15); border:1px solid #14532D; color:#16A34A;
                                 font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:3px;">
                        RECOMMENDED
                    </span>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:8px;">
                    <div style="background:#F8FAFC; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                        <div style="font-size:0.70rem; color:#64748B;">Distance</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{rb['distance_km']} km</div>
                    </div>
                    <div style="background:#F8FAFC; padding:8px; border-radius:5px; border:1px solid #E2E8F0;">
                        <div style="font-size:0.70rem; color:#64748B;">Est. Travel Time</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#0F172A;">{rb['duration_mins']} min</div>
                    </div>
                    <div style="background:#F0FDF4; padding:8px; border-radius:5px; border:1px solid #BBF7D0;">
                        <div style="font-size:0.70rem; color:#166534;">Average AQI</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#16A34A;">{rb['avg_aqi']}</div>
                    </div>
                    <div style="background:#F0FDF4; padding:8px; border-radius:5px; border:1px solid #BBF7D0;">
                        <div style="font-size:0.70rem; color:#166534;">Exposure Score</div>
                        <div style="font-size:1.15rem; font-weight:800; color:#16A34A;">{rb['exposure_score']} / 100</div>
                    </div>
                </div>
                <div style="font-size:0.75rem; color:#166534;">
                    <b style="color:#16A34A;">{route_analysis['reduction_pct']}% lower particulate inhalation</b> vs Route A.
                </div>
            </div>""",
            unsafe_allow_html=True
        )

    # Route Geospatial Map
    st.markdown("#### Geospatial Route & Pollution Hotspot Dispersion")
    st.caption("Displaying the optimized Best Route (solid green): lowest cumulative particulate exposure corridor. Red circles: localized high-pollution hotspots avoided.")
    render_route_map(route_analysis)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4: FastAPI Microservice & Model Retraining Pipeline (Items 4 & 5)
# ═════════════════════════════════════════════════════════════════════════════
with tab_fastapi_retrain:
    st.markdown("### 2.7  FastAPI Prediction Microservice & Continuous Retraining")
    st.caption(
        "Production-grade REST microservice exposing deep recurrent predictions, geostatistical interpolation, "
        "and automated weekly retraining triggers."
    )

    # Check FastAPI status
    import urllib.request
    api_online = False
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/health", headers={"User-Agent": "StreamlitClient"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.getcode() == 200:
                api_online = True
    except Exception:
        api_online = False

    st.markdown(
        f"""<div style="background:#FFFFFF; border:1px solid #334155; border-left:4px solid {'#10B981' if api_online else '#EF4444'};
                        padding:12px 18px; border-radius:6px; margin-bottom:18px; display:flex;
                        justify-content:space-between; align-items:center;">
            <div>
                <b style="color:#0F172A; font-size:0.95rem;">FastAPI Microservice Engine: {'ONLINE (PORT 8000)' if api_online else 'STANDBY'}</b>
                <div style="color:#64748B; font-size:0.78rem;">
                    REST Endpoints: /predict/forecast, /predict/interpolate, /route/exposure, /retrain, /stations
                </div>
            </div>
            <div>
                <a href="http://localhost:8000/docs" target="_blank"
                   style="background:#1D4ED8; color:white; font-size:0.78rem; font-weight:700;
                          padding:6px 14px; border-radius:4px; text-decoration:none;">
                    Open Swagger UI (/docs) ↗
                </a>
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    st.markdown("#### Live REST API Verification Tester")
    st.caption("Send real HTTP POST payloads to the live FastAPI server and inspect the JSON response in real-time.")

    test_c1, test_c2 = st.columns([1.5, 2.5])

    with test_c1:
        test_endpoint = st.selectbox(
            "Select API Endpoint to Query",
            [
                "POST /predict/forecast",
                "POST /predict/interpolate",
                "POST /route/exposure",
                "GET /health"
            ]
        )
        test_loc = st.selectbox("Target Station for Forecast", options=list(ALL_LOCATIONS.keys())[:5], index=0)
        send_api_req = st.button("Send Request to FastAPI", type="primary", use_container_width=True)

    with test_c2:
        if send_api_req:
            import urllib.request
            import json

            try:
                if "forecast" in test_endpoint:
                    url = "http://127.0.0.1:8000/predict/forecast"
                    payload = json.dumps({
                        "location_name": test_loc,
                        "architecture": "GRU",
                        "horizon_hours": 24
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                elif "interpolate" in test_endpoint:
                    url = "http://127.0.0.1:8000/predict/interpolate"
                    payload = json.dumps({
                        "latitude": 18.5204,
                        "longitude": 73.8567,
                        "method": "kriging"
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                elif "route" in test_endpoint:
                    url = "http://127.0.0.1:8000/route/exposure"
                    payload = json.dumps({
                        "origin": "Swargate, Pune",
                        "destination": "Viman Nagar, Pune",
                        "transport_mode": "Car",
                        "health_profile": "Asthmatic / Respiratory"
                    }).encode("utf-8")
                    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                else:
                    url = "http://127.0.0.1:8000/health"
                    req = urllib.request.Request(url)

                with urllib.request.urlopen(req, timeout=4) as response:
                    raw_body = response.read().decode("utf-8")
                    parsed_json = json.loads(raw_body)
                    st.success(f"HTTP {response.getcode()} OK — Payload Received from {url}")
                    st.json(parsed_json)

            except Exception as ex:
                st.error(f"API Request failed: {ex}")
        else:
            st.info("Click **'Send Request to FastAPI'** to execute a live query and view the response.")

    st.markdown("---")
    st.markdown("#### Weekly Model Retraining Execution")

    rc1, rc2 = st.columns([1.5, 1.0])
    with rc1:
        retrain_epochs = st.slider("Training Epochs for Next Batch", min_value=2, max_value=30, value=12)
        batch_notes = st.text_input("Batch Release Tag / Notes", value="Weekly Pune Sensor Ingestion — Batch #42")

        if st.button("Trigger Retraining Pipeline", use_container_width=True):
            with st.spinner("Executing data ingestion, feature normalization, and GRU network training..."):
                res = pipeline.run_weekly_retraining(epochs=retrain_epochs)

            if res.get("status") == "SUCCESS":
                st.success(f"Retraining successful in {res.get('duration_seconds')}s! New checkpoints registered.")
                st.rerun()
            else:
                st.error(f"Retraining encountered an issue: {res.get('message')}")

    with rc2:
        st.markdown(f"""
        **Active Production Checkpoint:**
        - **Model:** `aqi_gru.pt` (PyTorch GRU)
        - **Dataset:** `{meta.get('dataset_source', 'Pune_Dataset(processed).xlsx')}`
        - **Sequence Samples:** `{meta.get('total_samples', 2500)}`
        - **Features (10):** AQI, PM2.5, PM10, NO2, O3, CO, SO2, Temp, Humidity, Traffic
        """)
