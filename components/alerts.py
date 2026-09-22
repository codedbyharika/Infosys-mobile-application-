"""
Alert, Health Advisory, and Notification Center Components — Dark Theme
Personalized health guidance, travel advisories, and push notification feed.
"""

import streamlit as st
from data.custom_dataset import HEALTH_PROFILES, get_aqi_category_info

BG_CARD  = "#FFFFFF"
BORDER   = "#334155"
TEXT_PRI = "#0F172A"
TEXT_SEC = "#1E293B"
TEXT_DIM = "#334155"


def render_travel_advisory_card(advisory_text: str, risk_level: str, risk_color: str, reduction_pct: int):
    """Structured travel advisory container — dark surface."""
    st.markdown(
        f"""
        <div style="
            background: #F0FDF4;
            border-left: 5px solid #22C55E;
            border: 1px solid #BBF7D0;
            border-radius: 10px;
            padding: 20px 24px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            margin: 16px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;
                        margin-bottom: 10px; flex-wrap: wrap; gap: 10px;">
                <div style="font-weight: 700; font-size: 0.95rem; letter-spacing: 0.4px;
                            color: #16A34A;">
                    SMART TRAVEL ADVISORY
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: {risk_color}22; border:1px solid {risk_color}66;
                          color: {risk_color}; padding: 3px 12px; border-radius: 3px;
                          font-weight: 700; font-size: 0.75rem;">
                        {risk_level}
                    </span>
                    <span style="background: rgba(34,197,94,0.15); border: 1px solid #22C55E;
                          color: #16A34A; padding: 3px 12px; border-radius: 3px;
                          font-weight: 700; font-size: 0.75rem;">
                        Route B: {reduction_pct}% Lower Exposure
                    </span>
                </div>
            </div>
            <p style="font-size: 0.88rem; line-height: 1.65; color: {TEXT_SEC}; margin: 0;">
                {advisory_text}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_health_profile_card(profile_name: str, aqi_val: float):
    """Profile-sensitive health guidance card — dark theme."""
    prof = HEALTH_PROFILES.get(profile_name, HEALTH_PROFILES["General User"])
    needs_action = aqi_val > prof["recommended_threshold"]

    border  = "#FECACA" if needs_action else "#BBF7D0"
    bg      = "#FEF2F2" if needs_action else "#F0FDF4"
    badge_c = "#DC2626" if needs_action else "#16A34A"
    badge_b = "rgba(220,38,38,0.12)" if needs_action else "rgba(22,163,74,0.12)"
    badge_t = "Action Recommended" if needs_action else "Within Safe Range"
    txt_col = "#DC2626" if needs_action else "#16A34A"

    st.markdown(
        f"""
        <div style="background:{bg}; border:1px solid {border}; border-radius:8px;
                    padding:16px 20px; margin-top:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;
                        margin-bottom:8px;">
                <div style="font-weight:700; font-size:0.9rem; color:{TEXT_PRI};">
                    {profile_name} — Health Guidance
                </div>
                <span style="background:{badge_b}; border:1px solid {badge_c}40;
                      color:{badge_c}; padding:3px 10px; border-radius:3px;
                      font-weight:700; font-size:0.72rem;">
                    {badge_t}
                </span>
            </div>
            <p style="font-size:0.85rem; color:{TEXT_SEC}; margin:0 0 10px 0; line-height:1.5;">
                {prof['guidance']}
            </p>
            <div style="display:flex; gap:24px; font-size:0.75rem; color:{TEXT_DIM};
                        border-top:1px solid {BORDER}; padding-top:8px; flex-wrap:wrap;">
                <span>Alert Threshold: <b style="color:{txt_col};">{prof['recommended_threshold']} AQI</b></span>
                <span>Mask Advisory: <b style="color:{txt_col};">{prof['mask_advisory_threshold']} AQI</b></span>
                <span>Exercise Limit: <b style="color:{txt_col};">{prof['outdoor_exercise_limit']} AQI</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_notification_center(notifications: list):
    """Push notification log feed — dark theme."""
    st.subheader("Push Notification Center — Pune Alert Feed")
    st.caption(
        "Proactive notifications triggered when monitored thresholds or route risk levels are breached. "
        "Generated directly from Pune urban monitoring station telemetry."
    )

    severity_cfg = {
        "Hazardous":  {"border": "#EF4444", "bg": "#FEE2E2", "badge_bg": "rgba(239,68,68,0.15)",  "badge_c": "#DC2626"},
        "Advisory":   {"border": "#3B82F6", "bg": "#EFF6FF", "badge_bg": "rgba(59,130,246,0.15)", "badge_c": "#2563EB"},
        "Prediction": {"border": "#8B5CF6", "bg": "#F3E8FF", "badge_bg": "rgba(139,92,246,0.15)", "badge_c": "#7C3AED"},
        "Health":     {"border": "#F59E0B", "bg": "#FEF3C7", "badge_bg": "rgba(245,158,11,0.15)", "badge_c": "#D97706"},
    }

    for n in notifications:
        cfg = severity_cfg.get(n["severity"], severity_cfg["Advisory"])
        st.markdown(
            f"""
            <div style="
                background: {cfg['bg']};
                border-left: 4px solid {cfg['border']};
                border: 1px solid {cfg['border']}44;
                border-radius: 6px;
                padding: 12px 16px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 12px;
            ">
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:0.88rem; color:{TEXT_PRI}; margin-bottom:4px;">
                        {n['title']}
                    </div>
                    <div style="font-size:0.81rem; color:{TEXT_SEC}; line-height:1.45;">
                        {n['message']}
                    </div>
                </div>
                <div style="text-align:right; min-width:100px; flex-shrink:0;">
                    <div style="font-size:0.75rem; font-weight:600; color:{TEXT_DIM};">{n['time']}</div>
                    <span style="font-size:0.66rem; font-weight:700; background:{cfg['badge_bg']};
                          color:{cfg['badge_c']}; padding:2px 7px; border-radius:3px;
                          display:inline-block; margin-top:3px; text-transform:uppercase;">
                        {n['severity']}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
