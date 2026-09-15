import streamlit as st
from data.custom_dataset import load_pune_data
from data.demo_data import HEALTH_PROFILES

LOCATIONS_DATA = load_pune_data()

def render_sidebar():
    with st.sidebar:
        if st.button("Home Page", key="home_btn", use_container_width=True):
            st.switch_page("app.py")

        st.markdown(
            "<div style='font-size:0.70rem; font-weight:700; text-transform:uppercase; "
            "letter-spacing:1px; color:#334155; margin-bottom:8px;'>SESSION CONTEXT</div>",
            unsafe_allow_html=True
        )

        city_list = list(LOCATIONS_DATA.keys())
        if "selected_city" not in st.session_state or st.session_state.selected_city not in city_list:
            st.session_state.selected_city = city_list[0] if city_list else "BopadiSquare_65"
        
        cur_city = st.selectbox(
            "Active City / Station",
            options=city_list,
            index=city_list.index(st.session_state.selected_city)
                if st.session_state.selected_city in city_list else 0
        )
        st.session_state.selected_city = cur_city
        st.session_state.route_source = cur_city

        hp_list = list(HEALTH_PROFILES.keys())
        if "health_profile" not in st.session_state:
            st.session_state.health_profile = "General User"
            
        cur_hp = st.selectbox(
            "Health Profile",
            options=hp_list,
            index=hp_list.index(st.session_state.health_profile)
                if st.session_state.health_profile in hp_list else 0
        )
        st.session_state.health_profile = cur_hp

        st.markdown(
            "<div style='font-size:0.70rem; font-weight:700; text-transform:uppercase; "
            "letter-spacing:1px; color:#334155; margin:18px 0 8px 0;'>NAVIGATE TO MODULE</div>",
            unsafe_allow_html=True
        )

        if st.button("Module 1 — Location and Real-Time AQI",  use_container_width=True): st.switch_page("pages/1_Location_AQI_RealTime.py")
        if st.button("Module 2 — Predictive AQI Forecasting",  use_container_width=True): st.switch_page("pages/2_Predictive_AQI_Forecasting.py")
        if st.button("Module 3 — Route Advisory and Alerts",   use_container_width=True): st.switch_page("pages/3_Route_Advisory_Notifications.py")
        if st.button("Module 4 — System Integration Testing",  use_container_width=True): st.switch_page("pages/4_System_Integration_Testing.py")

        st.markdown(
            """
            <div style="margin-top:20px; background:#F8FAFC; padding:10px 12px; border-radius:6px;
                        border:1px solid #E2E8F0; font-size:0.75rem; color:#334155; text-align:center;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-weight: 500; letter-spacing: 0.3px;">
                Developed by <b>Harika.k</b>
            </div>
            """,
            unsafe_allow_html=True
        )
