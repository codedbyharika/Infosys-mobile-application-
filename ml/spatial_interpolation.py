"""
Spatial Interpolation Module for Arbitrary Location AQI Estimation.
Implements:
  1. Inverse Distance Weighting (IDW)
  2. Ordinary Kriging (Gaussian Variogram with Kriging Estimation Variance / Uncertainty)
  3. Spatial Meshgrid Generator for Regional Dispersion Mapping
"""

import math
import re
import numpy as np
from typing import Dict, List, Tuple, Optional, Any


def clean_station_name(stn_id: str) -> str:
    """Formats station key into professional, human-readable station name."""
    if not stn_id:
        return ""
    # Strip trailing numbers like _65, _14, _5, _01
    name = re.sub(r'_\d+$', '', str(stn_id)).replace('_', ' ')
    replacements = {
        'BopadiSquare': 'Bopodi Square',
        'Bopodi Square': 'Bopodi Square',
        'Karve Statue Square': 'Karve Statue Square',
        'Lullanagar Square': 'Lullanagar Square',
        'Hadapsar Gadital': 'Hadapsar Gadital',
        'PMPML Bus Depot Deccan': 'PMPML Bus Depot Deccan',
        'Goodluck Square Cafe': 'Goodluck Square Cafe',
        'Chitale Bandhu Corner': 'Chitale Bandhu Corner',
        'Pune Railway Station': 'Pune Railway Station',
        'Rajashri Shahu Bus stand': 'Rajashri Shahu Bus Stand',
        'Dr Baba Saheb Ambedkar Sethu Junction': 'Dr. Ambedkar Setu Junction'
    }
    return replacements.get(name, name).strip()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two geographic coordinates in kilometers.
    Includes IEEE 754 numerical clamping to prevent domain errors on boundary or antipodal points.
    """
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    a = min(1.0, max(0.0, a))
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
        Normalized linear combination: Z_hat = sum(w_i * Z_i) / sum(w_i)
        """
        coords, values, names = self._extract_points()
        if len(coords) == 0:
            return {
                "estimated_aqi": 75.0,
                "method": "IDW",
                "confidence": 0.5,
                "nearest_station": None,
                "nearest_station_id": None,
                "contributing_stations": {}
            }

        distances = []
        for i in range(len(coords)):
            d = haversine_distance(target_lat, target_lon, coords[i, 0], coords[i, 1])
            distances.append(d)

        distances = np.array(distances)
        min_idx = int(np.argmin(distances))
        min_dist = float(distances[min_idx])
        clean_stn = clean_station_name(names[min_idx])

        # Exact station proximity check (< 50 meters)
        if min_dist < 0.05:
            return {
                "estimated_aqi": round(float(values[min_idx]), 1),
                "method": "IDW",
                "nearest_station": names[min_idx],
                "nearest_station_id": names[min_idx],
                "nearest_station_clean": clean_stn,
                "distance_km": round(min_dist, 2),
                "confidence": 0.98,
                "uncertainty_score": 2.0,
                "standard_error": 2.0,
                "contributing_stations": {names[min_idx]: 1.0},
                "weights": {names[min_idx]: 1.0}
            }

        weights = 1.0 / (distances ** power)
        normalized_weights = weights / np.sum(weights)
        interpolated_aqi = float(np.sum(normalized_weights * values))

        # Geostatistical confidence: decays within city bounds (<=35km), exponential decay outside
        if min_dist <= 35.0:
            confidence = float(np.clip(1.0 - (min_dist / 40.0), 0.20, 0.95))
        else:
            confidence = float(max(0.05, 0.20 * math.exp(-(min_dist - 35.0) / 15.0)))

        top_indices = np.argsort(-normalized_weights)[:5]
        weight_breakdown = {
            names[i]: round(float(normalized_weights[i]), 3)
            for i in top_indices
        }

        return {
            "estimated_aqi": round(interpolated_aqi, 1),
            "method": "IDW",
            "power": power,
            "nearest_station": names[min_idx],
            "nearest_station_id": names[min_idx],
            "nearest_station_clean": clean_stn,
            "distance_km": round(min_dist, 2),
            "confidence": round(confidence, 2),
            "uncertainty_score": round(float(min_dist * 1.8), 1),
            "standard_error": round(float(min_dist * 1.8), 1),
            "contributing_stations": weight_breakdown,
            "weights": weight_breakdown
        }

    # ── 2. Ordinary Kriging (Exponential & Gaussian Variograms) ───────────────
    def kriging(
        self,
        target_lat: float,
        target_lon: float,
        nugget: float = 2.0,
        sill: float = 120.0,
        spatial_range_km: float = 6.0,
        variogram_model: str = "exponential"
    ) -> dict:
        """
        Estimates AQI at (target_lat, target_lon) using Ordinary Kriging.
        Default variogram is Exponential (gamma(h) = nugget + (sill - nugget)*(1 - exp(-3*h/a))),
        calibrated for urban-scale Pune spatial autocorrelation structures (inter-station range ~6km).
        Outputs Kriging estimation variance sigma_K^2 and standard error as spatial uncertainty measures.
        """
        coords, values, names = self._extract_points()
        N = len(coords)
        if N < 2:
            return self.idw(target_lat, target_lon)

        # Covariance formulation:
        def cov(h):
            h_arr = np.asarray(h, dtype=float)
            if variogram_model.lower() == "gaussian":
                return (sill - nugget) * np.exp(-3.0 * (h_arr / spatial_range_km) ** 2)
            elif variogram_model.lower() == "spherical":
                hr = np.clip(h_arr / spatial_range_km, 0.0, 1.0)
                return (sill - nugget) * (1.0 - (1.5 * hr - 0.5 * hr ** 3))
            else:  # Exponential (Best for dense urban environmental stations)
                return (sill - nugget) * np.exp(-3.0 * (h_arr / spatial_range_km))

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
        clean_stn = clean_station_name(names[min_idx])

        # Exact proximity check (< 50 meters)
        if min_dist < 0.05:
            st_err = round(math.sqrt(nugget), 2)
            return {
                "estimated_aqi": round(float(values[min_idx]), 1),
                "method": f"Ordinary Kriging ({variogram_model.capitalize()})",
                "nearest_station": names[min_idx],
                "nearest_station_id": names[min_idx],
                "nearest_station_clean": clean_stn,
                "distance_km": round(min_dist, 2),
                "kriging_variance": round(nugget, 2),
                "standard_error": st_err,
                "uncertainty_score": st_err,
                "confidence": 0.98,
                "contributing_stations": {names[min_idx]: 1.0},
                "weights": {names[min_idx]: 1.0}
            }

        # 3. Covariance matrix with diagonal nugget & ridge regularization
        C = cov(D) + np.eye(N) * (nugget + 0.05)
        c0 = cov(d_target)

        # 4. Augmented Ordinary Kriging linear system: [C 1; 1^T 0] * [lambda; mu] = [c0; 1]
        K = np.zeros((N + 1, N + 1))
        K[:N, :N] = C
        K[N, :N] = 1.0
        K[:N, N] = 1.0
        K[N, N] = 0.0

        rhs = np.zeros(N + 1)
        rhs[:N] = c0
        rhs[N] = 1.0

        # 5. Solve linear system with robust pseudo-inverse fallback
        try:
            try:
                sol = np.linalg.solve(K, rhs)
            except np.linalg.LinAlgError:
                sol = np.linalg.lstsq(K, rhs, rcond=1e-7)[0]

            lambdas = sol[:N]
            lagrange_mu = sol[N]

            # Regularize negative screening artifacts for physical realism
            if np.any(lambdas < 0):
                lambdas = np.clip(lambdas, 0.0, None)
                sum_w = np.sum(lambdas)
                if sum_w > 0:
                    lambdas = lambdas / sum_w
                else:
                    return self.idw(target_lat, target_lon)

            raw_est = float(np.sum(lambdas * values))
            interpolated_aqi = float(np.clip(raw_est, float(np.min(values)) * 0.85, float(np.max(values)) * 1.15))

            # Quadratic estimation variance: Var(Z - Z_hat) = C(0) - 2 * lambda^T * c0 + lambda^T * C * lambda
            quad_var = float(sill - 2.0 * np.dot(lambdas, c0) + np.dot(lambdas, C @ lambdas))
            kriging_var = float(np.clip(quad_var, nugget, sill * 1.5))

        except Exception as e:
            print(f"Kriging matrix solver warning: {e}, falling back to IDW")
            return self.idw(target_lat, target_lon)

        # Confidence decays as kriging variance increases and distance exceeds spatial range
        base_conf = max(0.10, 1.0 - (kriging_var / (sill * 1.2)))
        dist_factor = math.exp(-max(0.0, min_dist - spatial_range_km) / 8.0)
        confidence = float(np.clip(base_conf * dist_factor, 0.05, 0.98))

        top_indices = np.argsort(-np.abs(lambdas))[:5]
        top_contrib = {names[i]: round(float(lambdas[i]), 3) for i in top_indices if lambdas[i] > 0.001}
        std_err = round(math.sqrt(kriging_var), 2)

        return {
            "estimated_aqi": round(interpolated_aqi, 1),
            "method": f"Ordinary Kriging ({variogram_model.capitalize()})",
            "nearest_station": names[min_idx],
            "nearest_station_id": names[min_idx],
            "nearest_station_clean": clean_stn,
            "distance_km": round(min_dist, 2),
            "kriging_variance": round(kriging_var, 2),
            "standard_error": std_err,
            "uncertainty_score": std_err,
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
                    "confidence": res.get("confidence", 0.8),
                    "uncertainty": res.get("uncertainty_score", 5.0)
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
