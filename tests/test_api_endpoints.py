"""
Comprehensive Integration & System Tests for FastAPI REST Endpoints:
1. Static Web Application & Asset Delivery
2. System Health & Heartbeat Feeds
3. Real-time Station Telemetry & Historical Series
4. Station Comparison Analytics
5. Multi-Step Deep Recurrent Forecasting (GRU & LSTM)
6. Geostatistical Spatial Interpolation (IDW & Ordinary Kriging)
7. Travel Route Particulate Exposure Estimation Engine
8. KPI Summary & Neural Model Validation Tables
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from api.main import app


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    # ── 1. Web Frontend & Static Asset Delivery ──────────────────────────────
    def test_root_index_html(self):
        """Root GET / must serve the modern SPA index.html with valid doctype and container IDs."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("<!DOCTYPE html>", res.text)
        self.assertIn("AirSense", res.text)
        # Critical container elements
        self.assertIn('id="global-station-select"', res.text)
        self.assertIn('id="forecast-trajectory-chart"', res.text)
        self.assertIn('id="station-comparison-chart"', res.text)
        self.assertIn('id="route-exposure-map"', res.text)

    def test_static_assets_deliverable(self):
        """Ensure all required CSS and JavaScript bundles return HTTP 200 with non-empty content."""
        assets = [
            "/static/css/style.css",
            "/static/js/api.js",
            "/static/js/app.js",
            "/static/js/charts.js",
            "/static/js/map.js",
        ]
        for asset_url in assets:
            res = self.client.get(asset_url)
            self.assertEqual(res.status_code, 200, f"Static asset {asset_url} returned status {res.status_code}")
            self.assertGreater(len(res.text), 100, f"Static asset {asset_url} appears empty or truncated")

    # ── 2. Health & Heartbeat Endpoints ──────────────────────────────────────
    def test_health_check_endpoints(self):
        """Both /health and /api/health must report operational status and model registry."""
        for path in ["/health", "/api/health"]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"{path} returned {res.status_code}")
            data = res.json()
            self.assertEqual(data.get("status"), "HEALTHY")
            self.assertIn("registered_stations", data)
            self.assertGreaterEqual(data["registered_stations"], 10)
            self.assertIn("loaded_models", data)

    # ── 3. Station Telemetry & Historical Series ─────────────────────────────
    def test_get_all_stations(self):
        """GET /api/stations returns active telemetry nodes with all required environmental metrics."""
        res = self.client.get("/api/stations")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("stations", data)
        self.assertGreaterEqual(data["total"], 10)

        # Check required fields in each station
        for name, stn in data["stations"].items():
            self.assertIn("aqi", stn)
            self.assertIn("lat", stn)
            self.assertIn("lon", stn)
            self.assertIn("pm25", stn)
            self.assertIn("pm10", stn)
            self.assertIn("no2", stn)
            self.assertIn("traffic_congestion_score", stn)

    def test_get_single_station_valid_and_invalid(self):
        """GET /api/stations/{name} returns individual station or HTTP 404 for unknown stations."""
        res = self.client.get("/api/stations/BopadiSquare_65")
        self.assertEqual(res.status_code, 200)
        self.assertAlmostEqual(res.json()["aqi"], 78.9, delta=1.0)

        res_404 = self.client.get("/api/stations/NonExistent_Station_999")
        self.assertEqual(res_404.status_code, 404)

    def test_get_station_history(self):
        """GET /api/stations/{name}/history returns chronological sequential records."""
        res = self.client.get("/api/stations/BopadiSquare_65/history?lookback=24")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["station"], "BopadiSquare_65")
        self.assertEqual(data["lookback"], 24)
        self.assertGreater(len(data["records"]), 0)
        rec = data["records"][0]
        self.assertIn("timestamp", rec)
        self.assertIn("aqi", rec)
        self.assertIn("pm25", rec)

    # ── 4. Station Comparison Analytics ──────────────────────────────────────
    def test_station_comparison_api(self):
        """GET /api/station-comparison returns sorted telemetry with clean names and CPCB tags."""
        res = self.client.get("/api/station-comparison")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("stations", data)
        self.assertGreaterEqual(data["count"], 10)

        # Verify descending order by AQI
        stations = data["stations"]
        for i in range(len(stations) - 1):
            self.assertGreaterEqual(stations[i]["aqi"], stations[i + 1]["aqi"],
                                    "Station comparison must be sorted in descending AQI order")
            # Verify clean station name formatting
            self.assertNotIn("Square_65", stations[i]["station_name"])

    # ── 5. AI Recurrent Forecasting ──────────────────────────────────────────
    def test_forecast_gru_and_lstm(self):
        """POST /api/predict/forecast tests both GRU and LSTM with 24-step horizons."""
        for arch in ["GRU", "LSTM"]:
            payload = {
                "location_name": "BopadiSquare_65",
                "architecture": arch,
                "horizon_hours": 24
            }
            res = self.client.post("/api/predict/forecast", json=payload)
            self.assertEqual(res.status_code, 200, f"Forecast failed for {arch}")
            fc = res.json()
            self.assertEqual(fc["architecture"], arch)
            self.assertEqual(fc["horizon_hours"], 24)
            self.assertEqual(len(fc["aqi_trajectory"]), 24)
            self.assertEqual(len(fc["confidence_intervals"]), 24)
            self.assertIn("pm25", fc["pollutant_breakdown"])
            self.assertIn("pm10", fc["pollutant_breakdown"])
            self.assertIn("no2", fc["pollutant_breakdown"])

            # Verify math: hour 1 starts near current observation
            self.assertAlmostEqual(fc["aqi_trajectory"][0], fc["current_aqi"], delta=1.5)

    def test_forecast_horizon_options(self):
        """Verify forecast responds dynamically to 6h, 12h, and 24h horizons."""
        for h in [6, 12, 24]:
            payload = {"location_name": "Hadapsar_Gadital_01", "architecture": "GRU", "horizon_hours": h}
            res = self.client.post("/api/predict/forecast", json=payload)
            self.assertEqual(res.status_code, 200)
            fc = res.json()
            self.assertEqual(fc["horizon_hours"], h)
            self.assertEqual(len(fc["aqi_trajectory"]), h)
            self.assertEqual(len(fc["confidence_intervals"]), h)

    # ── 6. Geostatistical Spatial Interpolation ──────────────────────────────
    def test_interpolation_idw_and_kriging(self):
        """POST /api/predict/interpolate verifies IDW and Ordinary Kriging estimations."""
        # Test IDW
        res_idw = self.client.post("/api/predict/interpolate", json={
            "latitude": 18.5204,
            "longitude": 73.8567,
            "method": "idw",
            "power": 2.0
        })
        self.assertEqual(res_idw.status_code, 200)
        data_idw = res_idw.json()
        self.assertGreater(data_idw["estimated_aqi"], 0.0)
        self.assertEqual(data_idw["method"].lower(), "idw")

        # Test Kriging
        res_krig = self.client.post("/api/predict/interpolate", json={
            "latitude": 18.5300,
            "longitude": 73.8400,
            "method": "kriging"
        })
        self.assertEqual(res_krig.status_code, 200)
        data_krig = res_krig.json()
        self.assertGreater(data_krig["estimated_aqi"], 0.0)
        self.assertIn("kriging", data_krig["method"].lower())
        self.assertIsNotNone(data_krig["uncertainty_score"])

    # ── 7. Travel Route Exposure Engine ──────────────────────────────────────
    def test_route_exposure_api(self):
        """POST /api/route/exposure verifies route computation across transport modes."""
        payload = {
            "origin": "Hadapsar_Gadital_01",
            "destination": "BopadiSquare_65",
            "transport_mode": "Car",
            "health_profile": "General User"
        }
        res = self.client.post("/api/route/exposure", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("route_a", data)
        self.assertIn("route_b", data)
        self.assertIn("route_c", data)
        self.assertIn("reduction_pct", data)
        self.assertGreater(data["reduction_pct"], 0.0)
        self.assertIn("hotspots", data)

    # ── 8. KPI Summary & System Validation ───────────────────────────────────
    def test_kpi_summary_and_predictions_vs_actual(self):
        """GET /api/kpi-summary and /api/predictions-vs-actual return valid executive telemetry."""
        res_kpi = self.client.get("/api/kpi-summary")
        self.assertEqual(res_kpi.status_code, 200)
        kpi = res_kpi.json()
        self.assertEqual(kpi["active_stations"], 10)
        self.assertGreater(kpi["avg_city_aqi"], 0)
        self.assertIn("category_breakdown", kpi)

        res_pva = self.client.get("/api/predictions-vs-actual")
        self.assertEqual(res_pva.status_code, 200)
        pva = res_pva.json()
        self.assertEqual(pva["total"], 10)
        for row in pva["comparisons"]:
            self.assertIn("predicted_aqi", row)
            self.assertIn("actual_aqi", row)
            self.assertIn("accuracy", row)
            self.assertGreater(row["accuracy_val"], 80.0)


if __name__ == "__main__":
    unittest.main()
