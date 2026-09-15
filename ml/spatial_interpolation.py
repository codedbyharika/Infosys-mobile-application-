"""
Spatial Interpolation Module for Arbitrary Location AQI Estimation.
Implements:
  1. Inverse Distance Weighting (IDW)
  2. Ordinary Kriging (Gaussian Variogram with Kriging Variance / Uncertainty)
  3. Spatial Meshgrid Generator for Regional Dispersion Mapping
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two geographic coordinates in kilometers.
    """
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class SpatialInterpolator:
    """
    Geostatistical Spatial AQI Interpolation Engine.
    Estimates ambient air quality at arbitrary GPS coordinates between physical monitoring stations.
    """
    def __init__(self, stations: Optional[Dict[str, Any]] = None):
        """
        stations: dict mapping station_name -> {
            'lat': float, 'lon': float, 'aqi': float, 'pm25': float, ...
        }
        """
        self.stations = stations or {}

    def set_stations(self, stations: Dict[str, Any]):
        self.stations = stations

    def _extract_points(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Extracts coordinates (N, 2), AQI values (N,), and names from station dict."""
        coords = []
        values = []
        names = []
        for name, data in self.stations.items():
            if "lat" in data and "lon" in data and "aqi" in data:
                coords.append([float(data["lat"]), float(data["lon"])])
                values.append(float(data["aqi"]))
                names.append(name)
        return np.array(coords), np.array(values), names

    # ── 1. Inverse Distance Weighting (IDW) ──────────────────────────────────
    def idw(self, target_lat: float, target_lon: float, power: float = 2.0) -> dict:
        """
        Estimates AQI at (target_lat, target_lon) using Inverse Distance Weighting.
        Weight: w_i = 1 / (d_i ^ power)
        """
        coords, values, names = self._extract_points()
        if len(coords) == 0:
            return {"estimated_aqi": 75.0, "method": "IDW", "confidence": 0.5, "nearest_station": None}

        distances = []
        for i in range(len(coords)):
            d = haversine_distance(target_lat, target_lon, coords[i, 0], coords[i, 1])
            distances.append(d)

        distances = np.array(distances)
        min_idx = int(np.argmin(distances))
        min_dist = distances[min_idx]

        # Exact station proximity check
        if min_dist < 0.05:
            return {
                "estimated_aqi": round(float(values[min_idx]), 1),
                "method": "IDW",
                "nearest_station": names[min_idx],
                "distance_km": round(float(min_dist), 2),
                "confidence": 0.98,
                "uncertainty_score": 2.0,
                "weights": {names[min_idx]: 1.0}
            }

        weights = 1.0 / (distances ** power)
        normalized_weights = weights / np.sum(weights)

        interpolated_aqi = np.sum(normalized_weights * values)
        confidence = float(np.clip(1.0 - (min_dist / 35.0), 0.35, 0.95))

        weight_breakdown = {
            names[i]: round(float(normalized_weights[i]), 3)
            for i in np.argsort(-normalized_weights)[:5]
        }

        return {
            "estimated_aqi": round(float(interpolated_aqi), 1),
            "method": "IDW",
            "power": power,
            "nearest_station": names[min_idx],
            "distance_km": round(float(min_dist), 2),
            "confidence": round(confidence, 2),
            "uncertainty_score": round(float(min_dist * 1.8), 1),
            "contributing_stations": weight_breakdown
        }

    # ── 2. Ordinary Kriging (Gaussian Variogram) ─────────────────────────────
    def kriging(
        self,
        target_lat: float,
        target_lon: float,
        nugget: float = 4.0,
        sill: float = 140.0,
        spatial_range_km: float = 18.0
    ) -> dict:
        """
        Estimates AQI at (target_lat, target_lon) using Ordinary Kriging with a Gaussian Variogram.
        Semivariogram model: gamma(h) = nugget + (sill - nugget) * (1 - exp(-3 * (h / range)^2))
        Also outputs Kriging variance sigma_k^2 as a rigorous measure of spatial uncertainty.
        """
        coords, values, names = self._extract_points()
        N = len(coords)
        if N < 2:
            return self.idw(target_lat, target_lon)

        # Covariance formulation: C(h) = (sill - nugget) * exp(-3 * (h / range)^2)
        def cov(h):
            h_arr = np.asarray(h, dtype=float)
            return (sill - nugget) * np.exp(-3.0 * (h_arr / spatial_range_km) ** 2)

        # 1. Inter-station distance matrix D
        D = np.zeros((N, N))
        for i in range(N):
            for j in range(i + 1, N):
                d = haversine_distance(coords[i, 0], coords[i, 1], coords[j, 0], coords[j, 1])
                D[i, j] = d
                D[j, i] = d

        # 2. Target distance vector
        d_target = np.array([
            haversine_distance(target_lat, target_lon, coords[i, 0], coords[i, 1])
            for i in range(N)
        ])

        min_idx = int(np.argmin(d_target))
        min_dist = float(d_target[min_idx])

        # Exact proximity check (< 50 meters)
        if min_dist < 0.05:
            return {
                "estimated_aqi": round(float(values[min_idx]), 1),
                "method": "Ordinary Kriging",
                "nearest_station": names[min_idx],
                "distance_km": round(min_dist, 2),
                "kriging_variance": round(nugget, 2),
                "confidence": 0.98,
                "contributing_stations": {names[min_idx]: 1.0}
            }

        # 3. Covariance matrix with diagonal nugget & ridge regularization
        C = cov(D) + np.eye(N) * (nugget + 0.05)
        c0 = cov(d_target)

        # 4. Augmented Ordinary Kriging linear system
        K = np.zeros((N + 1, N + 1))
        K[:N, :N] = C
        K[N, :N] = 1.0
        K[:N, N] = 1.0
        K[N, N] = 0.0

        rhs = np.zeros(N + 1)
        rhs[:N] = c0
        rhs[N] = 1.0

        # 5. Solve linear system
        try:
            sol = np.linalg.solve(K, rhs)
            lambdas = sol[:N]
            lagrange_mu = sol[N]

            # Regularize negative screening artifacts for strictly physical AQI
            if np.any(lambdas < 0):
                lambdas = np.clip(lambdas, 0.0, None)
                sum_w = np.sum(lambdas)
                if sum_w > 0:
                    lambdas = lambdas / sum_w
                else:
                    return self.idw(target_lat, target_lon)

            raw_est = float(np.sum(lambdas * values))
            interpolated_aqi = float(np.clip(raw_est, float(np.min(values)) * 0.85, float(np.max(values)) * 1.15))
            kriging_var = float(max(0.5, abs(sill - np.sum(lambdas * c0) - lagrange_mu)))

        except Exception as e:
            print(f"Kriging matrix solver warning: {e}, falling back to IDW")
            return self.idw(target_lat, target_lon)

        # Confidence decays as kriging variance increases relative to sill
        confidence = float(np.clip(1.0 - (kriging_var / (sill * 1.2)), 0.25, 0.96))

        top_indices = np.argsort(-np.abs(lambdas))[:5]
        top_contrib = {names[i]: round(float(lambdas[i]), 3) for i in top_indices}

        return {
            "estimated_aqi": round(float(interpolated_aqi), 1),
            "method": "Ordinary Kriging (Gaussian Variogram)",
            "nearest_station": names[min_idx],
            "distance_km": round(min_dist, 2),
            "kriging_variance": round(kriging_var, 2),
            "standard_error": round(math.sqrt(kriging_var), 2),
            "confidence": round(confidence, 2),
            "contributing_stations": top_contrib,
            "weights": top_contrib
        }

    # ── 3. Spatial Regional Grid Generator ───────────────────────────────────
    def generate_grid(
        self,
        lat_min: float = 18.44,
        lat_max: float = 18.62,
        lon_min: float = 73.74,
        lon_max: float = 73.96,
        grid_steps: int = 12,
        method: str = "idw"
    ) -> List[dict]:
        """
        Generates a 2D interpolated spatial grid over a city bounding box.
        Used for rendering heatmaps and spatial exposure surfaces.
        """
        lats = np.linspace(lat_min, lat_max, grid_steps)
        lons = np.linspace(lon_min, lon_max, grid_steps)
        grid_points = []

        for lat in lats:
            for lon in lons:
                if method.lower() == "kriging":
                    res = self.kriging(float(lat), float(lon))
                else:
                    res = self.idw(float(lat), float(lon))

                grid_points.append({
                    "lat": round(float(lat), 5),
                    "lon": round(float(lon), 5),
                    "aqi": res["estimated_aqi"],
                    "confidence": res.get("confidence", 0.8)
                })

        return grid_points

    # Alias for naming consistency
    generate_surface_grid = generate_grid



# Singleton helper
_GLOBAL_INTERPOLATOR: Optional[SpatialInterpolator] = None

def get_spatial_interpolator(stations: Optional[Dict[str, Any]] = None) -> SpatialInterpolator:
    global _GLOBAL_INTERPOLATOR
    if stations is None:
        try:
            from data.custom_dataset import load_pune_data
            stations = load_pune_data()
        except Exception:
            stations = {}
    if _GLOBAL_INTERPOLATOR is None or stations is not None:
        _GLOBAL_INTERPOLATOR = SpatialInterpolator(stations)
    return _GLOBAL_INTERPOLATOR

