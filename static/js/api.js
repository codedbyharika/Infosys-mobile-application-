/**
 * EcoAir Intelligence — API Client Layer
 * Handles REST communication with FastAPI microservice.
 */

const API_BASE = '';

const API = {
  /**
   * Fetches top KPI summary metrics for the executive dashboard.
   */
  async getKPISummary() {
    try {
      const res = await fetch(`${API_BASE}/api/kpi-summary`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to fetch KPI summary:', err);
      throw err;
    }
  },

  /**
   * Fetches recent neural predictions vs actual ground truth records.
   */
  async getPredictionsVsActual() {
    try {
      const res = await fetch(`${API_BASE}/api/predictions-vs-actual`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to fetch predictions vs actual:', err);
      throw err;
    }
  },

  /**
   * Fetches comparative station telemetry for the dashboard comparison chart.
   */
  async getStationComparison() {
    try {
      const res = await fetch(`${API_BASE}/api/station-comparison`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn('Failed to fetch station comparison:', err);
      return null;
    }
  },

  /**
   * Fetches all monitoring stations with complete sensor telemetry.
   */
  async getStations() {
    try {
      const res = await fetch(`${API_BASE}/api/stations`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to fetch stations:', err);
      throw err;
    }
  },

  /**
   * Fetches specific station telemetry and sensor details.
   */
  async getStation(name) {
    try {
      const res = await fetch(`${API_BASE}/api/stations/${encodeURIComponent(name)}`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`Failed to fetch station ${name}:`, err);
      throw err;
    }
  },

  /**
   * Fetches 24-hour historical records for a station.
   */
  async getStationHistory(name, lookback = 24) {
    try {
      const res = await fetch(`${API_BASE}/api/stations/${encodeURIComponent(name)}/history?lookback=${lookback}`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`Failed to fetch history for ${name}:`, err);
      throw err;
    }
  },

  /**
   * Requests multi-step recurrent forecast (LSTM/GRU).
   */
  async getForecast({ location_name, latitude, longitude, architecture = 'GRU', horizon_hours = 24 }) {
    try {
      const res = await fetch(`${API_BASE}/api/predict/forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location_name,
          latitude,
          longitude,
          architecture,
          horizon_hours: parseInt(horizon_hours)
        })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to generate forecast:', err);
      throw err;
    }
  },

  /**
   * Evaluates geostatistical spatial interpolation (IDW / Ordinary Kriging).
   */
  async interpolatePoint({ latitude, longitude, method = 'idw', power = 2.0 }) {
    try {
      const res = await fetch(`${API_BASE}/api/predict/interpolate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
          method,
          power: parseFloat(power)
        })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to interpolate point:', err);
      throw err;
    }
  },

  /**
   * Calculates route pollution exposure comparison.
   */
  async calculateRouteExposure({ origin, destination, transport_mode = 'Car', health_profile = 'General User' }) {
    try {
      const res = await fetch(`${API_BASE}/api/route/exposure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin,
          destination,
          transport_mode,
          health_profile
        })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to calculate route exposure:', err);
      throw err;
    }
  },

  /**
   * Fetches health profiles and sensitivity thresholds.
   */
  async getHealthProfiles() {
    try {
      const res = await fetch(`${API_BASE}/api/health-profiles`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to fetch health profiles:', err);
      throw err;
    }
  },

  /**
   * Fetches operational subsystem status matrix for Module 4.
   */
  async getSystemStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/system/status`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to fetch system status:', err);
      throw err;
    }
  },

  /**
   * Executes QA test harness.
   */
  async runQATests() {
    try {
      const res = await fetch(`${API_BASE}/api/system/tests/run`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to run QA tests:', err);
      throw err;
    }
  }
};
