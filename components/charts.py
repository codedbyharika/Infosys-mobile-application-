"""
Chart Components — Dark Theme Plotly Visualizations
All charts use plotly_white template with custom dark background colors.
Fixes: add_vline uses ISO string to avoid Plotly 6 + pandas Timestamp arithmetic issue.
"""

import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import streamlit as st

# ── Custom dark template ────────────────────────────────────────────────────
DARK_LAYOUT = dict(
    paper_bgcolor="#F8FAFC",
    plot_bgcolor="#F8FAFC",
    font=dict(family="Inter, sans-serif", size=11, color="#64748B"),
    xaxis=dict(
        gridcolor="#334155",
        linecolor="#334155",
        tickcolor="#64748B",
        zerolinecolor="#334155",
    ),
    yaxis=dict(
        gridcolor="#334155",
        linecolor="#334155",
        tickcolor="#64748B",
        zerolinecolor="#334155",
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#E2E8F0",
        borderwidth=1,
        font=dict(color="#334155"),
    ),
    margin=dict(l=40, r=20, t=60, b=40),
)


def _dark_fig(**kwargs) -> go.Figure:
    """Creates a new Figure with dark base layout applied."""
    fig = go.Figure(**kwargs)
    fig.update_layout(**DARK_LAYOUT)
    return fig


def render_aqi_forecast_chart(hist_df: pd.DataFrame, forecast_df: pd.DataFrame, horizon_hours: int = 12):
    """
    Dual-phase interactive chart (dark):
    - Historical AQI — solid blue line
    - Predicted AQI — dashed indigo line
    - 95% CI ribbon
    - AQI severity zone background bands
    """
    fig = _dark_fig()

    # AQI severity background bands — darker semi-transparent fills
    severity_bands = [
        (0,   50,  "rgba(22,163,74,0.08)",   "Good (0–50)"),
        (50,  100, "rgba(202,138,4,0.08)",   "Moderate (51–100)"),
        (100, 200, "rgba(220,38,38,0.08)",   "Unhealthy (101–200)"),
        (200, 500, "rgba(124,58,237,0.07)",  "Very Poor / Hazardous (201+)"),
    ]
    for y0, y1, color, label in severity_bands:
        fig.add_hrect(
            y0=y0, y1=y1,
            fillcolor=color, opacity=1, line_width=0,
            annotation_text=label, annotation_position="top left",
            annotation_font_size=9, annotation_font_color="#64748B"
        )

    # Confidence interval ribbon
    fig.add_trace(go.Scatter(
        x=forecast_df["timestamp"], y=forecast_df["upper_bound"],
        mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["timestamp"], y=forecast_df["lower_bound"],
        mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor="rgba(99,102,241,0.18)",
        showlegend=True, name="95% Confidence Interval", hoverinfo="skip"
    ))

    # Historical line
    fig.add_trace(go.Scatter(
        x=hist_df["timestamp"], y=hist_df["aqi"],
        mode="lines+markers", name="Historical Observed AQI",
        line=dict(color="#0369A1", width=2.5),
        marker=dict(size=4, color="#0EA5E9"),
        hovertemplate="<b>Observed:</b> %{y:.0f} AQI<br><b>Time:</b> %{x|%d %b %H:%M}<extra></extra>"
    ))

    # Connector
    fig.add_trace(go.Scatter(
        x=[hist_df["timestamp"].iloc[-1], forecast_df["timestamp"].iloc[0]],
        y=[hist_df["aqi"].iloc[-1], forecast_df["aqi"].iloc[0]],
        mode="lines", line=dict(color="#818CF8", width=2, dash="dot"),
        showlegend=False, hoverinfo="skip"
    ))

    # Forecast line
    fig.add_trace(go.Scatter(
        x=forecast_df["timestamp"], y=forecast_df["aqi"],
        mode="lines+markers",
        name=f"Predicted AQI — {horizon_hours}h Horizon",
        line=dict(color="#818CF8", width=3, dash="dash"),
        marker=dict(size=6, color="#6366F1", symbol="diamond"),
        hovertemplate=(
            "<b>Predicted:</b> %{y:.0f} AQI<br>"
            "<b>Time:</b> %{x|%d %b %H:%M}<br>"
            "<b>95% CI:</b> [%{customdata[0]:.0f} — %{customdata[1]:.0f}]"
            "<extra></extra>"
        ),
        customdata=forecast_df[["lower_bound", "upper_bound"]]
    ))

    # Vertical "Now" line — ISO string to avoid Plotly 6 + Timestamp bug
    now_iso = hist_df["timestamp"].iloc[-1].isoformat()
    fig.add_shape(
        type="line", x0=now_iso, x1=now_iso, y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color="#64748B", width=1.5, dash="dot")
    )
    fig.add_annotation(
        x=now_iso, y=1, xref="x", yref="paper",
        text="Current — Forecast Start", showarrow=False, yanchor="bottom",
        font=dict(size=10, color="#64748B"),
        bgcolor="#FFFFFF", bordercolor="#334155", borderwidth=1, borderpad=4
    )

    fig.update_layout(
        title=dict(
            text=f"<b>24-Hour Historical AQI & {horizon_hours}-Hour Predictive Forecast</b>",
            font=dict(size=14, color="#0F172A")
        ),
        xaxis_title="Time",
        yaxis_title="Air Quality Index (AQI)",
        hovermode="x unified",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_pollutant_forecast_chart(forecast_df: pd.DataFrame):
    """Multi-line pollutant concentration forecast — dark."""
    fig = _dark_fig()

    traces = [
        ("PM2.5", "pm25", "#F87171"),
        ("PM10",  "pm10", "#FBBF24"),
        ("NO2",   "no2",  "#60A5FA"),
    ]
    for label, col, color in traces:
        fig.add_trace(go.Scatter(
            x=forecast_df["timestamp"], y=forecast_df[col],
            name=label,
            line=dict(color=color, width=2),
            mode="lines+markers",
            marker=dict(size=4)
        ))

    fig.update_layout(
        title=dict(text="<b>Pollutant Concentration Forecast</b>",
                   font=dict(size=13, color="#0F172A")),
        xaxis_title="Forecast Horizon",
        yaxis_title="Concentration",
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
        height=300,
        margin=dict(l=30, r=20, t=50, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_traffic_aqi_correlation_chart(traffic_data: dict, location_data: dict):
    """
    Grouped bar chart showing pollutant concentrations at the current traffic
    congestion level versus the baseline (emission_multiplier = 1.0).
    Illustrates how vehicular congestion amplifies local pollutant loading.
    """
    multiplier = max(float(traffic_data.get("emission_multiplier", 1.0)), 0.1)
    congestion = traffic_data.get("congestion_level", "Unknown")
    level_color = traffic_data.get("level_color", "#64748B")

    pollutants = ["PM2.5", "PM10", "NO2", "O3", "CO", "SO2"]
    baseline   = [
        location_data.get("pm25", 0) / multiplier,
        location_data.get("pm10", 0) / multiplier,
        location_data.get("no2",  0) / multiplier,
        location_data.get("o3",   0) / multiplier,
        location_data.get("co",   0) / multiplier,
        location_data.get("so2",  0) / multiplier,
    ]
    current = [
        location_data.get("pm25", 0),
        location_data.get("pm10", 0),
        location_data.get("no2",  0),
        location_data.get("o3",   0),
        location_data.get("co",   0),
        location_data.get("so2",  0),
    ]

    fig = _dark_fig()

    fig.add_trace(go.Bar(
        name="Baseline (Free-Flow Traffic)",
        x=pollutants,
        y=[round(v, 2) for v in baseline],
        marker_color="#60A5FA",
        marker_line=dict(color="rgba(0,0,0,0.15)", width=0.5),
        hovertemplate="<b>%{x}</b> — Baseline: %{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name=f"Current ({congestion} Congestion  ×{multiplier})",
        x=pollutants,
        y=[round(v, 2) for v in current],
        marker_color=level_color,
        marker_line=dict(color="rgba(0,0,0,0.15)", width=0.5),
        hovertemplate="<b>%{x}</b> — Current: %{y:.2f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="<b>Traffic Emission Impact — Pollutant Concentration vs Congestion Level</b>",
            font=dict(size=13, color="#0F172A")
        ),
        barmode="group",
        xaxis_title="Pollutant",
        yaxis_title="Concentration",
        legend=dict(orientation="h", y=1.10, x=0.5, xanchor="center"),
        height=320,
        margin=dict(l=30, r=20, t=60, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_station_comparison_barchart(stations_list: list):
    """Horizontal bar chart — dark theme with severity-coded bars."""
    if not stations_list:
        st.info("No monitoring station data available for this location.")
        return

    df = pd.DataFrame(stations_list)
    if "aqi" not in df.columns or df.empty:
        st.info("Station AQI data unavailable.")
        return

    colors = []
    for val in df["aqi"]:
        if val <= 50:
            colors.append("#16A34A")
        elif val <= 100:
            colors.append("#FBBF24")
        elif val <= 200:
            colors.append("#F87171")
        else:
            colors.append("#C084FC")

    fig = _dark_fig()
    fig.add_trace(go.Bar(
        x=df["aqi"], y=df["name"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.2)", width=0.5)),
        text=df["aqi"].astype(str),
        textposition="outside",
        textfont=dict(color="#334155")
    ))

    fig.update_layout(
        title=dict(text="<b>Monitoring Station AQI Readings</b>",
                   font=dict(size=13, color="#0F172A")),
        xaxis_title="AQI",
        yaxis_title=None,
        height=260,
        margin=dict(l=10, r=50, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
