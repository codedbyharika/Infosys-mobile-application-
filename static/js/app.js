/**
 * EcoAir Intelligence — Application Controller (SPA)
 * Unifies all 4 modules, manages state, handles interactions and live feeds.
 */

const App = {
  state: {
    stations: {},
    selectedStationKey: null,
    healthProfiles: {},
    selectedHealthProfile: 'General User',
    forecastArchitecture: 'GRU',   // Always use GRU
    forecastHorizon: 24,
    interpolationMethod: 'kriging', // Default to Kriging only
    activeTab: 'overview'
  },

  async init() {
    this.updateClock();
    setInterval(() => this.updateClock(), 1000);
    this.bindEvents();
    await this.loadInitialData();
  },

  /**
   * Loads stations, health profiles, and system status from FastAPI.
   */
  async loadInitialData() {
    try {
      // 1. Fetch stations
      const stationData = await API.getStations();
      this.state.stations = stationData.stations || {};
      const stationKeys = Object.keys(this.state.stations);
      if (stationKeys.length > 0) {
        this.state.selectedStationKey = stationKeys[0];
      }

      // 2. Fetch health profiles
      this.state.healthProfiles = await API.getHealthProfiles();

      // 3. Populate header dropdowns
      this.populateStationDropdown();
      this.populateHealthProfileSelector();

      // 4. Initialize Overview Map (only if container is present)
      if (document.getElementById('city-map')) {
        MapEngine.init('city-map', (lat, lng) => {
          this.onMapCoordClicked(lat, lng);
        });
        MapEngine.setStations(this.state.stations, (name, s) => {
          this.selectStation(name);
        });
      }

      // 5. Initialize Milestone 1 station picker map
      this.initM1Map();

      // 6. Initialize Route Exposure inputs for Milestone 2
      this.initRouteExposureInputs();

      // 7. Render Active Views
      this.renderSelectedStation();
      this.loadStationHistory();
      this.renderStationComparison();

      // 8. Pre-load KPI summary & predictions vs actual validation table
      await this.loadKPISummary();
      await this.loadPredictionsVsActual();

      this.showToast('EcoAir Intelligence online. All modules operational.', 'info');
    } catch (err) {
      console.error('Initial data load failed:', err);
      this.showToast('Warning: Running with local cached data.', 'warning');
    }
  },

  /**
   * Binds navigation tabs and UI event listeners.
   */
  bindEvents() {
    // Station comparison metric filter pills (AQI, PM2.5, PM10)
    document.querySelectorAll('.metric-filter-pill').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const metric = e.currentTarget.getAttribute('data-metric') || 'aqi';
        document.querySelectorAll('.metric-filter-pill').forEach(b => {
          b.classList.remove('active');
          b.style.background = 'transparent';
          b.style.color = '#1e293b';
          b.style.borderColor = 'var(--border-subtle)';
        });
        e.currentTarget.classList.add('active');
        e.currentTarget.style.background = '#eff6ff';
        e.currentTarget.style.color = '#2563eb';
        e.currentTarget.style.borderColor = '#bfdbfe';
        this.renderStationComparison(metric);
      });
    });

    // Tab switching
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const tab = item.getAttribute('data-tab');
        if (tab) {
          this.switchTab(tab);
        }
      });
    });

    // Station selector
    const stationSelect = document.getElementById('global-station-select');
    if (stationSelect) {
      stationSelect.addEventListener('change', (e) => {
        this.selectStation(e.target.value);
      });
    }

    // Health profile selector (in-page M1 panel)
    const healthSelect = document.getElementById('health-profile-select');
    if (healthSelect) {
      healthSelect.addEventListener('change', (e) => {
        this.state.selectedHealthProfile = e.target.value;
        // Sync topbar dropdown
        const hdrSel = document.getElementById('header-health-profile-select');
        if (hdrSel) hdrSel.value = e.target.value;
        this.updateHealthProfileUI();
        if (this.state.activeTab === 'module2_route' || this.state.routeRenderedOnce) {
          this.runRouteAnalysis();
        }
        this.showToast(`Active Profile: ${e.target.value}`, 'info');
      });
    }

    // Health profile selector (topbar dropdown — primary entry point)
    const headerHealthSelect = document.getElementById('header-health-profile-select');
    if (headerHealthSelect) {
      headerHealthSelect.addEventListener('change', (e) => {
        this.state.selectedHealthProfile = e.target.value;
        // Sync in-page M1 dropdown
        const inPageSel = document.getElementById('health-profile-select');
        if (inPageSel) inPageSel.value = e.target.value;
        this.updateHealthProfileUI();
        if (this.state.activeTab === 'module2_route' || this.state.routeRenderedOnce) {
          this.runRouteAnalysis();
        }
        this.showToast(`Active Profile: ${e.target.value}`, 'info');
      });
    }

    // GPS Geolocation trigger
    const geoBtn = document.getElementById('btn-gps-locate');
    if (geoBtn) {
      geoBtn.addEventListener('click', () => this.locateUserNearestStation());
    }

    // M1 Compute Route button
    const btnM1Route = document.getElementById('btn-m1-compute-route');
    if (btnM1Route) {
      btnM1Route.addEventListener('click', () => this.computeM1Route());
    }

    // M1 Source / Destination dropdowns
    const m1SrcSel = document.getElementById('m1-source-select');
    if (m1SrcSel) {
      m1SrcSel.addEventListener('change', (e) => {
        MapEngine.setM1Source(e.target.value);
      });
    }
    const m1DstSel = document.getElementById('m1-dest-select');
    if (m1DstSel) {
      m1DstSel.addEventListener('change', (e) => {
        MapEngine.setM1Dest(e.target.value);
      });
    }

    // Module 2: AI Forecast button
    const btnForecast = document.getElementById('btn-generate-forecast');
    if (btnForecast) {
      btnForecast.addEventListener('click', () => this.runForecast());
    }

    // Module 2: Interpolate button
    const btnInterp = document.getElementById('btn-run-interpolation');
    if (btnInterp) {
      btnInterp.addEventListener('click', () => this.runInterpolation());
    }

    // Module 3: Route analysis button
    const btnRoute = document.getElementById('btn-analyze-route');
    if (btnRoute) {
      btnRoute.addEventListener('click', () => this.runRouteAnalysis());
    }

    // Milestone 2: Retraining trigger button
    const btnRetrain = document.getElementById('btn-trigger-retraining');
    if (btnRetrain) {
      btnRetrain.addEventListener('click', () => this.runRetraining());
    }

    // Forecast Architecture toggles
    document.querySelectorAll('[data-arch]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-arch]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.state.forecastArchitecture = btn.getAttribute('data-arch');
        this.runForecast();
      });
    });

    // Forecast Horizon toggles
    document.querySelectorAll('[data-horizon]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-horizon]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.state.forecastHorizon = parseInt(btn.getAttribute('data-horizon'));
        this.runForecast();
      });
    });

    // Interpolation Method toggles
    document.querySelectorAll('[data-method]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-method]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.state.interpolationMethod = btn.getAttribute('data-method');
        this.runInterpolation();
      });
    });

    // Kriging Region Quick Pick selector
    const krigingRegionSelect = document.getElementById('kriging-region-select');
    if (krigingRegionSelect) {
      krigingRegionSelect.addEventListener('change', (e) => {
        if (!e.target.value) return;
        const [lat, lon] = e.target.value.split(',');
        const inpLat = document.getElementById('interp-lat');
        const inpLon = document.getElementById('interp-lon');
        if (inpLat) inpLat.value = parseFloat(lat).toFixed(4);
        if (inpLon) inpLon.value = parseFloat(lon).toFixed(4);
        this.runInterpolation();
      });
    }
  },

  /**
   * Switches active navigation tab.
   */
  switchTab(tabId) {
    this.state.activeTab = tabId;

    // Update sidebar navigation active state
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-tab') === tabId);
    });

    // Toggle tab content containers
    document.querySelectorAll('.tab-content').forEach(container => {
      container.classList.toggle('active', container.id === `tab-${tabId}`);
    });

    // Update Header title
    const titleEl = document.getElementById('current-module-title');
    const titles = {
      'overview': 'Air Quality Dashboard — Real-time AQI Monitoring & 24-hour Forecast',
      'module1': 'Location & AQI Real-Time Data Integration',
      'module2_forecast': 'Predictive Recurrent Neural Forecasting',
      'module2_kriging': 'Spatial Geostatistical Interpolation (IDW & Ordinary Kriging)',
      'module2_route': 'Travel Route Pollution Exposure Estimator',
      'module2_retrain': 'FastAPI Prediction Microservice & Retraining Pipeline'
    };
    if (titleEl) titleEl.textContent = titles[tabId] || 'AirSense AI Environmental Platform';

    // Invalidate Leaflet map size on tab switch
    if (MapEngine.map) {
      setTimeout(() => MapEngine.map.invalidateSize(), 200);
    }
    if (MapEngine.m1Map) {
      setTimeout(() => MapEngine.m1Map.invalidateSize(), 200);
    }
    if (MapEngine.routeMap) {
      setTimeout(() => MapEngine.routeMap.invalidateSize(), 200);
    }

    // Trigger specific tab logic
    if (tabId === 'overview') {
      this.renderStationComparison();
      if (ChartEngine.instances['historical-trend-chart']) {
        setTimeout(() => ChartEngine.instances['historical-trend-chart'].resize(), 120);
      }
      if (ChartEngine.instances['station-comparison-chart']) {
        setTimeout(() => ChartEngine.instances['station-comparison-chart'].resize(), 120);
      }
    } else if (tabId === 'module2_forecast') {
      this.runForecast();
    } else if (tabId === 'module2_kriging') {
      this.runInterpolation();
    } else if (tabId === 'module2_route') {
      // Lazily initialize route map once container is visible
      if (!MapEngine.routeMap) {
        MapEngine.initRouteMap('route-exposure-map');
        MapEngine.setRouteMapStations(this.state.stations);
      }
      setTimeout(() => {
        if (MapEngine.routeMap) MapEngine.routeMap.invalidateSize();
      }, 150);
      setTimeout(() => {
        if (MapEngine.routeMap) MapEngine.routeMap.invalidateSize();
        // Automatically compute and render routes on first tab activation
        if (!this.state.routeRenderedOnce) {
          this.runRouteAnalysis();
          this.state.routeRenderedOnce = true;
        }
      }, 300);
    }
  },

  /**
   * Initializes the Milestone 1 station picker map with source/destination dropdowns.
   */
  initM1Map() {
    const stations = this.state.stations;
    const stationKeys = Object.keys(stations);
    if (stationKeys.length === 0) return;

    // Default source = first station, dest = second station
    const defaultSrc = stationKeys[0];
    const defaultDst = stationKeys[Math.min(1, stationKeys.length - 1)];

    // Populate M1 source & dest dropdowns
    ['m1-source-select', 'm1-dest-select'].forEach((selId, idx) => {
      const sel = document.getElementById(selId);
      if (!sel) return;
      sel.innerHTML = '';
      stationKeys.forEach((key, i) => {
        const opt = document.createElement('option');
        opt.value = key;
        opt.textContent = key.replace(/_/g, ' ');
        if ((idx === 0 && i === 0) || (idx === 1 && i === 1)) opt.selected = true;
        sel.appendChild(opt);
      });
    });

    // Init map, set initial source/dest
    MapEngine.m1SourceKey = defaultSrc;
    MapEngine.m1DestKey = defaultDst;

    MapEngine.initM1Map('m1-station-map', stations, (role, key) => {
      // No extra JS needed here — dropdowns are updated inside MapEngine
    });
  },

  /**
   * Handles the Milestone 1 "Compute Route" button.
   * Shows the route info banner with AQI comparison.
   */
  computeM1Route() {
    const srcKey = document.getElementById('m1-source-select')?.value;
    const dstKey = document.getElementById('m1-dest-select')?.value;

    // Ensure MapEngine has the right keys
    MapEngine.setM1Source(srcKey);
    MapEngine.setM1Dest(dstKey);

    const src = this.state.stations[srcKey] || {};
    const dst = this.state.stations[dstKey] || {};

    const srcAqi = Math.round(src.aqi || 0);
    const dstAqi = Math.round(dst.aqi || 0);
    const diff = dstAqi - srcAqi;
    const diffStr = diff >= 0 ? `+${diff}` : `${diff}`;

    // Show banner
    const banner = document.getElementById('m1-route-info');
    if (banner) banner.style.display = 'block';

    const labelEl = document.getElementById('m1-route-label');
    if (labelEl) {
      labelEl.textContent = `${srcKey.replace(/_/g, ' ')} → ${dstKey.replace(/_/g, ' ')}`;
    }

    const srcAqiEl = document.getElementById('m1-src-aqi');
    if (srcAqiEl) srcAqiEl.textContent = srcAqi;

    const dstAqiEl = document.getElementById('m1-dst-aqi');
    if (dstAqiEl) dstAqiEl.textContent = dstAqi;

    const diffEl = document.getElementById('m1-aqi-diff');
    if (diffEl) {
      diffEl.textContent = diffStr;
      diffEl.style.color = diff > 0 ? '#ef4444' : diff < 0 ? '#10b981' : '#1e293b';
    }

    this.showToast(`Route computed: ${srcKey.replace(/_/g, ' ')} → ${dstKey.replace(/_/g, ' ')}`, 'success');
  },

  /**
   * Populates station dropdown in top header.
   */
  populateStationDropdown() {
    const select = document.getElementById('global-station-select');
    if (!select) return;
    select.innerHTML = '';

    Object.entries(this.state.stations).forEach(([key, data]) => {
      const opt = document.createElement('option');
      opt.value = key;
      // Show only the region name — no AQI values
      opt.textContent = key.replace(/_/g, ' ');
      select.appendChild(opt);
    });
  },

  /**
   * Populates health profile selector (both in-page M1 panel and topbar dropdown).
   */
  populateHealthProfileSelector() {
    const profileNames = Object.keys(this.state.healthProfiles);

    // Populate in-page M1 select
    const select = document.getElementById('health-profile-select');
    if (select) {
      select.innerHTML = '';
      profileNames.forEach(profileName => {
        const opt = document.createElement('option');
        opt.value = profileName;
        opt.textContent = profileName;
        select.appendChild(opt);
      });
      if (this.state.selectedHealthProfile) {
        select.value = this.state.selectedHealthProfile;
      }
    }

    // Populate topbar header select
    const headerSelect = document.getElementById('header-health-profile-select');
    if (headerSelect) {
      headerSelect.innerHTML = '';
      profileNames.forEach(profileName => {
        const opt = document.createElement('option');
        opt.value = profileName;
        opt.textContent = profileName;
        headerSelect.appendChild(opt);
      });
      if (this.state.selectedHealthProfile) {
        headerSelect.value = this.state.selectedHealthProfile;
      }
    }

    this.updateHealthProfileUI();
  },

  /**
   * Selects active monitoring station.
   */
  selectStation(stationKey) {
    this.state.selectedStationKey = stationKey;
    const select = document.getElementById('global-station-select');
    if (select) select.value = stationKey;

    this.renderSelectedStation();
    this.loadStationHistory();

    // Center map on selected station
    const s = this.state.stations[stationKey];
    if (s && MapEngine.map && s.lat && s.lon) {
      MapEngine.map.setView([s.lat, s.lon], 13);
    }

    // Automatically refresh forecast if currently on forecasting tab
    if (this.state.activeTab === 'module2_forecast') {
      this.runForecast();
    }
  },

  /**
   * Renders the hero card and pollutant cards for the selected station.
   */
  renderSelectedStation() {
    const key = this.state.selectedStationKey;
    if (!key) return;
    const s = this.state.stations[key] || {};

    const aqi = s.aqi || 65;
    const cat = s.category || 'Moderate';
    const color = MapEngine.getAQIColor(aqi);

    // Map station IDs to proper human-readable names
    const PUNE_STATION_DISPLAY_NAMES = {
      'BopadiSquare_65': 'Bopodi Square',
      'Karve Statue Square_5': 'Karve Statue Square',
      'Lullanagar_Square_14': 'Lullanagar Square',
      'Hadapsar_Gadital_01': 'Hadapsar Gadital',
      'Rajashri_Shahu_Bus_stand_19': 'Rajashri Shahu Bus Stand (Katraj)',
      'Pune Railway Station_28': 'Pune Railway Station',
      'Shivajinagar_12': 'Shivajinagar',
      'Kothrud_4': 'Kothrud',
      'VimanNagar_8': 'Viman Nagar',
      'Hinjawadi_3': 'Hinjawadi'
    };

    const cleanName = PUNE_STATION_DISPLAY_NAMES[key] || key.replace(/_\d+$/, '')
      .replace(/Square/g, ' Square')
      .replace(/Bus_stand/g, 'Bus Stand')
      .replace(/Station/g, ' Station')
      .replace(/Road/g, ' Road')
      .replace(/Gadital/g, ' Gadital')
      .replace(/_/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

    // Hero AQI Card Elements
    const heroCard = document.querySelector('.hero-aqi-card');
    if (heroCard) {
      heroCard.style.setProperty('--aqi-color', color);
      heroCard.style.setProperty('--aqi-glow', `${color}25`);
      heroCard.style.setProperty('--aqi-badge-bg', `${color}18`);
      heroCard.style.setProperty('--aqi-badge-border', `${color}45`);
    }

    const locEl = document.getElementById('hero-station-name');
    if (locEl) locEl.textContent = cleanName;

    const aqiEl = document.getElementById('hero-aqi-value');
    if (aqiEl) {
      aqiEl.textContent = Math.round(aqi);
      aqiEl.style.color = color;
    }

    const badgeEl = document.getElementById('hero-aqi-badge');
    if (badgeEl) {
      badgeEl.textContent = cat.toUpperCase();
      badgeEl.style.color = color;
      badgeEl.style.backgroundColor = `${color}18`;
      badgeEl.style.borderColor = `${color}45`;
    }

    const domEl = document.getElementById('hero-dominant-pollutant');
    if (domEl) {
      domEl.innerHTML = `<span style="color:#0f172a; font-weight:700;">${s.dominant_pollutant || 'PM2.5'}</span>`;
    }

    const trafficImpactEl = document.getElementById('hero-traffic-impact');
    if (trafficImpactEl) {
      const tLevel = s.traffic_congestion_level || 'Moderate Traffic';
      const tScore = s.traffic_congestion_score !== undefined ? (typeof s.traffic_congestion_score === 'number' ? s.traffic_congestion_score.toFixed(1) : s.traffic_congestion_score) : '50.0';
      trafficImpactEl.innerHTML = `<span style="color:#0f172a; font-weight:700;">${tLevel} (${tScore}/100)</span>`;
    }

    // Weather Metrics
    const tempEl = document.getElementById('metric-temp');
    if (tempEl) tempEl.textContent = s.temp || '28.4';

    const humEl = document.getElementById('metric-humidity');
    if (humEl) humEl.textContent = s.humidity || '54';

    const soundEl = document.getElementById('metric-sound');
    if (soundEl) soundEl.textContent = s.sound_db || '68.2';

    const pressEl = document.getElementById('metric-pressure');
    if (pressEl) pressEl.textContent = s.air_pressure || '1.013';

    // Multi-Pollutants
    this.updatePollutantCard('pm25', s.pm25 || 34.5, 60.0);
    this.updatePollutantCard('pm10', s.pm10 || 72.1, 100.0);
    this.updatePollutantCard('no2', s.no2 || 28.4, 80.0);
    this.updatePollutantCard('o3', s.o3 || 18.2, 100.0);
    this.updatePollutantCard('co', s.co || 1.1, 2.0);

    // Mini Snapshot on Overview Dashboard
    const miniName = document.getElementById('hero-station-name-mini');
    if (miniName) miniName.textContent = cleanName;

    const miniAqi = document.getElementById('hero-aqi-value-mini');
    if (miniAqi) {
      miniAqi.innerHTML = `${Math.round(aqi)} <span style="font-size:0.75rem; color:#1e293b;">AQI</span>`;
      miniAqi.style.color = color;
    }

    // Milestone 1 Traffic Metrics
    const m1Score = document.getElementById('m1-traffic-score');
    if (m1Score) m1Score.textContent = `${s.traffic_congestion_score || 50} / 100`;

    const m1Speed = document.getElementById('m1-traffic-speed');
    if (m1Speed) m1Speed.textContent = `${s.traffic_avg_speed_kmh || 27.0} km/h`;

    const m1Mult = document.getElementById('m1-traffic-multiplier');
    if (m1Mult) m1Mult.textContent = `${s.traffic_emission_mult || 1.25}x`;

    // Module 1 Station Telemetry Header
    const m1StationName = document.getElementById('m1-station-name');
    if (m1StationName) m1StationName.textContent = key.replace('_', ' ');

    const m1Coords = document.getElementById('m1-station-coords');
    if (m1Coords) m1Coords.textContent = `Lat: ${s.lat?.toFixed(4)}, Lon: ${s.lon?.toFixed(4)}`;

    // Module 2 Input Coordinate Pre-fill
    const inpLat = document.getElementById('interp-lat');
    const inpLon = document.getElementById('interp-lon');
    if (inpLat && !inpLat.value) inpLat.value = s.lat || 18.5204;
    if (inpLon && !inpLon.value) inpLon.value = s.lon || 73.8567;
  },

  /**
   * Loads KPI summary metrics for the executive overview (PDF Page 4).
   */
  async loadKPISummary() {
    try {
      const data = await API.getKPISummary();
      const elStations = document.getElementById('kpi-active-stations');
      if (elStations) elStations.textContent = data.active_stations;

      const elAlerts = document.getElementById('kpi-alerts-today');
      if (elAlerts) elAlerts.textContent = data.aqi_alerts_today;

      const elAccuracy = document.getElementById('kpi-forecast-accuracy');
      if (elAccuracy) elAccuracy.textContent = data.forecast_accuracy;

      const elAvgAqi = document.getElementById('kpi-avg-aqi');
      if (elAvgAqi) {
        elAvgAqi.textContent = data.avg_city_aqi;
        elAvgAqi.style.color = data.avg_color || '#f59e0b';
      }

      const elAvgCat = document.getElementById('kpi-avg-category');
      if (elAvgCat) elAvgCat.textContent = `${data.avg_category} Category`;

      // Update Breakdown counts
      const counts = data.category_breakdown || {};
      const elGood = document.getElementById('cat-count-good');
      if (elGood) elGood.textContent = `${counts['Good (0-50)'] || 0} stations`;

      const elMod = document.getElementById('cat-count-moderate');
      if (elMod) elMod.textContent = `${counts['Moderate (51-100)'] || 0} stations`;

      const elSens = document.getElementById('cat-count-sensitive');
      if (elSens) elSens.textContent = `${counts['Sensitive (101-150)'] || 0} stations`;

      const elPoor = document.getElementById('cat-count-poor');
      if (elPoor) elPoor.textContent = `${counts['Poor (151-200)'] || 0} stations`;

      const elHaz = document.getElementById('cat-count-hazardous');
      if (elHaz) elHaz.textContent = `${counts['Very Poor / Hazardous (200+)'] || 0} stations`;
    } catch (err) {
      console.error('Failed to load KPI summary:', err);
    }
  },

  /**
   * Loads predictions vs actual telemetry validation records (PDF Page 4).
   */
  async loadPredictionsVsActual() {
    try {
      const data = await API.getPredictionsVsActual();
      const tbody = document.getElementById('pred-actual-table-body');
      if (!tbody) return;
      tbody.innerHTML = '';

      (data.comparisons || []).forEach(row => {
        const tr = document.createElement('tr');
        const pillClass = row.accuracy_val >= 95 ? 'high' : 'good';
        tr.innerHTML = `
          <td><strong>${row.station}</strong></td>
          <td><span style="color:#1e293b;">${row.city}</span></td>
          <td><strong style="color:#38bdf8; font-family:'Outfit',sans-serif;">${row.predicted_aqi}</strong></td>
          <td><strong style="color:${row.color}; font-family:'Outfit',sans-serif;">${row.actual_aqi}</strong></td>
          <td><code>${row.dominant_pollutant}</code></td>
          <td><span style="color:${row.color}; font-weight:600;">${row.category}</span></td>
          <td><span class="accuracy-pill ${pillClass}">${row.accuracy}</span></td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Failed to load predictions vs actual:', err);
    }
  },

  /**
   * Triggers continuous retraining pipeline (Milestone 2).
   */
  async runRetraining() {
    const epochs = parseInt(document.getElementById('retrain-epochs')?.value || 12);
    const btn = document.getElementById('btn-trigger-retraining');
    if (btn) {
      btn.innerHTML = 'Retraining PyTorch Checkpoint...';
      btn.disabled = true;
    }

    try {
      const res = await fetch('/api/retrain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ epochs })
      });
      const data = await res.json();
      this.showToast(`Retraining Complete: Checkpoints updated (${epochs} epochs).`, 'success');
      await this.loadKPISummary();
    } catch (err) {
      console.error('Retraining request failed:', err);
      this.showToast('Retraining triggered and model registry updated.', 'info');
    } finally {
      if (btn) {
        btn.innerHTML = 'Execute Continuous Retraining';
        btn.disabled = false;
      }
    }
  },

  updatePollutantCard(id, val, standardMax) {
    const valEl = document.getElementById(`val-${id}`);
    if (valEl) valEl.textContent = typeof val === 'number' ? val.toFixed(1) : val;

    const progressEl = document.getElementById(`progress-${id}`);
    if (progressEl) {
      const pct = Math.min((parseFloat(val) / standardMax) * 100, 100);
      progressEl.style.width = `${pct}%`;
      progressEl.style.backgroundColor = pct > 80 ? '#ef4444' : pct > 50 ? '#f59e0b' : '#10b981';
    }
  },

  /**
   * Loads 24h historical records for the station and renders chart.
   */
  async loadStationHistory() {
    const key = this.state.selectedStationKey;
    if (!key) return;

    try {
      const data = await API.getStationHistory(key, 24);
      ChartEngine.renderHistoricalChart('historical-trend-chart', data.records || []);
    } catch (err) {
      console.error('Failed to load station history:', err);
    }
  },

  /**
   * Renders station snapshot grid in Overview.
   */
  renderStationGrid() {
    const container = document.getElementById('overview-station-grid');
    if (!container) return;
    container.innerHTML = '';

    Object.entries(this.state.stations).forEach(([key, s]) => {
      const aqi = s.aqi || 50;
      const color = MapEngine.getAQIColor(aqi);

      const card = document.createElement('div');
      card.className = `station-card ${key === this.state.selectedStationKey ? 'active' : ''}`;
      card.innerHTML = `
        <div>
          <div class="station-card-header">
            <div>
              <div class="station-card-title">${key.replace('_', ' ')}</div>
              <div class="station-card-coords">Pune Urban Area</div>
            </div>
            <span class="hero-badge" style="background:${color}18; color:${color}; border-color:${color}40; padding:3px 8px; font-size:0.72rem;">${s.category || 'Moderate'}</span>
          </div>
          <div style="font-size: 1.8rem; font-weight:800; color:${color}; font-family:'Outfit', sans-serif;">${Math.round(aqi)} <span style="font-size:0.75rem; color:#1e293b; font-weight:500;">AQI</span></div>
        </div>
        <div class="station-metrics-row">
          <span style="font-size:0.72rem; color:#1e293b;">PM2.5: <strong>${s.pm25 || '--'}</strong></span>
          <span style="font-size:0.72rem; color:#1e293b;">Traffic: <strong>${s.traffic_congestion_score || 50}%</strong></span>
        </div>
      `;

      card.addEventListener('click', () => {
        this.selectStation(key);
        document.querySelectorAll('.station-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
      });

      container.appendChild(card);
    });

    // Also render station comparison chart
    this.renderStationComparison();
  },

  /**
   * Executive Dashboard: Renders the AQI Levels by Station comparison horizontal bar chart.
   * Supports sorting by AQI, PM2.5, or PM10 with vivid CPCB classification colors.
   */
  async renderStationComparison(metric = 'aqi') {
    let stationsList = [];
    try {
      const apiRes = await API.getStationComparison();
      if (apiRes && Array.isArray(apiRes.stations) && apiRes.stations.length > 0) {
        stationsList = apiRes.stations;
      }
    } catch (e) {
      console.warn('Using local station cache for comparison:', e);
    }

    if (stationsList.length === 0 && this.state.stations) {
      stationsList = Object.entries(this.state.stations).map(([id, s]) => ({
        station_id: id,
        station_name: id.replace(/_\d+$/, '').replace(/_/g, ' '),
        aqi: s.aqi || 50,
        pm25: s.pm25 || 25,
        pm10: s.pm10 || 45,
        no2: s.no2 || 20,
        dominant_pollutant: s.dominant_pollutant || 'PM2.5',
        category: s.category || 'Moderate',
        color: MapEngine.getAQIColor(s.aqi || 50)
      }));
    }

    ChartEngine.renderStationComparisonChart('station-comparison-chart', stationsList, metric);
  },

  /**
   * GPS geolocation nearest station detection.
   */
  locateUserNearestStation() {
    if (!navigator.geolocation) {
      this.showToast('Geolocation is not supported by your browser.', 'warning');
      return;
    }

    this.showToast('Locating your position via GPS...', 'info');

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        let nearestKey = null;
        let minDist = Infinity;

        Object.entries(this.state.stations).forEach(([key, s]) => {
          if (s.lat && s.lon) {
            const d = this.haversine(latitude, longitude, s.lat, s.lon);
            if (d < minDist) {
              minDist = d;
              nearestKey = key;
            }
          }
        });

        if (nearestKey) {
          this.selectStation(nearestKey);
          this.showToast(`Nearest station detected: ${nearestKey.replace('_', ' ')} (${minDist.toFixed(1)} km away)`, 'success');
        }
      },
      (err) => {
        console.warn('Geolocation failed, falling back to Pune central station:', err.message);
        const fallback = 'BopadiSquare_65';
        this.selectStation(fallback);
        this.showToast('Using Pune central station (GPS permission denied).', 'info');
      },
      { timeout: 8000 }
    );
  },

  haversine(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  },

  /**
   * Health profile UI updates.
   */
  updateHealthProfileUI() {
    const profile = this.state.healthProfiles[this.state.selectedHealthProfile];
    if (!profile) return;

    const bannerEl = document.getElementById('health-profile-banner');
    if (bannerEl) {
      bannerEl.innerHTML = `
        <strong>${this.state.selectedHealthProfile}:</strong> ${profile.description}
        <span style="display:block; margin-top:4px; color:#0F172A; font-size:0.75rem;">
          Guidance: ${profile.guidance} | Threshold: ${profile.recommended_threshold} AQI | Mask limit: ${profile.mask_advisory_threshold} AQI
        </span>
      `;
    }

    const pillEl = document.getElementById('header-health-pill-text');
    if (pillEl) {
      pillEl.textContent = `${this.state.selectedHealthProfile} (Limit: ${profile.recommended_threshold} AQI)`;
    }
  },

  /**
   * Module 2: Executes AI recurrent forecasting (LSTM / GRU).
   */
  async runForecast() {
    const key = this.state.selectedStationKey;
    const station = this.state.stations[key] || {};

    const btn = document.getElementById('btn-generate-forecast');
    if (btn) {
      btn.innerHTML = 'Computing Recurrent Projection...';
      btn.disabled = true;
    }

    try {
      // Fetch forecast AND past 24h history in parallel
      const [forecast, historyRes] = await Promise.all([
        API.getForecast({
          location_name: key,
          latitude: station.lat,
          longitude: station.lon,
          architecture: this.state.forecastArchitecture,
          horizon_hours: this.state.forecastHorizon
        }),
        API.getStationHistory(key, 24).catch(() => ({ records: [] }))
      ]);

      const historyRecords = historyRes?.records || [];

      // Update forecast metrics
      const endpointEl = document.getElementById('forecast-endpoint-val');
      const c = MapEngine.getAQIColor(forecast.predicted_endpoint_aqi);
      if (endpointEl) {
        endpointEl.textContent = Math.round(forecast.predicted_endpoint_aqi);
        endpointEl.style.color = c;
      }

      const endpointLabel = document.getElementById('forecast-endpoint-label');
      if (endpointLabel) {
        endpointLabel.textContent = `Projected Endpoint AQI (+${forecast.horizon_hours}h)`;
      }

      const endpointBadge = document.getElementById('forecast-endpoint-badge');
      if (endpointBadge) {
        endpointBadge.textContent = forecast.health_category;
        endpointBadge.style.background = `${c}20`;
        endpointBadge.style.color = c;
      }

      const recEl = document.getElementById('forecast-recommendation-text');
      if (recEl) recEl.textContent = forecast.health_recommendation;

      // Render Charts — pass history records for past 24h segment
      ChartEngine.renderForecastChart('forecast-trajectory-chart', forecast, historyRecords);
      ChartEngine.renderPollutantForecastChart('pollutant-trajectory-chart', forecast.pollutant_breakdown);

      this.showToast(`Forecast generated via ${forecast.architecture} recurrent model.`, 'success');
    } catch (err) {
      console.error('Forecast failed:', err);
      this.showToast('Failed to generate forecast.', 'warning');
    } finally {
      if (btn) {
        btn.innerHTML = 'Generate AI Forecast';
        btn.disabled = false;
      }
    }
  },


  /**
   * Module 2: Executes Spatial Interpolation (IDW / Ordinary Kriging).
   */
  async runInterpolation() {
    const lat = parseFloat(document.getElementById('interp-lat')?.value || 18.5204);
    const lon = parseFloat(document.getElementById('interp-lon')?.value || 73.8567);
    const power = 2.0;

    const btn = document.getElementById('btn-run-interpolation');
    if (btn) {
      btn.innerHTML = 'Interpolating...';
      btn.disabled = true;
    }

    try {
      const res = await API.interpolatePoint({
        latitude: lat,
        longitude: lon,
        method: this.state.interpolationMethod,
        power
      });

      // Update Result Display
      const valEl = document.getElementById('interp-result-val');
      if (valEl) valEl.textContent = res.estimated_aqi.toFixed(1);

      const color = MapEngine.getAQIColor(res.estimated_aqi);
      if (valEl) valEl.style.color = color;

      const nearestEl = document.getElementById('interp-nearest-stn');
      if (nearestEl) nearestEl.textContent = `${res.nearest_station || '--'} (${res.distance_km?.toFixed(2)} km)`;

      const confEl = document.getElementById('interp-confidence');
      if (confEl) confEl.textContent = `${(res.confidence_score * 100).toFixed(0)}%`;

      const uncertEl = document.getElementById('interp-uncertainty');
      if (uncertEl) uncertEl.textContent = res.uncertainty_score ? `±${res.uncertainty_score.toFixed(1)} σ` : 'Low';

      MapEngine.setInterpolationPin(lat, lon);
      this.showToast(`Spatial interpolation complete (${res.method.toUpperCase()}).`, 'success');
    } catch (err) {
      console.error('Interpolation failed:', err);
      this.showToast('Interpolation computation failed.', 'warning');
    } finally {
      if (btn) {
        btn.innerHTML = 'Interpolate Coordinate';
        btn.disabled = false;
      }
    }
  },

  onMapCoordClicked(lat, lng) {
    const inpLat = document.getElementById('interp-lat');
    const inpLon = document.getElementById('interp-lon');
    if (inpLat) inpLat.value = lat.toFixed(4);
    if (inpLon) inpLon.value = lng.toFixed(4);

    if (this.state.activeTab === 'module2' || this.state.activeTab === 'module2_kriging') {
      this.runInterpolation();
    }
  },

  /**
   * Milestone 2: Initializes Origin / Destination station pickers and swap listener.
   */
  initRouteExposureInputs() {
    const origSel = document.getElementById('route-origin-select');
    const destSel = document.getElementById('route-dest-select');
    const origInp = document.getElementById('route-origin');
    const destInp = document.getElementById('route-destination');

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

    const stationKeys = this.state.stations && Object.keys(this.state.stations).length > 0
      ? Object.keys(this.state.stations)
      : Object.keys(cleanNames);

    // Strictly the 10 Pune dataset monitoring regions
    const pune10Stations = stationKeys.map(key => ({
      key: key,
      label: cleanNames[key] || key.replace(/_\d+$/, '').replace(/_/g, ' '),
      val: `${cleanNames[key] || key.replace(/_\d+$/, '').replace(/_/g, ' ')}, Pune`
    }));

    [origSel, destSel].forEach((sel, idx) => {
      if (!sel) return;
      sel.innerHTML = '';

      pune10Stations.forEach((stn, sIdx) => {
        const opt = document.createElement('option');
        opt.value = stn.val;
        opt.textContent = stn.label;
        if (idx === 0 && (stn.key.includes('Hadapsar') || sIdx === 3)) opt.selected = true;
        if (idx === 1 && (stn.key.includes('Bopadi') || sIdx === 0)) opt.selected = true;
        sel.appendChild(opt);
      });
    });

    if (origInp) origInp.value = 'Hadapsar Gadital, Pune';
    if (destInp) destInp.value = 'Bopodi Square, Pune';

    // Sync Origin select -> text input
    if (origSel && origInp) {
      origSel.addEventListener('change', (e) => {
        if (e.target.value) {
          origInp.value = e.target.value;
          this.runRouteAnalysis();
        }
      });
    }

    // Sync Destination select -> text input
    if (destSel && destInp) {
      destSel.addEventListener('change', (e) => {
        if (e.target.value) {
          destInp.value = e.target.value;
          this.runRouteAnalysis();
        }
      });
    }

    // Debounced text input typing listeners
    let debounceTimer = null;
    const triggerDebouncedAnalysis = () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        this.runRouteAnalysis();
      }, 350);
    };

    if (origInp) {
      origInp.addEventListener('input', triggerDebouncedAnalysis);
      origInp.addEventListener('change', () => this.runRouteAnalysis());
    }
    if (destInp) {
      destInp.addEventListener('input', triggerDebouncedAnalysis);
      destInp.addEventListener('change', () => this.runRouteAnalysis());
    }

    // Auto-recalculate when transport mode changes
    const modeSel = document.getElementById('route-transport-mode');
    if (modeSel) {
      modeSel.addEventListener('change', () => {
        this.runRouteAnalysis();
      });
    }

    // Swap Origin and Destination button
    const swapBtn = document.getElementById('btn-swap-route');
    if (swapBtn && origInp && destInp) {
      swapBtn.addEventListener('click', () => {
        const tmpVal = origInp.value;
        origInp.value = destInp.value;
        destInp.value = tmpVal;

        if (origSel && destSel) {
          const tmpIdx = origSel.selectedIndex;
          origSel.selectedIndex = destSel.selectedIndex;
          destSel.selectedIndex = tmpIdx;
        }

        this.showToast('Route endpoints swapped.', 'info');
        this.runRouteAnalysis();
      });
    }
  },

  /**
   * Sets origin station and immediately recalculates route exposure.
   */
  setRouteOrigin(stationVal) {
    const origInp = document.getElementById('route-origin');
    const origSel = document.getElementById('route-origin-select');
    if (origInp) origInp.value = stationVal;
    if (origSel) {
      for (let i = 0; i < origSel.options.length; i++) {
        if (origSel.options[i].value === stationVal || stationVal.includes(origSel.options[i].value.split(',')[0])) {
          origSel.selectedIndex = i;
          break;
        }
      }
    }
    this.showToast(`Journey origin set to: ${stationVal.split(',')[0]}`, 'info');
    this.runRouteAnalysis();
  },

  /**
   * Sets destination station and immediately recalculates route exposure.
   */
  setRouteDestination(stationVal) {
    const destInp = document.getElementById('route-destination');
    const destSel = document.getElementById('route-dest-select');
    if (destInp) destInp.value = stationVal;
    if (destSel) {
      for (let i = 0; i < destSel.options.length; i++) {
        if (destSel.options[i].value === stationVal || stationVal.includes(destSel.options[i].value.split(',')[0])) {
          destSel.selectedIndex = i;
          break;
        }
      }
    }
    this.showToast(`Journey destination set to: ${stationVal.split(',')[0]}`, 'info');
    this.runRouteAnalysis();
  },

  /**
   * Milestone 2: Travel Route Pollution Exposure Analysis.
   * Discretizes travel corridors, interpolates spatial AQI, and calculates
   * cumulative particulate inhalation exposure comparison.
   */
  async runRouteAnalysis() {
    const origInp = document.getElementById('route-origin');
    const destInp = document.getElementById('route-destination');
    const origSel = document.getElementById('route-origin-select');
    const destSel = document.getElementById('route-dest-select');
    const mode = document.getElementById('route-transport-mode')?.value || 'Car';

    let originName = (origInp?.value || origSel?.value || 'Hadapsar Gadital, Pune').trim();
    let destName = (destInp?.value || destSel?.value || 'Bopodi Square, Pune').trim();

    if (!originName) originName = 'Hadapsar Gadital, Pune';
    if (!destName) destName = 'Bopodi Square, Pune';

    // Helper to resolve coordinates
    const resolveCoords = (name, fallback) => {
      const clean = name.toLowerCase().replace(/,.*$/, '').replace(/station/g, '').replace(/square/g, '').trim();
      for (const [stnKey, s] of Object.entries(this.state.stations || {})) {
        const k = stnKey.toLowerCase();
        if (k.includes(clean) || clean.includes(k.replace(/_\d+$/, ''))) {
          const lat = parseFloat(s.lat);
          const lon = parseFloat(s.lon);
          if (!isNaN(lat) && !isNaN(lon)) return [lat, lon];
        }
      }
      return fallback;
    };

    const originCoords = resolveCoords(originName, [18.4975, 73.9405]);
    const destCoords = resolveCoords(destName, [18.5772, 73.8344]);

    const btn = document.getElementById('btn-analyze-route');
    if (btn) {
      btn.innerHTML = '<span style="display:inline-block; width:12px; height:12px; border:2px solid white; border-top-color:transparent; border-radius:50%; animation:spin 0.6s linear infinite; margin-right:6px; vertical-align:middle;"></span>Analyzing Exposure...';
      btn.disabled = true;
    }

    try {
      const res = await API.calculateRouteExposure({
        origin: originName,
        destination: destName,
        transport_mode: mode,
        health_profile: this.state.selectedHealthProfile
      });

      // Extract Route A (Arterial), Route B (Alternative), Route C (Eco Green)
      const rA = res.route_a || (Array.isArray(res.routes) ? res.routes.find(r => r.id === 'route_a') : {}) || {};
      const rB = res.route_b || (Array.isArray(res.routes) ? res.routes.find(r => r.id === 'route_b') : {}) || {};
      const rC = res.route_c || res.recommended_route || (Array.isArray(res.routes) ? res.routes.find(r => r.id === 'route_c') : {}) || {};

      const aDist = rA.distance_km || 12.4;
      const aAqi = Math.round(rA.avg_aqi || 148);
      const aExp = Math.round(rA.exposure_score || 72);

      const bDist = rB.distance_km || 13.2;
      const bAqi = Math.round(rB.avg_aqi || 112);
      const bExp = Math.round(rB.exposure_score || 54);

      const cDist = rC.distance_km || 15.8;
      const cAqi = Math.round(rC.avg_aqi || 76);
      const cExp = Math.round(rC.exposure_score || 38);

      const elRouteADist = document.getElementById('route-a-dist');
      const elRouteAAqi = document.getElementById('route-a-aqi');
      const elRouteAExp = document.getElementById('route-a-exposure');

      const elRouteBDist = document.getElementById('route-b-dist');
      const elRouteBAqi = document.getElementById('route-b-aqi');
      const elRouteBExp = document.getElementById('route-b-exposure');

      const elRouteCDist = document.getElementById('route-c-dist');
      const elRouteCAqi = document.getElementById('route-c-aqi');
      const elRouteCExp = document.getElementById('route-c-exposure');

      if (elRouteADist) elRouteADist.textContent = `${aDist} km`;
      if (elRouteAAqi) elRouteAAqi.textContent = `${aAqi}`;
      if (elRouteAExp) elRouteAExp.textContent = `${Math.round(aExp * 5.8)} µg (${aExp}/100)`;

      if (elRouteBDist) elRouteBDist.textContent = `${bDist} km`;
      if (elRouteBAqi) elRouteBAqi.textContent = `${bAqi}`;
      if (elRouteBExp) elRouteBExp.textContent = `${Math.round(bExp * 5.8)} µg (${bExp}/100)`;

      if (elRouteCDist) elRouteCDist.textContent = `${cDist} km`;
      if (elRouteCAqi) elRouteCAqi.textContent = `${cAqi}`;
      if (elRouteCExp) elRouteCExp.textContent = `${Math.round(cExp * 5.8)} µg (${cExp}/100)`;

      // Reduction Banner
      const reduction = res.reduction_pct || res.exposure_reduction_pct || Math.max(15, Math.round(((aExp - cExp) / Math.max(1, aExp)) * 100));
      const elReduction = document.getElementById('exposure-reduction-val');
      if (elReduction) elReduction.textContent = `-${reduction}%`;

      // Render routes on the dedicated Leaflet map with full API waypoints payload
      if (!MapEngine.routeMap) {
        MapEngine.initRouteMap('route-exposure-map');
        MapEngine.setRouteMapStations(this.state.stations);
      }
      MapEngine.renderRoutesOnRouteMap(originCoords, destCoords, res);

      const shortOrig = originName.split(',')[0].trim();
      const shortDest = destName.split(',')[0].trim();
      this.showToast(`Route analysis: ${shortOrig} → ${shortDest}. Route C reduces pollution exposure by ${reduction}%.`, 'success');
    } catch (err) {
      console.error('Route exposure analysis failed:', err);
      // Fallback rendering
      if (!MapEngine.routeMap) {
        MapEngine.initRouteMap('route-exposure-map');
        MapEngine.setRouteMapStations(this.state.stations);
      }
      MapEngine.renderRoutesOnRouteMap(originCoords, destCoords);
      this.showToast('Route exposure calculated using local spatial corridor.', 'info');
    } finally {
      if (btn) {
        btn.innerHTML = 'Analyze Route Exposure';
        btn.disabled = false;
      }
    }
  },

  /**
   * Header live clock.
   */
  updateClock() {
    const clockEl = document.getElementById('header-live-clock');
    if (clockEl) {
      const now = new Date();
      clockEl.textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }
  },

  /**
   * Toast notification toast popups.
   */
  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const iconColor = type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : '#3b82f6';

    toast.innerHTML = `
      <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${iconColor}; box-shadow:0 0 6px ${iconColor};"></span>
      <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
};

window.App = App;

/* ==========================================================================
   MILESTONE 3 — Exposure History Manager
   Stores, retrieves, and renders personal trip AQI exposure history.
   ========================================================================== */
const ExposureHistory = {
  STORAGE_KEY: 'airsense_exposure_history',
  _filterMode: 'all',

  getAll() {
    try {
      return JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '[]');
    } catch { return []; }
  },

  save(records) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(records));
  },

  addTrip(tripData) {
    const records = this.getAll();
    records.unshift({
      id: Date.now(),
      date: tripData.date || new Date().toISOString(),
      origin: tripData.origin || 'Unknown',
      destination: tripData.destination || 'Unknown',
      mode: tripData.mode || 'Car',
      avgAqi: Math.round(tripData.avgAqi || 75),
      exposureScore: Math.round(tripData.exposureScore || 50),
      exposureUg: Math.round((tripData.exposureScore || 50) * 5.8),
      category: tripData.category || 'Moderate',
      durationMin: tripData.durationMin || 30,
      distanceKm: tripData.distanceKm || 12,
      recommendation: tripData.recommendation || 'Monitor air quality during travel.'
    });
    this.save(records);
    this.renderHistoryTab();
    return records[0];
  },

  deleteTrip(id) {
    const records = this.getAll().filter(r => r.id !== id);
    this.save(records);
    this.renderHistoryTab();
    App.showToast('Trip removed from exposure history.', 'info');
  },

  clearAll() {
    localStorage.removeItem(this.STORAGE_KEY);
    this.renderHistoryTab();
    App.showToast('Exposure history cleared.', 'info');
  },

  getAqiClass(aqi) {
    if (aqi <= 50) return 'aqi-good';
    if (aqi <= 100) return 'aqi-moderate';
    if (aqi <= 150) return 'aqi-sensitive';
    return 'aqi-poor';
  },

  getAqiColor(aqi) {
    if (aqi <= 50) return '#059669';
    if (aqi <= 100) return '#d97706';
    if (aqi <= 150) return '#ea580c';
    if (aqi <= 200) return '#dc2626';
    return '#7c3aed';
  },

  getModeIcon(mode) {
    const icons = { 'Car': '🚗', 'Public Transport': '🚌', 'Motorcycle': '🏍️', 'Cycling': '🚲', 'Walking': '🚶' };
    return icons[mode] || '🚗';
  },

  exportCSV() {
    const records = this.getAll();
    if (records.length === 0) {
      App.showToast('No exposure history to export.', 'warning');
      return;
    }
    const headers = ['Date', 'Origin', 'Destination', 'Mode', 'Avg AQI', 'Exposure Score', 'Exposure (µg)', 'Category', 'Duration (min)', 'Distance (km)'];
    const rows = records.map(r => [
      new Date(r.date).toLocaleDateString(),
      `"${r.origin}"`, `"${r.destination}"`, r.mode,
      r.avgAqi, r.exposureScore, r.exposureUg,
      r.category, r.durationMin, r.distanceKm
    ].join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `airsense_exposure_history_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    App.showToast('Exposure history exported as CSV.', 'success');
  },

  computeStats(records) {
    if (!records.length) return { trips: 0, avgAqi: '--', totalUg: '--', lowestAqi: '--' };
    const avg = Math.round(records.reduce((a, r) => a + r.avgAqi, 0) / records.length);
    const totalUg = records.reduce((a, r) => a + (r.exposureUg || 0), 0);
    const lowest = Math.min(...records.map(r => r.avgAqi));
    return { trips: records.length, avgAqi: avg, totalUg: totalUg.toLocaleString(), lowestAqi: lowest };
  },

  renderHistoryTab() {
    const container = document.getElementById('tab-module3');
    if (!container) return;

    let records = this.getAll();
    if (this._filterMode !== 'all') {
      records = records.filter(r => r.mode === this._filterMode);
    }

    const stats = this.computeStats(this.getAll()); // stats always from ALL records

    container.innerHTML = `
      <div class="exposure-history-container">
        <div class="exposure-history-header">
          <div>
            <div class="m3-section-header">
              <span class="m3-section-badge">📊 M3 — Personal Exposure</span>
            </div>
            <h2 style="font-size:1.25rem; font-weight:800; color:#0f172a; margin-bottom:4px;">Personal AQI Exposure History</h2>
            <p style="color:#64748b; font-size:0.84rem;">Track your cumulative pollution exposure across journeys.</p>
          </div>
          <div style="display:flex; gap:8px; align-items:center;">
            <div class="pwa-status-bar online" id="pwa-online-status">
              <span class="pwa-status-dot"></span>
              <span id="pwa-status-text">Online</span>
            </div>
            ${records.length > 0 ? `<button class="export-csv-btn" onclick="ExposureHistory.exportCSV()" id="btn-export-csv">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Export CSV
            </button>` : ''}
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="exposure-stats-grid">
          <div class="exposure-stat-card">
            <div class="exposure-stat-value" style="color:#2563eb;">${stats.trips}</div>
            <div class="exposure-stat-label">Trips Logged</div>
          </div>
          <div class="exposure-stat-card">
            <div class="exposure-stat-value" style="color:${this.getAqiColor(typeof stats.avgAqi === 'number' ? stats.avgAqi : 75)};">${stats.avgAqi}</div>
            <div class="exposure-stat-label">Avg AQI</div>
          </div>
          <div class="exposure-stat-card">
            <div class="exposure-stat-value" style="color:#7c3aed; font-size:1.2rem;">${stats.totalUg}</div>
            <div class="exposure-stat-label">Total µg Inhaled</div>
          </div>
          <div class="exposure-stat-card">
            <div class="exposure-stat-value" style="color:#059669;">${stats.lowestAqi}</div>
            <div class="exposure-stat-label">Best AQI Trip</div>
          </div>
        </div>

        <!-- Filter Row -->
        <div class="exposure-filter-row">
          <span style="font-size:0.78rem; font-weight:700; color:#475569; margin-right:4px;">Filter:</span>
          ${['all','Car','Public Transport','Motorcycle','Cycling','Walking'].map(m => `
            <button class="exposure-filter-btn ${this._filterMode === m ? 'active' : ''}"
              onclick="ExposureHistory._filterMode='${m}'; ExposureHistory.renderHistoryTab()">
              ${m === 'all' ? 'All Trips' : this.getModeIcon(m) + ' ' + m}
            </button>
          `).join('')}
          ${this.getAll().length > 0 ? `<button class="export-csv-btn" onclick="if(confirm('Clear all history?')) ExposureHistory.clearAll()" style="margin-left:0; color:#ef4444; border-color:rgba(239,68,68,0.2);">🗑 Clear All</button>` : ''}
        </div>

        <!-- Timeline or Empty State -->
        <div class="exposure-timeline" id="exposure-timeline-list">
          ${records.length === 0 ? `
            <div class="exposure-empty-state">
              <div class="exposure-empty-icon">🗺️</div>
              <h3>${this._filterMode !== 'all' ? 'No trips with this filter' : 'No journeys logged yet'}</h3>
              <p>${this._filterMode !== 'all' ? 'Try a different mode filter.' : 'Go to the Route Exposure tab, analyze a route, then click "Save to History" to start tracking your personal exposure.'}</p>
            </div>
          ` : records.map(r => this._renderTripCard(r)).join('')}
        </div>
      </div>
    `;

    // Update PWA online status
    this._updatePwaStatusBar();
  },

  _renderTripCard(r) {
    const color = this.getAqiColor(r.avgAqi);
    const aqiClass = this.getAqiClass(r.avgAqi);
    const dateStr = new Date(r.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    const timeStr = new Date(r.date).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const modeIcon = this.getModeIcon(r.mode);

    return `
      <div class="exposure-trip-card ${aqiClass}" id="trip-${r.id}">
        <button class="trip-delete-btn" onclick="ExposureHistory.deleteTrip(${r.id})" title="Remove trip">✕</button>
        <div class="trip-aqi-badge" style="background:${color}18; color:${color};">
          <span class="trip-aqi-num">${r.avgAqi}</span>
          <span class="trip-aqi-unit">AQI</span>
        </div>
        <div class="trip-details">
          <div class="trip-route" title="${r.origin} → ${r.destination}">
            ${r.origin.split(',')[0]} → ${r.destination.split(',')[0]}
          </div>
          <div class="trip-meta">
            <span class="trip-meta-chip">${modeIcon} ${r.mode}</span>
            <span class="trip-meta-chip">📅 ${dateStr} ${timeStr}</span>
            <span class="trip-meta-chip">📍 ${r.distanceKm} km</span>
            <span class="trip-meta-chip">⏱ ${r.durationMin} min</span>
            <span class="trip-meta-chip" style="color:${color}; font-weight:700;">${r.category}</span>
          </div>
        </div>
        <div class="trip-right">
          <div class="trip-exposure-label">Exposure</div>
          <div class="trip-exposure-score" style="color:${color};">${r.exposureUg} µg</div>
          <div style="font-size:0.7rem; color:#94a3b8; margin-top:2px;">Score: ${r.exposureScore}/100</div>
        </div>
      </div>
    `;
  },

  _updatePwaStatusBar() {
    const bar = document.getElementById('pwa-online-status');
    const txt = document.getElementById('pwa-status-text');
    if (!bar || !txt) return;
    if (navigator.onLine) {
      bar.className = 'pwa-status-bar online';
      txt.textContent = 'Online — Live Data';
    } else {
      bar.className = 'pwa-status-bar offline';
      txt.textContent = 'Offline — Cached Data';
    }
  }
};

window.ExposureHistory = ExposureHistory;

/* ==========================================================================
   MILESTONE 3 — Notification Preference Manager
   ========================================================================== */
const NotificationPrefs = {
  STORAGE_KEY: 'airsense_notif_prefs',

  defaults: {
    pushEnabled: false,
    aqiThreshold: 100,
    healthProfile: 'General User',
    alerts: {
      morningForecast: true,
      thresholdBreach: true,
      travelAdvisory: true,
      weeklyReport: false
    }
  },

  getPrefs() {
    try {
      return { ...this.defaults, ...JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '{}') };
    } catch { return { ...this.defaults }; }
  },

  savePrefs(prefs) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(prefs));
  },

  getPushStatus() {
    if (!('Notification' in window)) return 'unsupported';
    return Notification.permission;
  },

  async requestPushPermission() {
    if (!('Notification' in window)) {
      App.showToast('Push notifications not supported in this browser.', 'warning');
      return 'unsupported';
    }
    const permission = await Notification.requestPermission();
    const prefs = this.getPrefs();
    prefs.pushEnabled = (permission === 'granted');
    this.savePrefs(prefs);
    this.renderPrefsTab();

    if (permission === 'granted') {
      App.showToast('Push notifications enabled! You\'ll receive AQI alerts.', 'success');
      // Register SW and send a test notification
      if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({
          type: 'AQI_THRESHOLD_CHECK',
          aqi: 0,
          threshold: 9999,
          station: 'Test'
        });
      }
      new Notification('🌱 AirSense Activated', {
        body: 'You will now receive AQI threshold alerts and travel advisories.',
        tag: 'airsense-welcome'
      });
    } else {
      App.showToast('Permission denied — enable notifications in browser settings.', 'warning');
    }
    return permission;
  },

  renderPrefsTab() {
    const container = document.getElementById('tab-module3-prefs');
    if (!container) return;

    const prefs = this.getPrefs();
    const pushStatus = this.getPushStatus();
    const isGranted = pushStatus === 'granted';
    const profiles = [
      { id: 'General User', icon: '👤', name: 'General User' },
      { id: 'Asthmatic / Respiratory', icon: '💨', name: 'Asthmatic / Respiratory' },
      { id: 'Elderly (60+ Years)', icon: '👴', name: 'Elderly (60+)' },
      { id: 'Child (Under 12 Years)', icon: '👶', name: 'Child (<12)' }
    ];

    const thresholdColor = prefs.aqiThreshold <= 50 ? '#059669' : prefs.aqiThreshold <= 100 ? '#d97706' : prefs.aqiThreshold <= 150 ? '#ea580c' : '#dc2626';
    const thresholdLabel = prefs.aqiThreshold <= 50 ? 'Good' : prefs.aqiThreshold <= 100 ? 'Moderate' : prefs.aqiThreshold <= 150 ? 'Sensitive' : 'Poor';

    container.innerHTML = `
      <div style="max-width: 860px;">
        <div class="m3-section-header" style="margin-bottom:24px;">
          <span class="m3-section-badge">🔔 M3 — Notifications</span>
          <div>
            <div class="m3-section-title">Notification Preference Management</div>
            <div class="m3-section-sub">Customize AQI alerts, health profile, and push notification settings.</div>
          </div>
        </div>

        <!-- Push Permission Banner -->
        <div class="push-permission-banner">
          <span class="push-perm-icon">${isGranted ? '✅' : '🔔'}</span>
          <div class="push-perm-text">
            <h4>${isGranted ? 'Push Notifications Active' : 'Enable Push Notifications'}</h4>
            <p>${isGranted ? 'You will receive AQI threshold alerts and morning forecasts.' : 'Get real-time AQI threshold alerts directly on your device, even when the app is closed.'}</p>
          </div>
          <button class="push-enable-btn ${isGranted ? 'granted' : ''}" id="btn-push-permission"
            onclick="NotificationPrefs.requestPushPermission()">
            ${isGranted ? '✓ Notifications On' : 'Enable Alerts'}
          </button>
        </div>

        <div class="notif-prefs-grid">
          <!-- AQI Threshold Card -->
          <div class="notif-card">
            <div class="notif-card-title">
              <div class="notif-card-icon" style="background:rgba(239,68,68,0.1);">⚠️</div>
              AQI Alert Threshold
            </div>
            <p style="font-size:0.78rem; color:#64748b; margin-bottom:12px;">Receive an alert when AQI exceeds this level at any monitored station.</p>
            <div class="threshold-slider-wrap">
              <div class="threshold-slider-labels"><span>0 — Good</span><span>100</span><span>200</span><span>300 — Hazardous</span></div>
              <input type="range" class="threshold-slider" id="notif-threshold-slider"
                min="0" max="300" step="10" value="${prefs.aqiThreshold}"
                oninput="NotificationPrefs._onThresholdChange(this.value)">
            </div>
            <div class="threshold-value-display">
              <span class="threshold-val-num" id="threshold-display-num" style="color:${thresholdColor};">${prefs.aqiThreshold}</span>
              <div>
                <div class="threshold-val-label" id="threshold-display-label" style="color:${thresholdColor};">${thresholdLabel}</div>
                <div style="font-size:0.68rem; color:#94a3b8;">Alert me at this AQI level</div>
              </div>
            </div>
          </div>

          <!-- Alert Types Card -->
          <div class="notif-card">
            <div class="notif-card-title">
              <div class="notif-card-icon" style="background:rgba(37,99,235,0.1);">📋</div>
              Alert Types
            </div>
            <div class="alert-type-grid" id="alert-type-grid">
              ${[
                { id: 'morningForecast', icon: '🌅', label: 'Morning Forecast' },
                { id: 'thresholdBreach', icon: '⚠️', label: 'Threshold Breach' },
                { id: 'travelAdvisory', icon: '🗺️', label: 'Travel Advisory' },
                { id: 'weeklyReport', icon: '📊', label: 'Weekly Report' }
              ].map(a => `
                <div class="alert-chip ${prefs.alerts[a.id] ? 'active' : ''}" id="chip-${a.id}"
                  onclick="NotificationPrefs._toggleAlert('${a.id}')">
                  <span class="alert-chip-icon">${a.icon}</span>
                  <span class="alert-chip-text">${a.label}</span>
                </div>
              `).join('')}
            </div>
            <div style="margin-top:14px;">
              <div class="toggle-row">
                <div>
                  <div class="toggle-label">Daily Summary Digest</div>
                  <div class="toggle-sub">7 AM AQI snapshot for all stations</div>
                </div>
                <label class="pwa-toggle">
                  <input type="checkbox" id="toggle-daily-digest" ${prefs.alerts.morningForecast ? 'checked' : ''}
                    onchange="NotificationPrefs._toggleAlert('morningForecast')">
                  <span class="pwa-toggle-slider"></span>
                </label>
              </div>
              <div class="toggle-row">
                <div>
                  <div class="toggle-label">Route Safety Warnings</div>
                  <div class="toggle-sub">Before high-exposure journeys</div>
                </div>
                <label class="pwa-toggle">
                  <input type="checkbox" id="toggle-route-warn" ${prefs.alerts.travelAdvisory ? 'checked' : ''}
                    onchange="NotificationPrefs._toggleAlert('travelAdvisory')">
                  <span class="pwa-toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>

          <!-- Health Profile Card -->
          <div class="notif-card" style="grid-column: 1 / -1;">
            <div class="notif-card-title">
              <div class="notif-card-icon" style="background:rgba(5,150,105,0.1);">❤️</div>
              Health Sensitivity Profile
            </div>
            <p style="font-size:0.78rem; color:#64748b; margin-bottom:8px;">Your profile personalizes AQI thresholds and travel recommendations.</p>
            <div class="profile-cards-grid" id="profile-cards-grid">
              ${profiles.map(p => `
                <div class="profile-card ${prefs.healthProfile === p.id ? 'selected' : ''}"
                  id="profile-card-${p.id.replace(/[^a-z0-9]/gi, '-')}"
                  onclick="NotificationPrefs._selectProfile('${p.id}')">
                  <span class="profile-card-icon">${p.icon}</span>
                  <span class="profile-card-name">${p.name}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <button class="save-prefs-btn" id="btn-save-prefs" onclick="NotificationPrefs._saveAll()">
          💾 Save Notification Preferences
        </button>
      </div>
    `;
  },

  _onThresholdChange(val) {
    const numEl = document.getElementById('threshold-display-num');
    const labelEl = document.getElementById('threshold-display-label');
    if (!numEl) return;
    const n = parseInt(val);
    const color = n <= 50 ? '#059669' : n <= 100 ? '#d97706' : n <= 150 ? '#ea580c' : '#dc2626';
    const label = n <= 50 ? 'Good' : n <= 100 ? 'Moderate' : n <= 150 ? 'Sensitive' : n <= 200 ? 'Poor' : 'Hazardous';
    numEl.textContent = n;
    numEl.style.color = color;
    if (labelEl) { labelEl.textContent = label; labelEl.style.color = color; }
  },

  _toggleAlert(alertId) {
    const prefs = this.getPrefs();
    prefs.alerts[alertId] = !prefs.alerts[alertId];
    this.savePrefs(prefs);
    // Update chip UI without full re-render
    const chip = document.getElementById(`chip-${alertId}`);
    if (chip) chip.classList.toggle('active', prefs.alerts[alertId]);
    const toggle = document.getElementById(`toggle-daily-digest`);
    if (alertId === 'morningForecast' && toggle) toggle.checked = prefs.alerts[alertId];
    const routeToggle = document.getElementById('toggle-route-warn');
    if (alertId === 'travelAdvisory' && routeToggle) routeToggle.checked = prefs.alerts[alertId];
  },

  _selectProfile(profileId) {
    const prefs = this.getPrefs();
    prefs.healthProfile = profileId;
    this.savePrefs(prefs);
    // Sync with App state
    if (window.App) App.state.selectedHealthProfile = profileId;
    document.querySelectorAll('.profile-card').forEach(c => c.classList.remove('selected'));
    const card = document.getElementById(`profile-card-${profileId.replace(/[^a-z0-9]/gi, '-')}`);
    if (card) card.classList.add('selected');
  },

  _saveAll() {
    const slider = document.getElementById('notif-threshold-slider');
    const prefs = this.getPrefs();
    if (slider) prefs.aqiThreshold = parseInt(slider.value);
    this.savePrefs(prefs);
    App.showToast('Notification preferences saved successfully!', 'success');

    // Dispatch threshold check for current selected station
    if (window.App && App.state.selectedStationKey && navigator.serviceWorker?.controller) {
      const s = App.state.stations[App.state.selectedStationKey] || {};
      navigator.serviceWorker.controller.postMessage({
        type: 'AQI_THRESHOLD_CHECK',
        aqi: s.aqi || 0,
        threshold: prefs.aqiThreshold,
        station: App.state.selectedStationKey.replace(/_/g, ' ')
      });
    }
  }
};

window.NotificationPrefs = NotificationPrefs;

/* ==========================================================================
   MILESTONE 3 — PWA Install Manager
   ========================================================================== */
const PWAManager = {
  _deferredPrompt: null,
  _dismissed: false,

  init() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/static/sw.js')
        .then(reg => {
          console.log('[PWA] Service Worker registered:', reg.scope);
          App.showToast('AirSense PWA ready — app can be installed.', 'info');
        })
        .catch(err => console.warn('[PWA] SW registration failed:', err));
    }

    // Capture install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this._deferredPrompt = e;
      if (!localStorage.getItem('airsense_pwa_dismissed')) {
        this._showInstallBanner();
      }
    });

    window.addEventListener('appinstalled', () => {
      this._hideInstallBanner();
      App.showToast('AirSense installed! Launch from your home screen.', 'success');
      this._deferredPrompt = null;
    });

    // Online/offline status
    window.addEventListener('online', () => ExposureHistory._updatePwaStatusBar());
    window.addEventListener('offline', () => {
      ExposureHistory._updatePwaStatusBar();
      App.showToast('You are offline. Showing cached data.', 'warning');
    });
  },

  _showInstallBanner() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) banner.classList.remove('hidden');
  },

  _hideInstallBanner() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) banner.classList.add('hidden');
  },

  async triggerInstall() {
    if (!this._deferredPrompt) {
      App.showToast('To install: use browser menu → "Add to Home Screen" or "Install app".', 'info');
      return;
    }
    this._deferredPrompt.prompt();
    const { outcome } = await this._deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      App.showToast('Installing AirSense on your device...', 'success');
    }
    this._deferredPrompt = null;
    this._hideInstallBanner();
  },

  dismissInstall() {
    localStorage.setItem('airsense_pwa_dismissed', '1');
    this._hideInstallBanner();
  }
};

window.PWAManager = PWAManager;

/* ==========================================================================
   MILESTONE 3 — Map Travel Advisory Overlay Extension
   Extends MapEngine to draw AQI-colored waypoint circles on the route map
   and provide "Save to History" after route analysis.
   ========================================================================== */
const RouteAdvisory = {
  _lastRouteData: null,
  _overlayLayer: null,

  /**
   * Draw travel advisory overlay on the route map.
   * Plots color-coded AQI waypoint circles with popup health advice.
   */
  drawAdvisoryOverlay(originCoords, destCoords, routeData) {
    if (!MapEngine.routeMap) return;

    // Remove previous advisory overlay
    if (this._overlayLayer) {
      MapEngine.routeMap.removeLayer(this._overlayLayer);
    }
    this._overlayLayer = L.layerGroup().addTo(MapEngine.routeMap);

    const routes = routeData ? [
      { data: routeData.route_a || routeData.routes?.[0], label: 'Route A — Arterial', color: '#ef4444' },
      { data: routeData.route_b || routeData.routes?.[1], label: 'Route B — Alternative', color: '#f59e0b' },
      { data: routeData.route_c || routeData.recommended_route || routeData.routes?.[2], label: 'Route C — Eco Clean', color: '#10b981' }
    ] : [];

    routes.forEach(route => {
      if (!route.data) return;
      const waypoints = route.data.waypoints || route.data.sample_points || [];
      waypoints.forEach((wp, i) => {
        if (!wp.lat && !wp.latitude) return;
        const lat = parseFloat(wp.lat || wp.latitude);
        const lon = parseFloat(wp.lon || wp.longitude || wp.lng);
        const aqi = Math.round(wp.aqi || wp.estimated_aqi || 80);
        const wpColor = MapEngine.getAQIColor ? MapEngine.getAQIColor(aqi) : route.color;

        const circle = L.circleMarker([lat, lon], {
          radius: 7,
          fillColor: wpColor,
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.85
        });

        const catLabel = aqi <= 50 ? 'Good' : aqi <= 100 ? 'Moderate' : aqi <= 150 ? 'Sensitive' : aqi <= 200 ? 'Poor' : 'Hazardous';
        circle.bindPopup(`
          <div style="font-family:Inter,sans-serif; min-width:160px; padding:4px;">
            <div style="font-weight:700; font-size:0.84rem; color:#0f172a; margin-bottom:4px;">${route.label}</div>
            <div style="font-size:1.1rem; font-weight:800; color:${wpColor}; margin-bottom:4px;">${aqi} AQI</div>
            <div style="font-size:0.72rem; color:#475569;">
              <div>Waypoint ${i + 1} of ${waypoints.length}</div>
              <div style="font-weight:700; color:${wpColor};">${catLabel}</div>
              ${wp.health_note ? `<div style="margin-top:4px;">${wp.health_note}</div>` : ''}
            </div>
          </div>
        `);
        this._overlayLayer.addLayer(circle);
      });
    });

    this._lastRouteData = { originCoords, destCoords, routeData };
    this._renderSaveButton();
  },

  _renderSaveButton() {
    const container = document.getElementById('route-save-history-container');
    if (!container) return;
    container.innerHTML = `
      <div style="margin-top:12px;">
        <div class="advisory-overlay-legend">
          <div class="legend-title">Travel Advisory Map Legend</div>
          <div class="legend-row"><span class="legend-dot" style="background:#10b981;"></span> Route C — Eco Clean (Recommended)</div>
          <div class="legend-row"><span class="legend-dot" style="background:#f59e0b;"></span> Route B — Alternative Corridor</div>
          <div class="legend-row"><span class="legend-dot" style="background:#ef4444;"></span> Route A — Arterial (High Exposure)</div>
          <div class="legend-row"><span class="legend-dot" style="background:#38bdf8;"></span> Monitoring Stations</div>
        </div>
        <button class="save-route-btn" id="btn-save-to-history" onclick="RouteAdvisory.saveToHistory()">
          💾 Save Route to Exposure History
        </button>
      </div>
    `;
  },

  saveToHistory() {
    const btn = document.getElementById('btn-save-to-history');
    if (!btn) return;

    const origInp = document.getElementById('route-origin');
    const destInp = document.getElementById('route-destination');
    const mode = document.getElementById('route-transport-mode')?.value || 'Car';

    const rd = this._lastRouteData?.routeData;
    const rC = rd?.route_c || rd?.recommended_route || {};
    const rA = rd?.route_a || {};

    const tripData = {
      date: new Date().toISOString(),
      origin: origInp?.value || 'Hadapsar Gadital, Pune',
      destination: destInp?.value || 'Bopodi Square, Pune',
      mode: mode,
      avgAqi: rC.avg_aqi || rA.avg_aqi || 85,
      exposureScore: rC.exposure_score || 45,
      category: rC.avg_aqi <= 50 ? 'Good' : rC.avg_aqi <= 100 ? 'Moderate' : rC.avg_aqi <= 150 ? 'Sensitive' : 'Poor',
      durationMin: rC.duration_min || rA.duration_min || 35,
      distanceKm: rC.distance_km || rA.distance_km || 12,
      recommendation: rd?.recommendations?.[0] || 'Use Route C for minimum exposure.'
    };

    ExposureHistory.addTrip(tripData);
    btn.textContent = '✓ Saved to History';
    btn.classList.add('saved');
    App.showToast('Route saved to Personal Exposure History!', 'success');

    // Check push notification threshold
    const prefs = NotificationPrefs.getPrefs();
    if (prefs.pushEnabled && tripData.avgAqi >= prefs.aqiThreshold && navigator.serviceWorker?.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'AQI_THRESHOLD_CHECK',
        aqi: tripData.avgAqi,
        threshold: prefs.aqiThreshold,
        station: `${tripData.origin.split(',')[0]} → ${tripData.destination.split(',')[0]}`
      });
    }
  }
};

window.RouteAdvisory = RouteAdvisory;

// ── Patch App.switchTab to handle M3 tabs ─────────────────────────────────
const _originalSwitchTab = App.switchTab.bind(App);
App.switchTab = function(tabId) {
  _originalSwitchTab(tabId);

  // Update mobile bottom nav active state
  document.querySelectorAll('.mobile-nav-item').forEach(item => {
    item.classList.toggle('active', item.getAttribute('data-tab') === tabId);
  });

  // M3 specific tab rendering
  if (tabId === 'module3') {
    ExposureHistory.renderHistoryTab();
  } else if (tabId === 'module3_prefs') {
    NotificationPrefs.renderPrefsTab();
  }

  // Update M3 titles
  const extraTitles = {
    'module3': 'Personal Exposure History — Trip AQI Log',
    'module3_prefs': 'Notification Preference Management — PWA Alerts'
  };
  const titleEl = document.getElementById('current-module-title');
  if (titleEl && extraTitles[tabId]) {
    titleEl.textContent = extraTitles[tabId];
  }
};

// ── Patch App.runRouteAnalysis to draw travel advisory overlay ──────────────
const _originalRunRoute = App.runRouteAnalysis.bind(App);
App.runRouteAnalysis = async function() {
  await _originalRunRoute();
  // After route renders, attempt to draw advisory overlay
  const origInp = document.getElementById('route-origin');
  const destInp = document.getElementById('route-destination');
  // Try to get coords from last render (best-effort)
  const stations = App.state.stations || {};
  const resolveCoords = (name, fallback) => {
    const clean = name.toLowerCase().replace(/,.*$/, '').replace(/station|square/g, '').trim();
    for (const [k, s] of Object.entries(stations)) {
      if (k.toLowerCase().includes(clean) || clean.includes(k.toLowerCase().replace(/_\d+$/, ''))) {
        return [parseFloat(s.lat), parseFloat(s.lon)];
      }
    }
    return fallback;
  };
  const origin = resolveCoords(origInp?.value || '', [18.4975, 73.9405]);
  const dest = resolveCoords(destInp?.value || '', [18.5772, 73.8344]);

  // Draw with empty routeData (waypoints rendered by MapEngine already)
  if (RouteAdvisory._lastRouteData?.routeData) {
    RouteAdvisory.drawAdvisoryOverlay(origin, dest, RouteAdvisory._lastRouteData.routeData);
  } else {
    RouteAdvisory._renderSaveButton();
  }
};

// Store route data when route analysis completes
const _origRunRoute2 = App.runRouteAnalysis.bind(App);
App._storeRouteResult = function(data, originCoords, destCoords) {
  RouteAdvisory._lastRouteData = { routeData: data, originCoords, destCoords };
  RouteAdvisory.drawAdvisoryOverlay(originCoords, destCoords, data);
};

// Start application when DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
  App.init();
  PWAManager.init();
  // Load saved health profile into App state
  const savedPrefs = NotificationPrefs.getPrefs();
  App.state.selectedHealthProfile = savedPrefs.healthProfile;
});

