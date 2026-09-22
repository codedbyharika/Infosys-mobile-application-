"""
Interactive Map Components — Dark Tile Theme
Folium maps using CartoDB dark_matter tiles.
"""

import folium
from streamlit_folium import st_folium
import streamlit as st
from data.custom_dataset import get_aqi_category_info


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
            <span style="color:#0F172A; font-size:11px;">CPCB / WAQI Continuous Feed</span>
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
    Renders route map on standard OSM tile background displaying 3 routes for the selected
    source to destination:
    - Route 3 / Recommended Route in Green (#16A34A)
    - Route 1 / Direct Arterial Route in Red (#DC2626)
    - Route 2 / Alternative Corridor in Blue (#2563EB)
    Along with origin/destination pins, localized waypoints, and avoided pollution hotspots.
    """
    route_a = route_analysis.get("route_a", {})
    route_b = route_analysis.get("route_b", {})
    route_c = route_analysis.get("route_c") or route_analysis.get("recommended_route", {})
    hotspots = route_analysis.get("hotspots", [])
    if not hotspots and "hotspots" in route_a:
        hotspots = route_a.get("hotspots", [])

    def _extract_coord(pt):
        if isinstance(pt, dict):
            return [pt["lat"], pt["lon"]]
        return [pt[0], pt[1]]

    raw_a = route_a.get("waypoints", [])
    raw_b = route_b.get("waypoints", [])
    raw_c = route_c.get("waypoints", []) if route_c else []

    if not raw_a and not raw_b and not raw_c:
        st.warning("No waypoints available to render.")
        return

    coords_a = [_extract_coord(pt) for pt in raw_a] if raw_a else []
    coords_b = [_extract_coord(pt) for pt in raw_b] if raw_b else []
    coords_c = [_extract_coord(pt) for pt in raw_c] if raw_c else []

    # If route_c is missing, designate the route with lower exposure score as recommended
    if not coords_c:
        score_a = route_a.get("exposure_score", 999.0)
        score_b = route_b.get("exposure_score", 999.0)
        if score_b <= score_a and coords_b:
            route_c = route_b
            coords_c = coords_b
        elif coords_a:
            route_c = route_a
            coords_c = coords_a

    # Determine reference center and start/end coordinates
    ref_coords = coords_c or coords_a or coords_b
    if not ref_coords:
        st.warning("No valid route coordinates available to render.")
        return

    start_pt = ref_coords[0]
    end_pt   = ref_coords[-1]
    mid_lat  = (start_pt[0] + end_pt[0]) / 2.0
    mid_lon  = (start_pt[1] + end_pt[1]) / 2.0

    m = folium.Map(
        location=[mid_lat, mid_lon],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    src_name = route_analysis.get("origin", route_analysis.get("source", "Origin"))
    dst_name = route_analysis.get("destination", "Destination")

    # 1. Origin marker (Green)
    folium.Marker(
        location=start_pt,
        popup=folium.Popup(
            f"""<div style="font-family:Arial,sans-serif; font-size:12px; min-width:160px;">
                <b style="color:#16A34A; font-size:13px;">🟢 ORIGIN</b><br>
                <b>{src_name}</b><br>
                Lat: {start_pt[0]:.4f} N &nbsp; Lon: {start_pt[1]:.4f} E
            </div>""",
            max_width=240
        ),
        tooltip=f"Origin: {src_name}",
        icon=folium.Icon(color="green", icon="play", prefix="glyphicon")
    ).add_to(m)

    # 2. Destination marker (Red)
    folium.Marker(
        location=end_pt,
        popup=folium.Popup(
            f"""<div style="font-family:Arial,sans-serif; font-size:12px; min-width:160px;">
                <b style="color:#DC2626; font-size:13px;">🔴 DESTINATION</b><br>
                <b>{dst_name}</b><br>
                Lat: {end_pt[0]:.4f} N &nbsp; Lon: {end_pt[1]:.4f} E
            </div>""",
            max_width=240
        ),
        tooltip=f"Destination: {dst_name}",
        icon=folium.Icon(color="red", icon="flag", prefix="glyphicon")
    ).add_to(m)

    # 3. Route 1: Direct Arterial Corridor (RED)
    if coords_a:
        dist_a = route_a.get('distance_km', '')
        dur_a = route_a.get('duration_mins', '')
        avg_aqi_a = route_a.get('avg_aqi', '')
        exp_a = route_a.get('exposure_score', '')
        popup_a_html = f"""
        <div style="font-family:Arial,sans-serif; font-size:12px; min-width:190px; padding:4px;">
            <b style="color:#DC2626; font-size:13px;">🔴 Route 1: Arterial Corridor</b><br>
            <div style="margin:6px 0; padding:4px 8px; background:#FEF2F2; color:#DC2626; border-radius:4px; font-weight:bold; border:1px solid #FECACA;">
                High Exposure Risk (Score: {exp_a}/100)
            </div>
            <b>Distance:</b> {dist_a} km<br>
            <b>Est. Time:</b> {dur_a} min<br>
            <b>Average AQI:</b> {avg_aqi_a}<br>
            <span style="color:#991B1B; font-size:11px;">Passes congested urban roads</span>
        </div>
        """
        # Waypoint nodes along Route A
        for wp in route_a.get("waypoint_details", []):
            i = wp.get("index", 1)
            wp_lat = wp.get("lat")
            wp_lon = wp.get("lon")
            wp_aqi = wp.get("aqi", "N/A")
            wp_cat = wp.get("category", "Moderate")
            wp_stn = wp.get("nearest_station_clean", "Pune Region")
            wp_d_stn = wp.get("distance_to_station_km", "")
            wp_d_orig = wp.get("distance_from_origin_km", "")
            if wp_lat is not None and wp_lon is not None:
                folium.CircleMarker(
                    location=[wp_lat, wp_lon],
                    radius=4,
                    color="#DC2626",
                    fill=True,
                    fill_color="#DC2626",
                    fill_opacity=0.85,
                    weight=1.5,
                    tooltip=f"🔴 Route 1 Waypoint #{i}: {wp_aqi} AQI ({wp_cat}) | Near {wp_stn} ({wp_d_stn} km)",
                    popup=folium.Popup(
                        f"""<div style='font-family:Arial,sans-serif; font-size:12px; min-width:180px;'>
                            <b style='color:#DC2626;'>🔴 Arterial Route — Waypoint #{i}</b><br>
                            <b>Ordinary Kriging AQI:</b> <span style='color:#DC2626; font-weight:bold;'>{wp_aqi}</span> ({wp_cat})<br>
                            <b>Nearest Sensor:</b> {wp_stn} ({wp_d_stn} km)<br>
                            <b>Journey Progress:</b> {wp_d_orig} km from origin<br>
                            <span style='color:#0F172A; font-size:10px;'>Coord: {wp_lat:.4f}, {wp_lon:.4f}</span>
                        </div>""",
                        max_width=220
                    )
                ).add_to(m)

    # 4. Route 2: Alternative Corridor (BLUE)
    if coords_b:
        dist_b = route_b.get('distance_km', '')
        dur_b = route_b.get('duration_mins', '')
        avg_aqi_b = route_b.get('avg_aqi', '')
        exp_b = route_b.get('exposure_score', '')
        popup_b_html = f"""
        <div style="font-family:Arial,sans-serif; font-size:12px; min-width:190px; padding:4px;">
            <b style="color:#2563EB; font-size:13px;">🔵 Route 2: Alternative Corridor</b><br>
            <div style="margin:6px 0; padding:4px 8px; background:#EFF6FF; color:#2563EB; border-radius:4px; font-weight:bold; border:1px solid #BFDBFE;">
                Alternative Route (Score: {exp_b}/100)
            </div>
            <b>Distance:</b> {dist_b} km<br>
            <b>Est. Time:</b> {dur_b} min<br>
            <b>Average AQI:</b> {avg_aqi_b}<br>
            <span style="color:#1D4ED8; font-size:11px;">Secondary transit route</span>
        </div>
        """
        folium.PolyLine(
            locations=coords_b,
            color="#2563EB",
            weight=5,
            opacity=0.85,
            dash_array="12 6",
            tooltip=f"🔵 Route 2 (Alternative - Blue): {dist_b} km | {dur_b} min | Avg AQI: {avg_aqi_b} | Exposure: {exp_b}/100",
            popup=folium.Popup(popup_b_html, max_width=250)
        ).add_to(m)

        # Waypoint nodes along Route B
        for wp in route_b.get("waypoint_details", []):
            i = wp.get("index", 1)
            wp_lat = wp.get("lat")
            wp_lon = wp.get("lon")
            wp_aqi = wp.get("aqi", "N/A")
            wp_cat = wp.get("category", "Moderate")
            wp_stn = wp.get("nearest_station_clean", "Pune Region")
            wp_d_stn = wp.get("distance_to_station_km", "")
            wp_d_orig = wp.get("distance_from_origin_km", "")
            if wp_lat is not None and wp_lon is not None:
                folium.CircleMarker(
                    location=[wp_lat, wp_lon],
                    radius=4.5,
                    color="#2563EB",
                    fill=True,
                    fill_color="#2563EB",
                    fill_opacity=0.85,
                    weight=1.5,
                    tooltip=f"🔵 Route 2 Waypoint #{i}: {wp_aqi} AQI ({wp_cat}) | Near {wp_stn} ({wp_d_stn} km)",
                    popup=folium.Popup(
                        f"""<div style='font-family:Arial,sans-serif; font-size:12px; min-width:180px;'>
                            <b style='color:#2563EB;'>🔵 Alternative Route — Waypoint #{i}</b><br>
                            <b>Ordinary Kriging AQI:</b> <span style='color:#2563EB; font-weight:bold;'>{wp_aqi}</span> ({wp_cat})<br>
                            <b>Nearest Sensor:</b> {wp_stn} ({wp_d_stn} km)<br>
                            <b>Journey Progress:</b> {wp_d_orig} km from origin<br>
                            <span style='color:#0F172A; font-size:10px;'>Coord: {wp_lat:.4f}, {wp_lon:.4f}</span>
                        </div>""",
                        max_width=220
                    )
                ).add_to(m)

    # 5. Route 3: Clean-Air Corridor (GREEN - RECOMMENDED)
    if coords_c:
        dist_c = route_c.get('distance_km', '')
        dur_c = route_c.get('duration_mins', '')
        avg_aqi_c = route_c.get('avg_aqi', '')
        exp_c = route_c.get('exposure_score', '')
        popup_c_html = f"""
        <div style="font-family:Arial,sans-serif; font-size:12px; min-width:200px; padding:4px;">
            <b style="color:#16A34A; font-size:13px;">🟢 Route 3: Clean-Air Corridor</b><br>
            <div style="margin:6px 0; padding:4px 8px; background:#F0FDF4; color:#16A34A; border-radius:4px; font-weight:bold; border:1px solid #BBF7D0;">
                ★ RECOMMENDED (Score: {exp_c}/100)
            </div>
            <b>Distance:</b> {dist_c} km<br>
            <b>Est. Time:</b> {dur_c} min<br>
            <b>Average AQI:</b> {avg_aqi_c}<br>
            <b style="color:#166534; font-size:11px;">Lowest cumulative pollution inhalation</b>
        </div>
        """
        folium.PolyLine(
            locations=coords_c,
            color="#16A34A",
            weight=7,
            opacity=0.95,
            tooltip=f"🟢 ★ RECOMMENDED (Green): {dist_c} km | {dur_c} min | Avg AQI: {avg_aqi_c} | Exposure: {exp_c}/100",
            popup=folium.Popup(popup_c_html, max_width=260)
        ).add_to(m)

        # Waypoint nodes along the recommended clean corridor route
        for wp in route_c.get("waypoint_details", []):
            i = wp.get("index", 1)
            wp_lat = wp.get("lat")
            wp_lon = wp.get("lon")
            wp_aqi = wp.get("aqi", "N/A")
            wp_cat = wp.get("category", "Moderate")
            wp_stn = wp.get("nearest_station_clean", "Pune Region")
            wp_d_stn = wp.get("distance_to_station_km", "")
            wp_d_orig = wp.get("distance_from_origin_km", "")
            if wp_lat is not None and wp_lon is not None:
                folium.CircleMarker(
                    location=[wp_lat, wp_lon],
                    radius=5.5,
                    color="#16A34A",
                    fill=True,
                    fill_color="#FFFFFF",
                    fill_opacity=0.95,
                    weight=2.5,
                    tooltip=f"🟢 Route 3 Waypoint #{i}: {wp_aqi} AQI ({wp_cat}) | Near {wp_stn} ({wp_d_stn} km)",
                    popup=folium.Popup(
                        f"""<div style='font-family:Arial,sans-serif; font-size:12px; min-width:190px;'>
                            <b style='color:#16A34A;'>🟢 Clean Corridor — Waypoint #{i}</b><br>
                            <b>Ordinary Kriging AQI:</b> <span style='color:#16A34A; font-weight:bold;'>{wp_aqi}</span> ({wp_cat})<br>
                            <b>Nearest Sensor:</b> {wp_stn} ({wp_d_stn} km)<br>
                            <b>Journey Progress:</b> {wp_d_orig} km from origin<br>
                            <span style='color:#0F172A; font-size:10px;'>Coord: {wp_lat:.4f}, {wp_lon:.4f}</span>
                        </div>""",
                        max_width=230
                    )
                ).add_to(m)

    # Avoided high-pollution hotspots overlay
    for spot in hotspots:
        spot_name = spot.get("name", spot.get("description", "High Pollution Hotspot"))
        s_lat = spot.get("lat")
        s_lon = spot.get("lon")
        if s_lat is not None and s_lon is not None:
            folium.Circle(
                location=[s_lat, s_lon],
                radius=spot.get("radius", 650),
                color="#EF4444", fill=True, fill_color="#DC2626",
                fill_opacity=0.22, weight=1,
                popup=f"<b>Avoided Hotspot:</b><br>{spot_name}<br>Localized AQI: {spot.get('aqi', '')}",
                tooltip=f"Avoided Hotspot: {spot_name} — AQI {spot.get('aqi', '')}"
            ).add_to(m)

    # Fit bounds dynamically to enclose all 3 routes
    all_coords = []
    if coords_c:
        all_coords.extend(coords_c)
    if coords_a:
        all_coords.extend(coords_a)
    if coords_b:
        all_coords.extend(coords_b)

    if all_coords:
        m.fit_bounds(all_coords, padding=(35, 35))

    # Route summary badge bar above the interactive map
    st.markdown(
        f"""<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:10px; margin-bottom:12px;">
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:8px 12px; border-radius:6px; font-size:0.80rem;">
                <b style="color:#166534;">🟢 RECOMMENDED (Green)</b><br>
                <b>{route_c.get('name', 'Route 3')}</b><br>
                Exposure: <b>{route_c.get('exposure_score', '')}/100</b> &nbsp;|&nbsp; Avg AQI: <b>{route_c.get('avg_aqi', '')}</b> &nbsp;|&nbsp; {route_c.get('distance_km', '')} km
            </div>
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #2563EB; padding:8px 12px; border-radius:6px; font-size:0.80rem;">
                <b style="color:#1D4ED8;">🔵 ALTERNATIVE (Blue)</b><br>
                <b>{route_b.get('name', 'Route 2')}</b><br>
                Exposure: <b>{route_b.get('exposure_score', '')}/100</b> &nbsp;|&nbsp; Avg AQI: <b>{route_b.get('avg_aqi', '')}</b> &nbsp;|&nbsp; {route_b.get('distance_km', '')} km
            </div>
            <div style="background:#FEF2F2; border:1px solid #FECACA; border-left:4px solid #DC2626; padding:8px 12px; border-radius:6px; font-size:0.80rem;">
                <b style="color:#991B1B;">🔴 ARTERIAL (Red)</b><br>
                <b>{route_a.get('name', 'Route 1')}</b><br>
                Exposure: <b>{route_a.get('exposure_score', '')}/100</b> &nbsp;|&nbsp; Avg AQI: <b>{route_a.get('avg_aqi', '')}</b> &nbsp;|&nbsp; {route_a.get('distance_km', '')} km
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    st_folium(m, use_container_width=True, height=460, returned_objects=[])

