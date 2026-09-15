"""
Metrics and Visual Indicator Components — Dark Theme
Professional dark metric cards, AQI banners, pollutant grids, weather panels.
"""

import streamlit as st
from data.demo_data import get_aqi_category_info

# ── Dark-theme color tokens ────────────────────────────────────────────────
BG_CARD   = "#FFFFFF"   # card surface
BG_INNER  = "#F8FAFC"   # nested / inset surface
BORDER    = "#334155"   # card border
TEXT_PRI  = "#0F172A"   # primary text
TEXT_SEC  = "#64748B"   # secondary / muted text
TEXT_DIM  = "#64748B"   # very muted


def render_demo_banner(module_label: str = ""):
    """Non-intrusive demo mode indicator — dark style."""
    pass


def render_hero_aqi_card(aqi_val: float, dominant_pollutant: str, last_updated: str, data_source: str):
    """Primary AQI display card — deep dark surface."""
    cat = get_aqi_category_info(aqi_val)

    # Darken category bg for dark theme
    dark_cat_bg = {
        "Good":           "#DCFCE7",
        "Satisfactory / Moderate": "#FEF9C3",
        "Unhealthy for Sensitive Groups": "#FFEDD5",
        "Unhealthy / Poor": "#FEE2E2",
        "Very Unhealthy / Very Poor": "#F3E8FF",
        "Hazardous / Severe": "#FFE4E6",
    }
    bg = dark_cat_bg.get(cat["label"], "#FFFFFF")

    st.markdown(
        f"""
        <div style="
            background: #F8FAFC;
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 24px 28px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        ">
            <div style="display: flex; justify-content: space-between;
                        align-items: flex-start; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="color: {TEXT_DIM}; font-size: 0.72rem; font-weight: 600;
                                text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px;">
                        Real-Time Air Quality Index
                    </div>
                    <div style="display: flex; align-items: baseline; gap: 16px;">
                        <span style="font-size: 3.2rem; font-weight: 800;
                                     line-height: 1; color: {cat['color']};">
                            {int(aqi_val)}
                        </span>
                        <div>
                            <span style="background: {bg}; color: {cat['color']};
                                  border: 1px solid {cat['color']}40;
                                  padding: 4px 12px; border-radius: 4px;
                                  font-weight: 700; font-size: 0.88rem; display: inline-block;">
                                {cat['label']}
                            </span>
                            <div style="color: {TEXT_SEC}; font-size: 0.80rem; margin-top: 5px;">
                                {cat['severity']}
                            </div>
                        </div>
                    </div>
                </div>
                <div style="background: #FFFFFF; padding: 14px 18px; border-radius: 8px;
                            border: 1px solid {BORDER}; min-width: 230px;">
                    <div style="display: flex; justify-content: space-between;
                                margin-bottom: 8px; font-size: 0.82rem;">
                        <span style="color: {TEXT_SEC};">Dominant Pollutant</span>
                        <span style="font-weight: 700; color: #0369A1;">{dominant_pollutant}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;
                                margin-bottom: 8px; font-size: 0.82rem;">
                        <span style="color: {TEXT_SEC};">Data Source</span>
                        <span style="font-weight: 600; color: {TEXT_PRI};">{data_source}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.80rem;">
                        <span style="color: {TEXT_SEC};">Last Synchronized</span>
                        <span style="color: #16A34A;">Active — {last_updated}</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_pollutant_cards(pm25: float, pm10: float, no2: float, o3: float, co: float, so2: float = 12.0):
    """Six-column pollutant telemetry grid — dark cards calibrated to CPCB NAAQS standards."""
    cols = st.columns(6)

    # CO in dataset is µg/m³; CPCB NAAQS standard is mg/m³ (safe 8h limit = 2.0 mg/m³)
    co_display = round(co / 1000.0, 2) if co > 20.0 else round(co, 2)

    pollutants = [
        {"name": "PM2.5", "val": round(pm25, 1), "unit": "µg/m³", "safe": 60.0,  "desc": "Fine Particulate"},
        {"name": "PM10",  "val": round(pm10, 1), "unit": "µg/m³", "safe": 100.0, "desc": "Coarse Dust"},
        {"name": "NO2",   "val": round(no2, 1),  "unit": "µg/m³", "safe": 80.0,  "desc": "Nitrogen Dioxide"},
        {"name": "O3",    "val": round(o3, 1),   "unit": "µg/m³", "safe": 100.0, "desc": "Ground Ozone"},
        {"name": "CO",    "val": co_display,     "unit": "mg/m³", "safe": 2.0,   "desc": "Carbon Monoxide"},
        {"name": "SO2",   "val": round(so2, 1),  "unit": "µg/m³", "safe": 80.0,  "desc": "Sulfur Dioxide"},
    ]

    for i, p in enumerate(pollutants):
        with cols[i]:
            is_elevated = p["val"] > p["safe"]
            val_col    = "#DC2626" if is_elevated else "#16A34A"
            border_col = "#FECACA" if is_elevated else "#BBF7D0"
            bg         = "#FEF2F2" if is_elevated else "#F0FDF4"
            status_txt = "Above Limit" if is_elevated else "Within Limit"

            st.markdown(
                f"""
                <div style="
                    background: {bg};
                    border: 1px solid {border_col};
                    border-radius: 8px;
                    padding: 12px 10px;
                    text-align: center;
                ">
                    <div style="font-size: 0.72rem; font-weight: 700; color: {TEXT_SEC};
                                text-transform: uppercase; letter-spacing: 0.8px;">
                        {p['name']}
                    </div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: {val_col};
                                margin: 4px 0;">
                        {p['val']}
                    </div>
                    <div style="font-size: 0.68rem; color: {TEXT_DIM};">{p['unit']}</div>
                    <div style="font-size: 0.68rem; font-weight: 600; color: {val_col};
                                margin-top: 4px;">
                        {status_txt}
                    </div>
                    <div style="font-size: 0.62rem; color: {TEXT_DIM}; margin-top: 2px;">
                        Limit: {p['safe']} {p['unit']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_weather_cards(temp: float, humidity: float, wind_speed: float, wind_deg: str, weather_desc: str):
    """Four meteorological parameter cards — dark theme."""
    cols = st.columns(4)

    items = [
        {"title": "Temperature",       "value": f"{temp} C",          "sub": "Ambient (Celsius)"},
        {"title": "Relative Humidity", "value": f"{humidity}%",       "sub": "Moisture Ratio"},
        {"title": "Wind Speed",        "value": f"{wind_speed} km/h", "sub": wind_deg},
        {"title": "Atmospheric State", "value": weather_desc,         "sub": "Surface Conditions"},
    ]

    for i, item in enumerate(items):
        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    padding: 14px 16px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                ">
                    <div style="font-size: 0.72rem; font-weight: 600; color: {TEXT_DIM};
                                text-transform: uppercase; letter-spacing: 0.8px;">
                        {item['title']}
                    </div>
                    <div style="font-size: 1.35rem; font-weight: 700; color: {TEXT_PRI};
                                margin: 6px 0 2px 0;">
                        {item['value']}
                    </div>
                    <div style="font-size: 0.75rem; color: {TEXT_SEC};">{item['sub']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
