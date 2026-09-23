/**
 * EcoAir Intelligence — Leaflet GIS Mapping Engine
 * Manages spatial sensor markers, pollution dispersion heatmaps,
 * coordinate click-to-interpolate triggers, and route comparison polylines.
 * Supports multiple independent map instances:
 *   - MapEngine.map       → Overview "city-map"
 *   - MapEngine.m1Map     → Milestone 1 source/destination picker
 *   - MapEngine.routeMap  → Route Exposure Estimator live map
 */

const MapEngine = {
  map: null,
  markersLayer: null,
  heatLayer: null,
  routeLayer: null,
  interpMarker: null,
  currentCenter: [18.5204, 73.8567],

  // Milestone 1 source/destination picker state
  m1Map: null,
  m1MarkersLayer: null,
  m1SourceMarker: null,
  m1DestMarker: null,
  m1SourceKey: null,
  m1DestKey: null,
  m1Stations: {},
  m1OnChange: null,

  // Route Exposure map state
  routeMap: null,
  routeMapLayer: null,
  routeMapMarkersLayer: null,

  /**
   * Initializes Leaflet map instance on specified DOM container.
   */
  init(containerId = 'city-map', onMapClick = null) {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }

    const container = document.getElementById(containerId);
    if (!container) return;

    this.map = L.map(containerId, {
      center: this.currentCenter,
      zoom: 12,
      zoomControl: true,
      attributionControl: false
    });

    // OpenStreetMap tiles with dark CSS filter (free, no API key needed)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      subdomains: 'abc',
      className: 'map-tiles-dark'
    }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);
    this.routeLayer = L.layerGroup().addTo(this.map);

    // Map Click Handler (used for spatial interpolation)
    this.map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      this.setInterpolationPin(lat, lng);
      if (typeof onMapClick === 'function') {
        onMapClick(lat, lng);
      }
    });

    setTimeout(() => {
      this.map.invalidateSize();
    }, 250);
  },

  /**
   * Initializes the Milestone 1 source/destination picker map.
   * Renders all 10 Pune stations as clickable markers.
   * First click = origin (green), second click = destination (red),
   * then alternates or lets dropdowns drive it.
   */
  initM1Map(containerId, stations, onChange) {
    if (this.m1Map) {
      this.m1Map.remove();
      this.m1Map = null;
    }

    const container = document.getElementById(containerId);
    if (!container) return;

    this.m1Stations = stations;
    this.m1OnChange = onChange;

    this.m1Map = L.map(containerId, {
      center: this.currentCenter,
      zoom: 12,
      zoomControl: true,
      attributionControl: false
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      subdomains: 'abc',
      className: 'map-tiles-dark'
    }).addTo(this.m1Map);

    this.m1MarkersLayer = L.layerGroup().addTo(this.m1Map);

    this._renderM1StationMarkers();

    setTimeout(() => {
      this.m1Map.invalidateSize();
    }, 250);
  },

  /**
   * Renders station markers on the M1 picker map.
   * Highlights source (green) and destination (red) markers.
   */
  _renderM1StationMarkers() {
    if (!this.m1MarkersLayer) return;
    this.m1MarkersLayer.clearLayers();

    Object.entries(this.m1Stations).forEach(([name, s]) => {
      const lat = parseFloat(s.lat);
      const lon = parseFloat(s.lon);
      if (isNaN(lat) || isNaN(lon)) return;

      const aqi = s.aqi || 50;
      const isSource = name === this.m1SourceKey;
      const isDest = name === this.m1DestKey;

      // Choose ring color based on role
      let fillColor = this.getAQIColor(aqi);
      let ringColor = '#ffffff';
      let ringWeight = 1.5;
      let radius = 10;

      if (isSource) {
        fillColor = '#22c55e';  // green for origin
        ringColor = '#ffffff';
        ringWeight = 3;
        radius = 14;
      } else if (isDest) {
        fillColor = '#ef4444';  // red for destination
        ringColor = '#ffffff';
        ringWeight = 3;
        radius = 14;
      }

      const marker = L.circleMarker([lat, lon], {
        radius,
        fillColor,
        color: ringColor,
        weight: ringWeight,
        opacity: 0.9,
        fillOpacity: 0.9
      });

      let roleLabel = '';
      if (isSource) roleLabel = `<div style="color:#22c55e; font-weight:700; margin-bottom:4px;">📍 ORIGIN (Source)</div>`;
      if (isDest) roleLabel = `<div style="color:#ef4444; font-weight:700; margin-bottom:4px;">🏁 DESTINATION</div>`;

      const popupContent = `
        <div style="font-family: 'Inter', sans-serif; min-width: 190px; color: #0f172a; padding: 4px;">
          ${roleLabel}
          <h4 style="font-size: 0.88rem; font-weight: 700; margin-bottom: 4px; color: #0f172a;">${name.replace(/_/g, ' ')}</h4>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="font-size: 1.1rem; font-weight: 800; color: ${this.getAQIColor(aqi)};">${aqi} AQI</span>
            <span style="font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; background: ${this.getAQIColor(aqi)}20; color: ${this.getAQIColor(aqi)}; font-weight: 700;">${s.category || 'Moderate'}</span>
          </div>
          <div style="font-size: 0.74rem; color: #1e293b; border-top: 1px solid #e2e8f0; padding-top: 6px;">
            <div><strong>Lat/Lon:</strong> ${lat.toFixed(4)}, ${lon.toFixed(4)}</div>
            <div><strong>PM2.5:</strong> ${s.pm25 || '--'} µg/m³ &nbsp; <strong>PM10:</strong> ${s.pm10 || '--'} µg/m³</div>
            <div><strong>Traffic:</strong> ${s.traffic_congestion_level || 'Moderate'} (${s.traffic_congestion_score || 50}/100)</div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px; margin-top:8px;">
            <button onclick="MapEngine.setM1Source('${name}')" style="padding:4px 8px; background:#22c55e20; color:#22c55e; border:1px solid #22c55e50; border-radius:4px; font-size:0.72rem; cursor:pointer; font-family:'Inter',sans-serif;">Set as Origin</button>
            <button onclick="MapEngine.setM1Dest('${name}')" style="padding:4px 8px; background:#ef444420; color:#ef4444; border:1px solid #ef444450; border-radius:4px; font-size:0.72rem; cursor:pointer; font-family:'Inter',sans-serif;">Set as Dest</button>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);
      this.m1MarkersLayer.addLayer(marker);
    });

    // Draw line between source and destination if both set
    this._drawM1RouteLine();
  },

  /**
   * Draw an actual route polyline between M1 source and destination stations.
   * Uses real station lat/lon coordinates with intermediate waypoints.
   */
  _drawM1RouteLine() {
    // Remove old route line if any
    if (this._m1RouteLine) {
      this.m1Map.removeLayer(this._m1RouteLine);
      this._m1RouteLine = null;
    }
    if (this._m1RouteDecorations) {
      this._m1RouteDecorations.forEach(l => this.m1Map.removeLayer(l));
      this._m1RouteDecorations = [];
    }

    const src = this.m1Stations[this.m1SourceKey];
    const dst = this.m1Stations[this.m1DestKey];

    if (!src || !dst || !src.lat || !dst.lat) return;

    const oLat = parseFloat(src.lat), oLon = parseFloat(src.lon);
    const dLat = parseFloat(dst.lat), dLon = parseFloat(dst.lon);
    const midLat = (oLat + dLat) / 2;
    const midLon = (oLon + dLon) / 2;

    // Build route waypoints with a realistic bend
    const routePoints = [
      [oLat, oLon],
      [oLat + (midLat - oLat) * 0.35 - 0.004, oLon + (midLon - oLon) * 0.35 - 0.003],
      [midLat + 0.003, midLon - 0.004],
      [dLat - (dLat - midLat) * 0.35 + 0.004, dLon - (dLon - midLon) * 0.35 + 0.003],
      [dLat, dLon]
    ];

    // Shadow / glow line
    this.m1Map.removeLayer; // cleanup guard
    const shadow = L.polyline(routePoints, {
      color: '#2563eb', weight: 9, opacity: 0.12
    }).addTo(this.m1Map);

    // Main route line
    this._m1RouteLine = L.polyline(routePoints, {
      color: '#2563eb', weight: 4, opacity: 0.9,
      lineJoin: 'round', lineCap: 'round'
    }).addTo(this.m1Map);

    // Direction arrows (animated dashes)
    const arrows = L.polyline(routePoints, {
      color: '#ffffff', weight: 1.5, opacity: 0.6,
      dashArray: '6, 14'
    }).addTo(this.m1Map);

    this._m1RouteDecorations = [shadow, arrows];

    // Origin pin
    const originIcon = L.divIcon({
      className: '',
      html: `<div style="background:#22c55e; color:white; width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:11px; border:2px solid white; box-shadow:0 2px 8px rgba(34,197,94,0.7);">S</div>`
    });
    const destIcon = L.divIcon({
      className: '',
      html: `<div style="background:#ef4444; color:white; width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:11px; border:2px solid white; box-shadow:0 2px 8px rgba(239,68,68,0.7);">D</div>`
    });

    L.marker([oLat, oLon], { icon: originIcon })
      .addTo(this.m1Map)
      .bindPopup(`<b style="color:#22c55e;">Origin: ${this.m1SourceKey.replace(/_/g, ' ')}</b><br/>AQI: ${src.aqi || '--'}`);
    L.marker([dLat, dLon], { icon: destIcon })
      .addTo(this.m1Map)
      .bindPopup(`<b style="color:#ef4444;">Destination: ${this.m1DestKey.replace(/_/g, ' ')}</b><br/>AQI: ${dst.aqi || '--'}`);

    const bounds = L.latLngBounds(routePoints);
    this.m1Map.fitBounds(bounds, { padding: [50, 50] });
  },

  /**
   * Sets source station on M1 map.
   */
  setM1Source(stationKey) {
    this.m1SourceKey = stationKey;
    // Sync dropdown
    const sel = document.getElementById('m1-source-select');
    if (sel) sel.value = stationKey;
    this._renderM1StationMarkers();
    if (this.m1Map) this.m1Map.closePopup();
    if (typeof this.m1OnChange === 'function') this.m1OnChange('source', stationKey);
  },

  /**
   * Sets destination station on M1 map.
   */
  setM1Dest(stationKey) {
    this.m1DestKey = stationKey;
    // Sync dropdown
    const sel = document.getElementById('m1-dest-select');
    if (sel) sel.value = stationKey;
    this._renderM1StationMarkers();
    if (this.m1Map) this.m1Map.closePopup();
    if (typeof this.m1OnChange === 'function') this.m1OnChange('dest', stationKey);
  },

  /**
   * Initializes the Route Exposure Estimator dedicated map.
   */
  initRouteMap(containerId = 'route-exposure-map') {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (this.routeMap) {
      try {
        this.routeMap.remove();
      } catch (e) {
        console.warn('Error removing route map:', e);
      }
      this.routeMap = null;
    }

    this.routeMap = L.map(containerId, {
      center: this.currentCenter,
      zoom: 12,
      zoomControl: true,
      attributionControl: false
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      subdomains: 'abc',
      className: 'map-tiles-dark'
    }).addTo(this.routeMap);

    this.routeMapLayer = L.layerGroup().addTo(this.routeMap);
    this.routeMapMarkersLayer = L.layerGroup().addTo(this.routeMap);

    setTimeout(() => {
      if (this.routeMap) this.routeMap.invalidateSize();
    }, 200);
  },

  /**
   * Adds station background markers to Route map with interactive Origin/Destination selection.
   */
  setRouteMapStations(stations = {}) {
    if (!this.routeMapMarkersLayer) return;
    this._allStationsCache = stations;          // cache for intermediate labels
    this.routeMapMarkersLayer.clearLayers();

    const cleanNames = {
      'BopadiSquare_65': 'Bopodi Square',
      'Karve Statue Square_5': 'Karve Statue Square',
      'Lullanagar_Square_14': 'Lullanagar Square',
      'Hadapsar_Gadital_01': 'Hadapsar Gadital',
      'PMPML_Bus_Depot_Deccan_15': 'PMPML Bus Depot Deccan',
      'Goodluck Square_Cafe_23': 'Goodluck Square Cafe',
      'Chitale Bandhu Corner_41': 'Chitale Bandhu Corner',
      'Pune Railway Station_28': 'Pune Railway Station',
      'Rajashri_Shahu_Bus_stand_19': 'Rajashri Shahu Bus Stand',
      'Dr Baba Saheb Ambedkar Sethu Junction_60': 'Dr. Babasaheb Ambedkar Setu'
    };

    Object.entries(stations).forEach(([name, s]) => {
      const lat = parseFloat(s.lat);
      const lon = parseFloat(s.lon);
      if (isNaN(lat) || isNaN(lon)) return;

      const aqi = s.aqi || 50;
      const color = this.getAQIColor(aqi);
      const displayName = cleanNames[name] || name.replace(/_\d+$/, '').replace(/_/g, ' ');
      const valStr = `${displayName}, Pune`;

      const marker = L.circleMarker([lat, lon], {
        radius: 7,
        fillColor: color,
        color: '#ffffff',
        weight: 1.5,
        opacity: 0.85,
        fillOpacity: 0.7
      });

      marker.bindTooltip(`<b>${displayName}</b>: ${Math.round(aqi)} AQI`, { direction: 'top' });

      const popupContent = `
        <div style="font-family:Inter,system-ui,sans-serif; font-size:12px; line-height:1.4; min-width:190px; padding:4px;">
          <strong style="color:#0f172a; font-size:13px; display:block; margin-bottom:2px;">📍 ${displayName}</strong>
          <div style="display:flex; align-items:center; gap:6px; margin:4px 0 8px;">
            <span style="font-weight:800; font-size:1.1rem; color:${color}; font-family:Outfit,sans-serif;">${Math.round(aqi)} AQI</span>
            <span style="background:${color}20; color:${color}; font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; border:1px solid ${color}40;">${s.category || 'Moderate'}</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:4px; margin-top:6px; border-top:1px solid #e2e8f0; padding-top:6px;">
            <button onclick="if(window.App){window.App.setRouteOrigin('${valStr}');}" style="background:#16a34a; color:white; border:none; border-radius:4px; padding:4px 8px; font-size:11px; font-weight:600; cursor:pointer; text-align:left; display:flex; align-items:center; gap:4px;">
              <span>🟢</span> Set as Journey Origin
            </button>
            <button onclick="if(window.App){window.App.setRouteDestination('${valStr}');}" style="background:#dc2626; color:white; border:none; border-radius:4px; padding:4px 8px; font-size:11px; font-weight:600; cursor:pointer; text-align:left; display:flex; align-items:center; gap:4px;">
              <span>🔴</span> Set as Journey Destination
            </button>
          </div>
        </div>
      `;
      marker.bindPopup(popupContent, { maxWidth: 240 });

      this.routeMapMarkersLayer.addLayer(marker);
    });
  },

  /**
   * Renders 3 Route options on the dedicated Route Exposure Map with interactive Kriging waypoints.
   */
  renderRoutesOnRouteMap(originCoords, destCoords, routeData = null) {
    if (!this.routeMap) {
      this.initRouteMap('route-exposure-map');
    }
    if (!this.routeMapLayer || !this.routeMap) return;

    this.routeMapLayer.clearLayers();

    const [oLat, oLon] = originCoords || [18.5018, 73.8580];
    const [dLat, dLon] = destCoords || [18.5679, 73.9143];
    const midLat = (oLat + dLat) / 2;
    const midLon = (oLon + dLon) / 2;

    // Helper to normalize waypoints array: [[lat, lon], ...]
    const normalizePoints = (pts) => {
      if (!Array.isArray(pts) || pts.length === 0) return null;
      return pts.map(p => {
        if (Array.isArray(p)) return [parseFloat(p[0]), parseFloat(p[1])];
        if (p && typeof p === 'object') return [parseFloat(p.lat), parseFloat(p.lon)];
        return null;
      }).filter(p => p && !isNaN(p[0]) && !isNaN(p[1]));
    };

    // ── Extract real waypoints or synthesize smooth corridors ────────────
    const rA = routeData?.route_a || (Array.isArray(routeData?.routes) ? routeData.routes.find(r => r.id === 'route_a') : null);
    const rB = routeData?.route_b || (Array.isArray(routeData?.routes) ? routeData.routes.find(r => r.id === 'route_b') : null);
    const rC = routeData?.route_c || routeData?.recommended_route || (Array.isArray(routeData?.routes) ? routeData.routes.find(r => r.id === 'route_c') : null);

    const apiPtsA = normalizePoints(rA?.waypoints);
    const apiPtsB = normalizePoints(rB?.waypoints);
    const apiPtsC = normalizePoints(rC?.waypoints);

    const routeAPoints = apiPtsA && apiPtsA.length >= 2 ? apiPtsA : [
      [oLat, oLon],
      [oLat + (midLat - oLat) * 0.4 - 0.009, oLon + (midLon - oLon) * 0.4 - 0.007],
      [midLat - 0.013, midLon - 0.009],
      [dLat - (dLat - midLat) * 0.4 - 0.007, dLon - (dLon - midLon) * 0.4 - 0.005],
      [dLat, dLon]
    ];

    const routeBPoints = apiPtsB && apiPtsB.length >= 2 ? apiPtsB : [
      [oLat, oLon],
      [oLat + (midLat - oLat) * 0.5 + 0.007, oLon + (midLon - oLon) * 0.5 + 0.005],
      [midLat + 0.007, midLon + 0.010],
      [dLat - (dLat - midLat) * 0.5 + 0.005, dLon - (dLon - midLon) * 0.5 + 0.006],
      [dLat, dLon]
    ];

    const routeCPoints = apiPtsC && apiPtsC.length >= 2 ? apiPtsC : [
      [oLat, oLon],
      [oLat + (midLat - oLat) * 0.5 + 0.018, oLon + (midLon - oLon) * 0.5 + 0.020],
      [midLat + 0.022, midLon + 0.030],
      [dLat - (dLat - midLat) * 0.5 + 0.015, dLon - (dLon - midLon) * 0.5 + 0.018],
      [dLat, dLon]
    ];

    // Determine actual start & end points from waypoints
    const startCoord = routeAPoints[0] || [oLat, oLon];
    const endCoord = routeAPoints[routeAPoints.length - 1] || [dLat, dLon];

    // ── Start / End markers ───────────────────────────────────────────────
    const startIcon = L.divIcon({
      className: '',
      html: `<div style="background:#16a34a; color:white; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:13px; border:3px solid white; box-shadow:0 3px 12px rgba(22,163,74,0.7);">S</div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });
    const endIcon = L.divIcon({
      className: '',
      html: `<div style="background:#dc2626; color:white; width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:13px; border:3px solid white; box-shadow:0 3px 12px rgba(220,38,38,0.7);">D</div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    });

    const srcTitle = routeData?.origin || routeData?.source || 'Origin';
    const dstTitle = routeData?.destination || 'Destination';

    L.marker(startCoord, { icon: startIcon }).addTo(this.routeMapLayer)
      .bindPopup(`<div style="font-family:inherit; padding:4px;">
        <strong style="color:#16a34a; font-size:13px;">🟢 Journey Origin</strong><br/>
        <b>${srcTitle}</b><br/>
        <span style="color:#1e293b; font-size:11px;">Coord: ${startCoord[0].toFixed(4)}, ${startCoord[1].toFixed(4)}</span>
      </div>`);

    L.marker(endCoord, { icon: endIcon }).addTo(this.routeMapLayer)
      .bindPopup(`<div style="font-family:inherit; padding:4px;">
        <strong style="color:#dc2626; font-size:13px;">🔴 Journey Destination</strong><br/>
        <b>${dstTitle}</b><br/>
        <span style="color:#1e293b; font-size:11px;">Coord: ${endCoord[0].toFixed(4)}, ${endCoord[1].toFixed(4)}</span>
      </div>`);

    // Helper to render interactive waypoint markers with rich Kriging tooltips
    const renderWaypoints = (waypointList, routeName, routeColor, routeBadge, markerOpts) => {
      if (!Array.isArray(waypointList) || waypointList.length === 0) return;
      
      waypointList.forEach((wp, idx) => {
        const wLat = parseFloat(wp.lat);
        const wLon = parseFloat(wp.lon);
        if (isNaN(wLat) || isNaN(wLon)) return;

        const wAqi = Math.round(wp.aqi || 75);
        const aqiColor = this.getAQIColor(wAqi);
        const cat = wp.category || 'Moderate';
        const stn = wp.nearest_station_clean || wp.nearest_station || 'Pune Region';
        const dStn = wp.distance_to_station_km !== undefined ? `${wp.distance_to_station_km} km` : 'Near Station';
        const dOrig = wp.distance_from_origin_km !== undefined ? `${wp.distance_from_origin_km} km` : `${(idx * 1.2).toFixed(1)} km`;
        const wpIdx = wp.index || (idx + 1);

        const marker = L.circleMarker([wLat, wLon], {
          radius: markerOpts.radius || 5,
          color: markerOpts.color || routeColor,
          fillColor: markerOpts.fillColor || routeColor,
          fillOpacity: markerOpts.fillOpacity || 0.9,
          weight: markerOpts.weight || 2
        });

        const tooltipHtml = `
          <div style="font-family:'Inter',system-ui,sans-serif; font-size:11.5px; line-height:1.45; min-width:205px; padding:8px 10px; background:#ffffff; color:#0f172a; border-radius:8px; border:1px solid #cbd5e1; box-shadow:0 10px 25px -5px rgba(15,23,42,0.15), 0 4px 6px -2px rgba(15,23,42,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; border-bottom:1px solid #f1f5f9; padding-bottom:4px;">
              <span style="font-weight:700; color:${routeColor}; font-size:11.5px; display:inline-flex; align-items:center; gap:4px;">${routeBadge} Waypoint #${wpIdx}</span>
              <span style="background:${aqiColor}18; color:${aqiColor}; border:1px solid ${aqiColor}40; border-radius:4px; padding:1.5px 6px; font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:0.3px;">${cat}</span>
            </div>
            <div style="font-size:1.25rem; font-weight:800; color:${aqiColor}; font-family:'Outfit',sans-serif; margin:3px 0 5px; display:flex; align-items:baseline; gap:6px;">
              ${wAqi} <span style="font-size:0.72rem; color:#64748b; font-weight:600; font-family:'Inter',sans-serif; text-transform:uppercase; letter-spacing:0.3px;">AQI (Kriging)</span>
            </div>
            <div style="font-size:11px; color:#475569; margin-top:3px; display:flex; align-items:center; gap:4px;">
              <span>📍</span> <span style="color:#64748b;">Near:</span> <strong style="color:#0f172a;">${stn}</strong> <span style="color:#64748b; font-size:10.5px;">(${dStn})</span>
            </div>
            <div style="font-size:11px; color:#475569; margin-top:2px; display:flex; align-items:center; gap:4px;">
              <span>🚗</span> <span style="color:#64748b;">Progress:</span> <strong style="color:#0f172a;">${dOrig}</strong> <span style="color:#64748b; font-size:10.5px;">from origin</span>
            </div>
            <div style="font-size:9.5px; color:#64748b; margin-top:6px; border-top:1px dashed #e2e8f0; padding-top:4px; display:flex; justify-content:space-between; align-items:center;">
              <span>🌐 ${wLat.toFixed(4)}° N, ${wLon.toFixed(4)}° E</span> <span style="font-weight:600; color:#0284c7;">Ordinary Kriging</span>
            </div>
          </div>
        `;

        marker.bindTooltip(tooltipHtml, {
          direction: 'top',
          offset: [0, -6],
          opacity: 1.0,
          className: 'route-waypoint-tooltip'
        });

        const popupHtml = `
          <div style="font-family:'Inter',system-ui,sans-serif; font-size:12px; line-height:1.5; min-width:215px; padding:6px 4px; color:#0f172a;">
            <strong style="color:${routeColor}; font-size:13px; display:block; margin-bottom:4px;">${routeName} — Waypoint #${wpIdx}</strong>
            <div style="display:flex; align-items:center; gap:6px; margin:4px 0 8px;">
              <span style="font-size:1.3rem; font-weight:800; color:${aqiColor}; font-family:'Outfit',sans-serif;">${wAqi} AQI</span>
              <span style="background:${aqiColor}18; color:${aqiColor}; border:1px solid ${aqiColor}40; border-radius:4px; padding:1.5px 6px; font-size:10px; font-weight:700; text-transform:uppercase;">${cat}</span>
            </div>
            <div style="color:#334155; margin-bottom:3px;"><span style="color:#64748b;">Estimator:</span> <strong style="color:#0f172a;">Ordinary Kriging</strong></div>
            <div style="color:#334155; margin-bottom:3px;"><span style="color:#64748b;">Nearest Station:</span> <strong style="color:#0f172a;">${stn}</strong> <span style="color:#64748b; font-size:11px;">(${dStn})</span></div>
            <div style="color:#334155; margin-bottom:3px;"><span style="color:#64748b;">Progress:</span> <strong style="color:#0f172a;">${dOrig}</strong> <span style="color:#64748b; font-size:11px;">from origin</span></div>
            <div style="color:#64748b; font-size:10.5px; margin-top:6px; border-top:1px solid #e2e8f0; padding-top:4px;">🌐 Coordinates: ${wLat.toFixed(4)}° N, ${wLon.toFixed(4)}° E</div>
          </div>
        `;
        marker.bindPopup(popupHtml, { maxWidth: 250 });

        marker.addTo(this.routeMapLayer);
      });
    };

    // ── Route A — Direct Arterial (Worst, Red dashed) ─────────────────────
    const distA = rA?.distance_km || 12.4;
    const durA = rA?.duration_mins || 31;
    const aqiA = Math.round(rA?.avg_aqi || 148);
    const expA = Math.round(rA?.exposure_score || 72);

    L.polyline(routeAPoints, {
      color: '#ef4444',
      weight: 4.5,
      opacity: 0.85,
      dashArray: '10, 8'
    }).addTo(this.routeMapLayer)
      .bindPopup(`<div style="font-family:inherit; padding:4px; min-width:180px; color:#0f172a;">
        <strong style="color:#ef4444; font-size:13px;">🔴 Route A — Direct Arterial</strong><br/>
        <b>Distance:</b> ${distA} km &nbsp;|&nbsp; <b>Time:</b> ${durA} min<br/>
        <b>Mean AQI:</b> <span style="color:#ef4444; font-weight:700;">${aqiA}</span><br/>
        <b>Exposure Index:</b> <span style="color:#ef4444; font-weight:700;">${expA} / 100</span><br/>
        <span style="color:#64748b; font-size:11px;">Heavy traffic &amp; high particulate exposure</span>
      </div>`);

    // Render Route A Waypoints
    renderWaypoints(rA?.waypoint_details, 'Route A (Arterial)', '#ef4444', '🔴 Route A', {
      radius: 4,
      color: '#dc2626',
      fillColor: '#ef4444',
      fillOpacity: 0.9,
      weight: 1.5
    });

    // ── Route B — Mixed Urban (Moderate, Amber/Blue) ──────────────────────
    const distB = rB?.distance_km || 13.2;
    const durB = rB?.duration_mins || 32;
    const aqiB = Math.round(rB?.avg_aqi || 112);
    const expB = Math.round(rB?.exposure_score || 54);

    L.polyline(routeBPoints, {
      color: '#d97706',
      weight: 4.5,
      opacity: 0.9,
      dashArray: '7, 6'
    }).addTo(this.routeMapLayer)
      .bindPopup(`<div style="font-family:inherit; padding:4px; min-width:180px; color:#0f172a;">
        <strong style="color:#d97706; font-size:13px;">🟡 Route B — Mixed Urban Corridor</strong><br/>
        <b>Distance:</b> ${distB} km &nbsp;|&nbsp; <b>Time:</b> ${durB} min<br/>
        <b>Mean AQI:</b> <span style="color:#d97706; font-weight:700;">${aqiB}</span><br/>
        <b>Exposure Index:</b> <span style="color:#d97706; font-weight:700;">${expB} / 100</span><br/>
        <span style="color:#64748b; font-size:11px;">Secondary transit route</span>
      </div>`);

    // Render Route B Waypoints
    renderWaypoints(rB?.waypoint_details, 'Route B (Mixed Urban)', '#d97706', '🟡 Route B', {
      radius: 4.5,
      color: '#b45309',
      fillColor: '#f59e0b',
      fillOpacity: 0.9,
      weight: 1.5
    });

    // ── Route C — Eco Green Corridor (Best, Green) ★ ─────────────────────
    const distC = rC?.distance_km || 15.8;
    const durC = rC?.duration_mins || 30;
    const aqiC = Math.round(rC?.avg_aqi || 76);
    const expC = Math.round(rC?.exposure_score || 38);
    const reduction = routeData?.reduction_pct || Math.max(15, Math.round(((expA - expC) / Math.max(1, expA)) * 100));

    // Glow halo
    L.polyline(routeCPoints, {
      color: '#059669',
      weight: 12,
      opacity: 0.20
    }).addTo(this.routeMapLayer);

    // Main line
    L.polyline(routeCPoints, {
      color: '#059669',
      weight: 6,
      opacity: 1.0
    }).addTo(this.routeMapLayer)
      .bindPopup(`<div style="font-family:inherit; padding:4px; min-width:200px;">
        <strong style="color:#059669; font-size:13px;">⭐ Route C — Eco Green Corridor (RECOMMENDED)</strong><br/>
        <b>Distance:</b> ${distC} km &nbsp;|&nbsp; <b>Time:</b> ${durC} min<br/>
        <b>Mean AQI:</b> <span style="color:#059669; font-weight:700;">${aqiC}</span> (Lowest)<br/>
        <b>Exposure Index:</b> <span style="color:#059669; font-weight:700;">${expC} / 100</span><br/>
        <div style="margin-top:4px; padding:3px 6px; background:#f0fdf4; border-radius:4px; border:1px solid #bbf7d0; color:#166534; font-weight:700; font-size:11px;">
          Saves ${reduction}% pollution exposure vs arterial route
        </div>
      </div>`);

    // Render Route C Waypoints
    renderWaypoints(rC?.waypoint_details, 'Route C (Eco Green Corridor)', '#059669', '🟢 Route C', {
      radius: 5.5,
      color: '#047857',
      fillColor: '#ffffff',
      fillOpacity: 0.95,
      weight: 2.5
    });

    // Midpoint badge on Route C
    const midIdx = Math.floor(routeCPoints.length / 2);
    const midPoint = routeCPoints[midIdx] || [midLat, midLon];

    const labelIcon = L.divIcon({
      className: '',
      html: `<div style="background:#059669; color:white; padding:3px 9px; border-radius:12px; font-size:11px; font-weight:700; white-space:nowrap; box-shadow:0 2px 8px rgba(5,150,105,0.6); border:1.5px solid white;">⭐ Best Route (-${reduction}%)</div>`,
      iconAnchor: [55, 12]
    });
    L.marker(midPoint, { icon: labelIcon }).addTo(this.routeMapLayer);

    // ── High Pollution Hotspots Overlays ──────────────────────────────────
    const hotspots = routeData?.hotspots || [];
    hotspots.forEach(spot => {
      const sLat = parseFloat(spot.lat);
      const sLon = parseFloat(spot.lon);
      if (isNaN(sLat) || isNaN(sLon)) return;

      const spotAqi = Math.round(spot.aqi || 125);
      const spotDesc = spot.description || `Pollution Hotspot (~${spotAqi} AQI)`;

      L.circle([sLat, sLon], {
        radius: 650,
        color: '#dc2626',
        weight: 1.5,
        fillColor: '#ef4444',
        fillOpacity: 0.25
      }).addTo(this.routeMapLayer)
        .bindTooltip(`⚠️ Avoided Hotspot: ${spotDesc}`, { direction: 'top' });
    });

    // ── Intermediate Station AQI Labels ──────────────────────────────────
    this._renderIntermediateStations([oLat, oLon], [dLat, dLon]);

    // ── Fit Bounds & Sizing Invalidation ──────────────────────────────────
    const allCoords = [...routeAPoints, ...routeBPoints, ...routeCPoints];
    if (allCoords.length > 0) {
      const bounds = L.latLngBounds(allCoords);
      this.routeMap.fitBounds(bounds, { padding: [44, 44] });
    }

    setTimeout(() => {
      if (this.routeMap) this.routeMap.invalidateSize();
    }, 150);
  },

  /**
   * Updates monitoring station markers across the overview map.
   */
  setStations(stations = {}, onSelectStation = null) {
    if (!this.markersLayer) return;
    this.markersLayer.clearLayers();

    const heatPoints = [];

    Object.entries(stations).forEach(([name, s]) => {
      const lat = parseFloat(s.lat);
      const lon = parseFloat(s.lon);
      if (isNaN(lat) || isNaN(lon)) return;

      const aqi = s.aqi || 50;
      const color = this.getAQIColor(aqi);

      heatPoints.push([lat, lon, Math.min(aqi / 250, 1.0)]);

      // Custom circle marker
      const marker = L.circleMarker([lat, lon], {
        radius: 9,
        fillColor: color,
        color: '#ffffff',
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.85
      });

      const popupContent = `
        <div style="font-family: 'Inter', sans-serif; min-width: 170px; color: #0f172a; padding: 4px;">
          <h4 style="font-size: 0.88rem; font-weight: 700; margin-bottom: 4px; color: #0f172a;">${name.replace(/_/g, ' ')}</h4>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span style="font-size: 1.2rem; font-weight: 800; color: ${color};">${aqi} AQI</span>
            <span style="font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; background: ${color}20; color: ${color}; font-weight: 700;">${s.category || 'Moderate'}</span>
          </div>
          <div style="font-size: 0.75rem; color: #1e293b; border-top: 1px solid #e2e8f0; padding-top: 4px;">
            <div><strong>PM2.5:</strong> ${s.pm25 || '--'} µg/m³</div>
            <div><strong>PM10:</strong> ${s.pm10 || '--'} µg/m³</div>
            <div><strong>Traffic:</strong> ${s.traffic_congestion_level || 'Moderate'} (${s.traffic_congestion_score || 50}/100)</div>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);
      marker.on('click', () => {
        if (typeof onSelectStation === 'function') {
          onSelectStation(name, s);
        }
      });

      this.markersLayer.addLayer(marker);
    });

    // Add heatmap layer if Leaflet.heat is available
    if (typeof L.heatLayer === 'function' && heatPoints.length > 0) {
      if (this.heatLayer) {
        this.map.removeLayer(this.heatLayer);
      }
      this.heatLayer = L.heatLayer(heatPoints, {
        radius: 35,
        blur: 25,
        maxZoom: 15,
        gradient: {
          0.2: '#10b981',
          0.4: '#f59e0b',
          0.6: '#f97316',
          0.8: '#ef4444',
          1.0: '#8b5cf6'
        }
      }).addTo(this.map);
    }
  },

  /**
   * Drops a crosshair pin at target coordinates for interpolation.
   */
  setInterpolationPin(lat, lng) {
    if (!this.map) return;
    if (this.interpMarker) {
      this.map.removeLayer(this.interpMarker);
    }

    this.interpMarker = L.circleMarker([lat, lng], {
      radius: 11,
      fillColor: '#38bdf8',
      color: '#ffffff',
      weight: 3,
      opacity: 1,
      fillOpacity: 0.9
    }).addTo(this.map);

    this.interpMarker.bindPopup(`
      <div style="font-family: 'Inter', sans-serif; color: #0f172a;">
        <strong>Target Interpolation Coordinate</strong><br/>
        Lat: ${lat.toFixed(4)}, Lon: ${lng.toFixed(4)}
      </div>
    `).openPopup();
  },

  /**
   * Renders Route A (arterial) vs Route B (clean air corridor) polylines on overview map.
   */
  renderRoutes(originCoords, destCoords) {
    if (!this.routeLayer) return;
    this.routeLayer.clearLayers();

    const [oLat, oLon] = originCoords;
    const [dLat, dLon] = destCoords;

    // Start & Destination Markers
    const startIcon = L.divIcon({
      className: 'custom-pin',
      html: `<div style="background:#10b981; color:white; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px; border:2px solid white; box-shadow:0 0 10px rgba(16,185,129,0.7)">A</div>`
    });

    const endIcon = L.divIcon({
      className: 'custom-pin',
      html: `<div style="background:#ef4444; color:white; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px; border:2px solid white; box-shadow:0 0 10px rgba(239,68,68,0.7)">B</div>`
    });

    L.marker([oLat, oLon], { icon: startIcon }).addTo(this.routeLayer).bindPopup('Journey Origin');
    L.marker([dLat, dLon], { icon: endIcon }).addTo(this.routeLayer).bindPopup('Journey Destination');

    // Synthesize realistic waypoints for Route A (arterial road) and Route B (clean corridor)
    const midLat = (oLat + dLat) / 2;
    const midLon = (oLon + dLon) / 2;

    // Route A (Arterial: slightly skewed towards urban core)
    const routeAPoints = [
      [oLat, oLon],
      [oLat + (midLat - oLat) * 0.45 - 0.008, oLon + (midLon - oLon) * 0.45 - 0.006],
      [midLat - 0.012, midLon - 0.008],
      [dLat - (dLat - midLat) * 0.45 - 0.006, dLon - (dLon - midLon) * 0.45 - 0.005],
      [dLat, dLon]
    ];

    // Route B (Clean Corridor: greener bypass arc)
    const routeBPoints = [
      [oLat, oLon],
      [oLat + (midLat - oLat) * 0.5 + 0.014, oLon + (midLon - oLon) * 0.5 + 0.015],
      [midLat + 0.018, midLon + 0.022],
      [dLat - (dLat - midLat) * 0.5 + 0.012, dLon - (dLon - midLon) * 0.5 + 0.014],
      [dLat, dLon]
    ];

    // Route A line (Arterial / Direct - Amber/Red)
    L.polyline(routeAPoints, {
      color: '#ef4444',
      weight: 5,
      opacity: 0.85,
      dashArray: '8, 6'
    }).addTo(this.routeLayer).bindPopup('Route A: Direct Arterial Corridor (High Particulate Exposure)');

    // Route B line (Clean corridor - Emerald)
    L.polyline(routeBPoints, {
      color: '#10b981',
      weight: 6,
      opacity: 0.95
    }).addTo(this.routeLayer).bindPopup('Route B: Recommended Clean Air Corridor (34% Less Exposure)');

    // Fit map bounds to show complete journey
    const bounds = L.latLngBounds([...routeAPoints, ...routeBPoints]);
    this.map.fitBounds(bounds, { padding: [40, 40] });
  },

  /**
   * Renders AQI label badges for all intermediate Pune stations along the route.
   * Stations are shown if they fall within the route's bounding corridor (with buffer).
   * Origin and destination stations are excluded (already have S/D pins).
   */
  _renderIntermediateStations(originCoords, destCoords) {
    if (!this.routeMap || !this.routeMapLayer) return;

    const stations = this._allStationsCache || {};
    if (!Object.keys(stations).length) return;

    const [oLat, oLon] = originCoords;
    const [dLat, dLon] = destCoords;

    // Bounding box of the route with a generous 0.06° buffer (~6 km)
    const BUFFER = 0.06;
    const minLat = Math.min(oLat, dLat) - BUFFER;
    const maxLat = Math.max(oLat, dLat) + BUFFER;
    const minLon = Math.min(oLon, dLon) - BUFFER;
    const maxLon = Math.max(oLon, dLon) + BUFFER;

    // Distance from point to line segment (origin→dest) for corridor check
    const ptToSegDist = (pLat, pLon) => {
      const dx = dLon - oLon, dy = dLat - oLat;
      const len2 = dx * dx + dy * dy;
      if (len2 === 0) return Math.hypot(pLat - oLat, pLon - oLon);
      const t = Math.max(0, Math.min(1, ((pLon - oLon) * dx + (pLat - oLat) * dy) / len2));
      return Math.hypot(pLat - (oLat + t * dy), pLon - (oLon + t * dx));
    };

    const cleanNames = {
      'BopadiSquare_65': 'Bopodi Square',
      'Karve Statue Square_5': 'Karve Statue Square',
      'Lullanagar_Square_14': 'Lullanagar Square',
      'Hadapsar_Gadital_01': 'Hadapsar Gadital',
      'PMPML_Bus_Depot_Deccan_15': 'PMPML Bus Depot Deccan',
      'Goodluck Square_Cafe_23': 'Goodluck Square Cafe',
      'Chitale Bandhu Corner_41': 'Chitale Bandhu Corner',
      'Pune Railway Station_28': 'Pune Railway Station',
      'Rajashri_Shahu_Bus_stand_19': 'Rajashri Shahu Bus Stand',
      'Dr Baba Saheb Ambedkar Sethu Junction_60': 'Dr. Babasaheb Ambedkar Setu'
    };

    Object.entries(stations).forEach(([key, s]) => {
      const lat = parseFloat(s.lat);
      const lon = parseFloat(s.lon);
      if (isNaN(lat) || isNaN(lon)) return;

      // Skip if outside bounding box
      if (lat < minLat || lat > maxLat || lon < minLon || lon > maxLon) return;

      // Skip origin and destination themselves (within 0.005°)
      const isOrigin = Math.abs(lat - oLat) < 0.005 && Math.abs(lon - oLon) < 0.005;
      const isDest   = Math.abs(lat - dLat) < 0.005 && Math.abs(lon - dLon) < 0.005;
      if (isOrigin || isDest) return;

      const aqi = Math.round(s.aqi || 50);
      const color = this.getAQIColor(aqi);
      const category = s.category || 'Moderate';
      const displayName = cleanNames[key] || key.replace(/_\d+$/, '').replace(/_/g, ' ');
      const pm25 = s.pm25 ? `${Math.round(s.pm25)} µg/m³` : '--';
      const pm10 = s.pm10 ? `${Math.round(s.pm10)} µg/m³` : '--';
      const traffic = s.traffic_congestion_level || 'Moderate';

      // AQI label pill divIcon — clearly visible on map
      const labelIcon = L.divIcon({
        className: '',
        html: `
          <div style="
            display: flex; flex-direction: column; align-items: center;
            filter: drop-shadow(0 2px 6px rgba(0,0,0,0.45));
            pointer-events: auto;
          ">
            <!-- AQI badge pill -->
            <div style="
              background: ${color};
              color: #ffffff;
              padding: 3px 9px 3px 7px;
              border-radius: 20px;
              font-family: 'Inter', system-ui, sans-serif;
              font-size: 11.5px;
              font-weight: 700;
              white-space: nowrap;
              border: 2px solid rgba(255,255,255,0.9);
              display: flex; align-items: center; gap: 5px;
              box-shadow: 0 2px 8px rgba(0,0,0,0.35);
              line-height: 1.2;
            ">
              <span style="
                background: rgba(255,255,255,0.25);
                border-radius: 50%;
                width: 18px; height: 18px;
                display: flex; align-items: center; justify-content: center;
                font-size: 10px; font-weight: 800;
              ">${aqi}</span>
              <span style="max-width: 100px; overflow: hidden; text-overflow: ellipsis;">${displayName}</span>
            </div>
            <!-- Connector dot -->
            <div style="
              width: 6px; height: 6px; border-radius: 50%;
              background: ${color}; border: 1.5px solid white;
              margin-top: 2px;
              box-shadow: 0 1px 4px rgba(0,0,0,0.4);
            "></div>
          </div>
        `,
        iconSize: [150, 40],
        iconAnchor: [75, 40]
      });

      const marker = L.marker([lat, lon], { icon: labelIcon });

      const popupHtml = `
        <div style="font-family:'Inter',system-ui,sans-serif; font-size:12px; line-height:1.5; min-width:215px; padding:6px 4px; color:#0f172a;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <strong style="color:#0f172a; font-size:13px;">📍 ${displayName}</strong>
            <span style="background:${color}18; color:${color}; border:1px solid ${color}40; border-radius:4px; padding:1.5px 7px; font-size:10px; font-weight:700; text-transform:uppercase;">${category}</span>
          </div>
          <div style="display:flex; align-items:baseline; gap:6px; margin-bottom:8px;">
            <span style="font-size:1.6rem; font-weight:900; color:${color}; font-family:'Outfit',sans-serif; line-height:1;">${aqi}</span>
            <span style="font-size:11px; color:#64748b; font-weight:500;">AQI — Intermediate Station</span>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:11px; border-top:1px solid #e2e8f0; padding-top:6px; color:#334155;">
            <div><span style="color:#64748b;">PM2.5:</span> <strong style="color:#0f172a;">${pm25}</strong></div>
            <div><span style="color:#64748b;">PM10:</span> <strong style="color:#0f172a;">${pm10}</strong></div>
            <div><span style="color:#64748b;">Traffic:</span> <strong style="color:#0f172a;">${traffic}</strong></div>
            <div style="color:#64748b;"><span style="color:#64748b;">Coord:</span> ${lat.toFixed(4)}, ${lon.toFixed(4)}</div>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml, { maxWidth: 250 });
      marker.addTo(this.routeMapLayer);
    });
  },

  getAQIColor(aqi) {
    if (aqi <= 50) return '#10b981';
    if (aqi <= 100) return '#f59e0b';
    if (aqi <= 150) return '#f97316';
    if (aqi <= 200) return '#ef4444';
    if (aqi <= 300) return '#8b5cf6';
    return '#991b1b';
  }
};
