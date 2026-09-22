"""
Unit & Regression Tests for Machine Learning & Geostatistical Engines:
1. PyTorch / NumPy Recurrent Multi-Step AQI Predictors (LSTM, GRU)
2. Geostatistical Spatial Interpolation (IDW, Ordinary Kriging)
3. Route Particulate Exposure Estimation Engine
4. CPCB National Ambient Air Quality Index (NAAQI) Classification
"""

import os
import sys
import unittest
import numpy as np

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.custom_dataset import load_pune_data, get_aqi_category_info, HEALTH_PROFILES
from ml.models import AQIPredictor
from ml.spatial_interpolation import SpatialInterpolator, haversine_distance, get_spatial_interpolator
from ml.route_exposure import (
    RoutePollutionEstimator,
    MODE_VENTILATION_FACTORS,
    HEALTH_PROFILE_MULTIPLIERS,
    PUNE_LANDMARKS
)


class TestMLEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pune_data = load_pune_data()
        cls.predictor = AQIPredictor()
        cls.interpolator = get_spatial_interpolator(cls.pune_data)
        cls.route_estimator = RoutePollutionEstimator(cls.interpolator)

    # ── 1. Telemetry Dataset Ingestion Tests ─────────────────────────────────
    def test_pune_telemetry_loaded(self):
        """Ensure Pune telemetry dataset is loaded with valid station nodes and metadata."""
        self.assertGreaterEqual(len(self.pune_data), 10, "Should have at least 10 Pune monitoring stations")
        first_stn = list(self.pune_data.values())[0]
        required_keys = ["lat", "lon", "aqi", "pm25", "pm10", "no2"]
        for key in required_keys:
            self.assertIn(key, first_stn, f"Station metadata missing required sensor key: {key}")
            self.assertIsNotNone(first_stn[key], f"Station key {key} cannot be None")

    # ── 2. CPCB AQI Categorization Tests ─────────────────────────────────────
    def test_cpcb_category_boundaries(self):
        """Verify CPCB standard 6-tier categorization across exact breakpoint boundaries."""
        test_cases = [
            (25.0, "Good", "#16A34A"),
            (50.0, "Good", "#16A34A"),
            (51.0, "Satisfactory / Moderate", "#CA8A04"),
            (100.0, "Satisfactory / Moderate", "#CA8A04"),
            (101.0, "Unhealthy for Sensitive Groups", "#EA580C"),
            (150.0, "Unhealthy for Sensitive Groups", "#EA580C"),
            (151.0, "Unhealthy / Poor", "#DC2626"),
            (200.0, "Unhealthy / Poor", "#DC2626"),
            (201.0, "Very Unhealthy / Very Poor", "#7C3AED"),
            (300.0, "Very Unhealthy / Very Poor", "#7C3AED"),
            (301.0, "Hazardous / Severe", "#991B1B"),
            (450.0, "Hazardous / Severe", "#991B1B"),
        ]
        for aqi, expected_label, expected_color in test_cases:
            info = get_aqi_category_info(aqi)
            self.assertIn("label", info, f"Missing label for AQI={aqi}")
            self.assertIn("color", info, f"Missing color for AQI={aqi}")
            self.assertEqual(info["label"], expected_label, f"AQI {aqi} expected label '{expected_label}' but got '{info['label']}'")
            self.assertEqual(info["color"], expected_color, f"AQI {aqi} expected color '{expected_color}' but got '{info['color']}'")

    # ── 3. Deep Recurrent Forecasting Tests (LSTM & GRU) ────────────────────
    def test_gru_forecasting_24h(self):
        """Verify GRU multi-step 24-hour predictive forecast structure and confidence bounds."""
        stn_data = list(self.pune_data.values())[0]
        res = self.predictor.predict(stn_data, architecture="GRU", horizon=24)

        self.assertEqual(res["architecture"], "GRU")
        self.assertEqual(res["horizon_hours"], 24)
        self.assertEqual(len(res["aqi_trajectory"]), 24, "Forecast must generate exactly 24 hours of trajectory")
        self.assertEqual(len(res["lower_bound"]), 24)
        self.assertEqual(len(res["upper_bound"]), 24)

        # Mathematical sanity: lower bound <= predicted <= upper bound
        for t in range(24):
            pred = res["aqi_trajectory"][t]
            low = res["lower_bound"][t]
            high = res["upper_bound"][t]
            self.assertGreater(pred, 0, f"Predicted AQI at t={t} must be positive")
            self.assertLessEqual(low, pred + 0.01, f"Lower bound exceeds prediction at hour {t}")
            self.assertGreaterEqual(high, pred - 0.01, f"Upper bound is lower than prediction at hour {t}")

    def test_lstm_forecasting_custom_horizon(self):
        """Verify LSTM multi-step forecast with custom 12-hour horizon."""
        stn_data = list(self.pune_data.values())[1]
        res = self.predictor.predict(stn_data, architecture="LSTM", horizon=12)

        self.assertEqual(res["architecture"], "LSTM")
        self.assertEqual(res["horizon_hours"], 12)
        self.assertEqual(len(res["aqi_trajectory"]), 12)
        self.assertIn("pm25_trajectory", res)
        self.assertIn("pm10_trajectory", res)
        self.assertIn("no2_trajectory", res)
        self.assertEqual(len(res["pm25_trajectory"]), 12)

    # ── 4. Spatial Interpolation Tests (IDW & Ordinary Kriging) ──────────────
    def test_haversine_distance_accuracy(self):
        """Verify Haversine distance computation against known geographic distance."""
        # Distance between Mumbai (19.0760, 72.8777) and Pune (18.5204, 73.8567) is approx 118-120 km
        dist = haversine_distance(19.0760, 72.8777, 18.5204, 73.8567)
        self.assertAlmostEqual(dist, 119.0, delta=5.0, msg="Haversine distance between Mumbai and Pune is inaccurate")

    def test_idw_exact_station_match(self):
        """When target coordinates coincide with an existing station, IDW should return that station's AQI."""
        stn_name, stn = list(self.pune_data.items())[0]
        res = self.interpolator.idw(stn["lat"], stn["lon"])
        self.assertAlmostEqual(res["estimated_aqi"], stn["aqi"], delta=0.5,
                               msg=f"IDW at station {stn_name} did not match station's exact AQI")
        self.assertEqual(res["nearest_station"], stn_name)
        self.assertAlmostEqual(res["distance_km"], 0.0, delta=0.1)

    def test_ordinary_kriging_estimation_and_variance(self):
        """Verify Ordinary Kriging returns bounded AQI and non-negative estimation variance."""
        res = self.interpolator.kriging(18.5300, 73.8400)
        self.assertIn("estimated_aqi", res)
        self.assertGreater(res["estimated_aqi"], 0.0)
        self.assertLess(res["estimated_aqi"], 600.0)
        self.assertIn("standard_error", res)
        self.assertGreaterEqual(res["standard_error"], 0.0)

    # ── 5. Travel Route Particulate Exposure Tests ───────────────────────────
    def test_route_exposure_calculation(self):
        """Verify travel route exposure estimator generates 3 distinct paths and exposure metrics."""
        result = self.route_estimator.estimate_exposure(
            origin="Hadapsar_Gadital_01",
            destination="BopadiSquare_65",
            transport_mode="Car",
            health_profile="General User"
        )
        self.assertIn("routes", result)
        self.assertIn("route_a", result)
        self.assertIn("route_b", result)
        self.assertIn("route_c", result)
        self.assertIn("reduction_pct", result)
        self.assertGreater(result["reduction_pct"], 0.0, "Route C (Eco Corridor) should achieve positive exposure reduction")

        # Check waypoints exist and are valid coordinate pairs
        for r_key in ["route_a", "route_b", "route_c"]:
            route = result[r_key]
            self.assertIn("waypoints", route)
            self.assertGreater(len(route["waypoints"]), 3, f"Route {r_key} should have multiple waypoints")
            self.assertIn("exposure_index", route)
            self.assertGreater(route["exposure_index"], 0.0)

    def test_transport_mode_and_health_multipliers(self):
        """Verify that more active transport modes and sensitive profiles increase particulate exposure."""
        res_car = self.route_estimator.estimate_exposure(
            origin="Hadapsar_Gadital_01", destination="BopadiSquare_65",
            transport_mode="Car", health_profile="General User"
        )
        res_walking = self.route_estimator.estimate_exposure(
            origin="Hadapsar_Gadital_01", destination="BopadiSquare_65",
            transport_mode="Walking", health_profile="General User"
        )
        res_asthmatic = self.route_estimator.estimate_exposure(
            origin="Hadapsar_Gadital_01", destination="BopadiSquare_65",
            transport_mode="Walking", health_profile="Asthmatic / Respiratory"
        )

        exp_car = res_car["route_a"]["exposure_index"]
        exp_walk = res_walking["route_a"]["exposure_index"]
        exp_asthma = res_asthmatic["route_a"]["exposure_index"]

        self.assertGreater(exp_walk, exp_car, "Walking exposure should exceed Car exposure due to ventilation factors")
        self.assertGreater(exp_asthma, exp_walk, "Asthmatic exposure should exceed General User due to vulnerability multiplier")


if __name__ == "__main__":
    unittest.main()
