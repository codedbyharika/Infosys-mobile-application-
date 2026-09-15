"""
Interactive Map Components — Dark Tile Theme
Folium maps using CartoDB dark_matter tiles.
"""

import folium
from streamlit_folium import st_folium
import streamlit as st
from data.demo_data import get_aqi_category_info


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Return great-circle distance in km between two lat/lon points."""
    import math
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def render_pollution_map(
    city_data: dict,
    stations_list: list,
    source_data: dict | None = None,
    destination_data: dict | None = None,
    source_name: str = "Source",
    destination_name: str = "Destination",
    route_info: dict | None = None,
):
    """
    Interactive OSM map showing AQI monitoring stations.
    When source_data and destination_data are provided, also draws:
      - Green Source pin
      - Red Destination flag
      - Severity color-coded PolyLine reflecting Composite Route AQI
      - Intermediate corridor monitoring waypoints (if present)
    Map bounds auto-fit to encompass both endpoints.
    """
    has_route = (
        source_data is not None and destination_data is not None
        and source_data != destination_data
    )

    # Determine map centre and zoom
    if has_route:
        center_lat = (source_data["lat"] + destination_data["lat"]) / 2
        center_lon = (source_data["lon"] + destination_data["lon"]) / 2
    else:
        center_lat = city_data["lat"]
        center_lon = city_data["lon"]

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="OpenStreetMap"
    )

    # ── Route line and endpoint pins ─────────────────────────────────────────
    if has_route:
        src_lat, src_lon = source_data["lat"], source_data["lon"]
        dst_lat, dst_lon = destination_data["lat"], destination_data["lon"]
        dist_km = _haversine_km(src_lat, src_lon, dst_lat, dst_lon)

        line_color = route_info.get("color", "#3B82F6") if route_info else "#3B82F6"
        if route_info:
            line_tooltip = (
                f"Corridor Route AQI: {route_info['route_aqi']} ({route_info['category']})  |  "
                f"Length: {dist_km:.1f} km  |  "
                f"Base AQI: {route_info['base_aqi']}  |  "
                f"Traffic: +{route_info['traffic_penalty_pct']}%  |  "
                f"Weather: {route_info['weather_impact_pct']:+.1f}%"
            )
        else:
            line_tooltip = (
                f"Route: {source_name} → {destination_name}  |  "
                f"Straight-line distance: {dist_km:.1f} km  |  "
                f"Source AQI: {int(source_data['aqi'])}  →  "
                f"Destination AQI: {int(destination_data['aqi'])}"
            )

        # Straight-line route polyline (colored by composite Route AQI)
        folium.PolyLine(
            locations=[[src_lat, src_lon], [dst_lat, dst_lon]],
            color=line_color,
            weight=6,
            opacity=0.90,
            dash_array="10 5",
            tooltip=line_tooltip
        ).add_to(m)

        # Intermediate corridor waypoints (if any detected)
        if route_info and route_info.get("intermediate_stations"):
            for inter in route_info["intermediate_stations"]:
                folium.CircleMarker(
                    location=[inter["lat"], inter["lon"]],
                    radius=8,
                    color="#F59E0B",
                    fill=True,
                    fill_color="#F59E0B",
                    fill_opacity=0.85,
                    weight=2,
                    tooltip=f"Corridor Waypoint: {inter['name']} (AQI {int(inter['aqi'])}) — {inter['dist_from_path_km']} km off route",
                    popup=folium.Popup(
                        f"<b>Corridor Waypoint:</b> {inter['name']}<br>"
                        f"Station AQI: <b>{int(inter['aqi'])}</b><br>"
                        f"Corridor Offset: {inter['dist_from_path_km']} km",
                        max_width=200
                    )
                ).add_to(m)

        # Source marker (green)
        src_cat = get_aqi_category_info(source_data["aqi"])
        folium.Marker(
            location=[src_lat, src_lon],
            popup=folium.Popup(
                f"""<div style="font-family:Arial,sans-serif; font-size:12px; min-width:160px;">
                    <b style="color:#16A34A;">🟢 SOURCE</b><br>
                    <b>{source_name}</b><br>
                    AQI: <b style="color:{src_cat['color']};">{int(source_data['aqi'])} — {src_cat['label']}</b><br>
                    Lat: {src_lat:.4f} N &nbsp; Lon: {src_lon:.4f} E
                </div>""",
                max_width=240
            ),
            tooltip=f"SOURCE: {source_name} (AQI {int(source_data['aqi'])})",
            icon=folium.Icon(color="green", icon="play", prefix="glyphicon")
        ).add_to(m)

        # Destination marker (red)
        dst_cat = get_aqi_category_info(destination_data["aqi"])
        folium.Marker(
            location=[dst_lat, dst_lon],
            popup=folium.Popup(
                f"""<div style="font-family:Arial,sans-serif; font-size:12px; min-width:160px;">
                    <b style="color:#DC2626;">🔴 DESTINATION</b><br>
                    <b>{destination_name}</b><br>
                    AQI: <b style="color:{dst_cat['color']};">{int(destination_data['aqi'])} — {dst_cat['label']}</b><br>
                    Lat: {dst_lat:.4f} N &nbsp; Lon: {dst_lon:.4f} E
                </div>""",
                max_width=240
            ),
            tooltip=f"DESTINATION: {destination_name} (AQI {int(destination_data['aqi'])})",
            icon=folium.Icon(color="red", icon="flag", prefix="glyphicon")
        ).add_to(m)

        # Auto-fit bounds to both endpoints
        m.fit_bounds([[src_lat, src_lon], [dst_lat, dst_lon]], padding=(40, 40))

    else:
        # Fallback: single city centre marker
        folium.Marker(
            location=[city_data["lat"], city_data["lon"]],
            popup=f"<b>{city_data.get('city', 'City')} — Reference Point</b><br>Regional AQI: {city_data['aqi']}",
            tooltip=f"{city_data.get('city', 'City')} Center (AQI {city_data['aqi']})",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # ── AQI station circle markers (always shown) ─────────────────────────────
    for stn in stations_list:
        stn_aqi = stn["aqi"]
        cat = get_aqi_category_info(stn_aqi)

        folium_color = "green"
        if stn_aqi > 50:  folium_color = "orange"
        if stn_aqi > 100: folium_color = "red"
        if stn_aqi > 200: folium_color = "purple"
        if stn_aqi > 300: folium_color = "darkred"

        popup_html = f"""
        <div style="font-family:Arial,sans-serif; min-width:170px; font-size:12px;
                    background:#FFFFFF; color:#0F172A; padding:8px; border-radius:4px;">
            <b style="font-size:13px; color:#000000;">{stn['name']}</b><br>
            <div style="margin:6px 0; padding:4px 8px; background:{cat['color']}22;
                        color:{cat['color']}; border-radius:3px; font-weight:bold; text-align:center;
                        border:1px solid {cat['color']}66;">
                AQI: {stn_aqi} — {cat['label']}
            </div>
            Status: <b style="color:#16A34A;">{stn.get('status', 'Active')}</b><br>
            <span style="color:#64748B; font-size:11px;">CPCB / WAQI Continuous Feed</span>
        </div>
        """

        folium.CircleMarker(
            location=[stn["lat"], stn["lon"]],
            radius=11,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{stn['name']} — AQI {stn_aqi}",
            color=cat["color"],
            fill=True,
            fill_color=cat["color"],
            fill_opacity=0.80,
            weight=2
        ).add_to(m)

        folium.Circle(
            location=[stn["lat"], stn["lon"]],
            radius=900,
            color=cat["color"],
            fill=True,
            fill_color=cat["color"],
            fill_opacity=0.12,
            weight=1
        ).add_to(m)

    st_folium(m, use_container_width=True, height=420, returned_objects=[])


def render_route_map(route_analysis: dict, *args, **kwargs):
    """
    Renders route map on standard OSM tile background.
    Finds the optimal route with lowest cumulative exposure score and renders only that route for the user.
    """
    only_best_route = kwargs.get("only_best_route", True) if kwargs else (args[0] if args else True)
    route_a = route_analysis.get("route_a", {})
    route_b = route_analysis.get("route_b", {})
    hotspots = route_analysis.get("hotspots", [])
    if not hotspots and "hotspots" in route_a:
        hotspots = route_a.get("hotspots", [])

    def _extract_coord(pt):
        if isinstance(pt, dict):
            return [pt["lat"], pt["lon"]]
        return [pt[0], pt[1]]

    raw_a = route_a.get("waypoints", [])
    raw_b = route_b.get("waypoints", [])
    if not raw_a and not raw_b:
        st.warning("No waypoints available to render.")
        return

    coords_a = [_extract_coord(pt) for pt in raw_a] if raw_a else []
    coords_b = [_extract_coord(pt) for pt in raw_b] if raw_b else []

    # Identify the best route by lowest exposure score; fallback to lowest avg AQI
    score_a = route_a.get("exposure_score", 999.0)
    score_b = route_b.get("exposure_score", 999.0)

    if coords_b and (score_b < score_a or (score_b == score_a and route_b.get("avg_aqi", 999) <= route_a.get("avg_aqi", 999))):
        best_route = route_b
        best_coords = coords_b
        best_tag = "RECOMMENDED BEST ROUTE"
        is_clean_corridor = True
    elif coords_a:
        best_route = route_a
        best_coords = coords_a
        best_tag = "BEST AVAILABLE ROUTE"
        is_clean_corridor = False
    elif coords_b:
        best_route = route_b
        best_coords = coords_b
        best_tag = "RECOMMENDED BEST ROUTE"
        is_clean_corridor = True
    else:
        st.warning("No valid route coordinates available to render.")
        return

    start_pt = best_coords[0]
    end_pt   = best_coords[-1]
    mid_lat  = (start_pt[0] + end_pt[0]) / 2.0
    mid_lon  = (start_pt[1] + end_pt[1]) / 2.0

    m = folium.Map(
        location=[mid_lat, mid_lon],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    src_name = route_analysis.get("origin", route_analysis.get("source", "Origin"))
    dst_name = route_analysis.get("destination", "Destination")

    # Origin marker (Green)
    folium.Marker(
        location=start_pt,
        popup=folium.Popup(
            f"""<div style="font-family:Arial,sans-serif; font-size:12px; min-width:150px;">
                <b style="color:#16A34A;">🟢 ORIGIN</b><br>
                <b>{src_name}</b><br>
                Lat: {start_pt[0]:.4f} N &nbsp; Lon: {start_pt[1]:.4f} E
            </div>""",
            max_width=220
        ),
        tooltip=f"Origin: {src_name}",
        icon=folium.Icon(color="green", icon="play", prefix="glyphicon")
    ).add_to(m)

    # Destination marker (Red)
    folium.Marker(
        location=end_pt,
        popup=folium.Popup(
            f"""<div style="font-family:Arial,sans-serif; font-size:12px; min-width:150px;">
                <b style="color:#DC2626;">🔴 DESTINATION</b><br>
                <b>{dst_name}</b><br>
                Lat: {end_pt[0]:.4f} N &nbsp; Lon: {end_pt[1]:.4f} E
            </div>""",
            max_width=220
        ),
        tooltip=f"Destination: {dst_name}",
        icon=folium.Icon(color="red", icon="flag", prefix="glyphicon")
    ).add_to(m)

    if only_best_route:
        # Render ONLY the best route
        route_color = "#16A34A" if is_clean_corridor else best_route.get("risk_color", "#2563EB")
        route_name = best_route.get("name", "Best Route")
        dist_km = best_route.get("distance_km", "")
        dur_mins = best_route.get("duration_mins", "")
        avg_aqi = best_route.get("avg_aqi", "")
        exposure_score = best_route.get("exposure_score", "")

        tooltip_text = (
            f"★ {best_tag}: {route_name} | "
            f"Distance: {dist_km} km | "
            f"Duration: {dur_mins} min | "
            f"Avg AQI: {avg_aqi} | "
            f"Exposure Score: {exposure_score}/100"
        )

        folium.PolyLine(
            locations=best_coords,
            color=route_color,
            weight=7,
            opacity=0.95,
            tooltip=tooltip_text
        ).add_to(m)

        # Waypoint nodes along the best route
        wp_details = best_route.get("waypoint_details", [])
        if wp_details:
            for i, wp in enumerate(wp_details):
                if i % 3 == 0 and 0 < i < len(wp_details) - 1:
                    wp_lat = wp.get("lat")
                    wp_lon = wp.get("lon")
                    wp_aqi = wp.get("aqi", "N/A")
                    if wp_lat is not None and wp_lon is not None:
                        folium.CircleMarker(
                            location=[wp_lat, wp_lon],
                            radius=5,
                            color=route_color,
                            fill=True,
                            fill_color="#FFFFFF",
                            fill_opacity=0.95,
                            weight=2,
                            tooltip=f"Waypoint {i+1}: AQI {wp_aqi}"
                        ).add_to(m)

    else:
        # Comparative view showing both routes
        if coords_a:
            folium.PolyLine(
                locations=coords_a,
                color="#EF4444", weight=6, opacity=0.90,
                tooltip=f"Route A — {route_a.get('distance_km', '')} km | Avg AQI {route_a.get('avg_aqi', '')} (High Exposure)"
            ).add_to(m)

        if coords_b:
            folium.PolyLine(
                locations=coords_b,
                color="#22C55E", weight=7, opacity=0.95, dash_array="8 5",
                tooltip=f"Route B [RECOMMENDED] — {route_b.get('distance_km', '')} km | Avg AQI {route_b.get('avg_aqi', '')}"
            ).add_to(m)

    # Avoided high-pollution hotspots overlay
    for spot in hotspots:
        spot_name = spot.get("name", spot.get("description", "High Pollution Hotspot"))
        s_lat = spot.get("lat")
        s_lon = spot.get("lon")
        if s_lat is not None and s_lon is not None:
            folium.Circle(
                location=[s_lat, s_lon],
                radius=spot.get("radius", 600),
                color="#EF4444", fill=True, fill_color="#DC2626",
                fill_opacity=0.25, weight=1,
                popup=f"<b>Hotspot Avoided:</b><br>{spot_name}<br>Localized AQI: {spot.get('aqi', '')}",
                tooltip=f"Avoided Hotspot: {spot_name} — AQI {spot.get('aqi', '')}"
            ).add_to(m)

    # Fit bounds dynamically to enclose the best route
    m.fit_bounds(best_coords, padding=(35, 35))

    st.markdown(
        f"""<div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A;
                        padding:8px 14px; border-radius:5px; margin-bottom:10px; font-size:0.82rem; color:#166534;">
            <b>Displaying Optimal Best Route:</b> {best_route.get('name', 'Recommended Route')} &nbsp;|&nbsp;
            Exposure Score: <b>{best_route.get('exposure_score', '')} / 100</b> &nbsp;|&nbsp;
            Avg AQI: <b>{best_route.get('avg_aqi', '')}</b> &nbsp;|&nbsp;
            Distance: <b>{best_route.get('distance_km', '')} km</b> ({best_route.get('duration_mins', '')} mins)
        </div>""",
        unsafe_allow_html=True
    )

    st_folium(m, use_container_width=True, height=440, returned_objects=[])

