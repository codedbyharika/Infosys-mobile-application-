"""
FastAPI Microservice for Predictive AQI Forecasting, Spatial Interpolation,
and Route Pollution Exposure Estimation.
"""

import os
import sys
import time
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from data.custom_dataset import load_pune_data
from ml.models import AQIPredictor
from ml.spatial_interpolation import get_spatial_interpolator
from ml.route_exposure import RoutePollutionEstimator
from ml.retrain_pipeline import RetrainingPipeline

# Initialize application
app = FastAPI(
    title="EcoAir Intelligence — AQI Forecasting & Spatial Microservice",
    description=(
        "Production-grade FastAPI service providing multi-step deep recurrent (LSTM/GRU) AQI predictions, "
        "geostatistical spatial interpolation (IDW / Ordinary Kriging), route-level cumulative particulate "
        "exposure quantification, and weekly model retraining triggers."
    ),
    version="2.0.0"
)

# Enable CORS for Streamlit / external web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared singletons (strictly powered by preprocessed Pune telemetry)
_pune_data = load_pune_data()
_all_stations = _pune_data
_predictor = AQIPredictor()
_interpolator = get_spatial_interpolator(_all_stations)
_route_estimator = RoutePollutionEstimator(_interpolator)
_retrain_pipeline = RetrainingPipeline()


# ── Pydantic Request & Response Schemas ──────────────────────────────────────
class ForecastRequest(BaseModel):
    location_name: Optional[str] = Field("BopadiSquare_65", description="Station or city name")
    latitude: Optional[float] = Field(None, description="Optional target latitude")
    longitude: Optional[float] = Field(None, description="Optional target longitude")
    architecture: str = Field("GRU", description="Recurrent neural architecture: 'GRU' (Recommended) or 'LSTM'")
    horizon_hours: int = Field(24, ge=1, le=24, description="Forecast horizon in hours (1-24)")

class ConfidenceInterval(BaseModel):
    step_hour: int
    lower_bound: float
    predicted_aqi: float
    upper_bound: float

class ForecastResponse(BaseModel):
    location: str
    architecture: str
    horizon_hours: int
    current_aqi: float
    predicted_endpoint_aqi: float
    aqi_trajectory: List[float]
    confidence_intervals: List[ConfidenceInterval]
    pollutant_breakdown: Dict[str, List[float]]
    health_category: str
    health_recommendation: str
    model_status: str

class InterpolateRequest(BaseModel):
    latitude: float = Field(..., description="Target latitude coordinate")
    longitude: float = Field(..., description="Target longitude coordinate")
    method: str = Field("idw", description="Spatial interpolation algorithm: 'idw' or 'kriging'")
    power: Optional[float] = Field(2.0, description="IDW distance power exponent")

class InterpolateResponse(BaseModel):
    latitude: float
    longitude: float
    estimated_aqi: float
    method: str
    nearest_station: Optional[str]
    distance_km: Optional[float]
    confidence_score: float
    uncertainty_score: Optional[float]
    contributing_stations: Dict[str, float]

class RouteExposureRequest(BaseModel):
    origin: str = Field("Swargate, Pune", description="Journey origin address or landmark")
    destination: str = Field("Viman Nagar, Pune", description="Journey destination address or landmark")
    transport_mode: str = Field("Car", description="Mode: 'Car', 'Public Transport', 'Motorcycle', 'Cycling', 'Walking'")
    health_profile: str = Field("General User", description="Profile: 'General User', 'Asthmatic / Respiratory', 'Elderly', 'Child / Sensitive'")

class RetrainRequest(BaseModel):
    batch_filename: Optional[str] = Field(None, description="Optional relative or absolute path to new batch file")
    epochs: int = Field(12, ge=2, le=50, description="Number of training epochs")


# ── REST Endpoints ──────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    """Returns microservice operational status, loaded model checkpoints, and training metadata."""
    meta = _predictor.model_meta
    return {
        "status": "HEALTHY",
        "service": "EcoAir Prediction Engine",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "registered_stations": len(_all_stations),
        "loaded_models": {
            "pytorch_lstm": _predictor.lstm_model is not None,
            "pytorch_gru": _predictor.gru_model is not None,
            "numpy_fallback": _predictor.numpy_model is not None
        },
        "model_metadata": meta
    }


@app.get("/stations", tags=["Data"])
def list_stations(limit: int = Query(50, ge=1, le=200)):
    """Lists monitoring stations and their current sensor metrics."""
    res = []
    for name, s in list(_all_stations.items())[:limit]:
        res.append({
            "name": name,
            "city": s.get("city", "Pune"),
            "lat": s.get("lat"),
            "lon": s.get("lon"),
            "aqi": s.get("aqi"),
            "category": s.get("category", "Moderate"),
            "dominant_pollutant": s.get("dominant_pollutant", "PM2.5"),
            "traffic_congestion_score": s.get("traffic_congestion_score", 50.0)
        })
    return {"total": len(_all_stations), "stations": res}


@app.post("/predict/forecast", response_model=ForecastResponse, tags=["Forecasting"])
def predict_aqi_forecast(req: ForecastRequest):
    """
    Generates multi-step ahead AQI forecasts (1–24h) using trained LSTM or GRU recurrent networks.
    Includes 95% confidence intervals and multi-pollutant projections.
    """
    target_loc = req.location_name
    station_data = _all_stations.get(target_loc)

    # Fallback by coordinates if location name not directly found
    if not station_data and req.latitude is not None and req.longitude is not None:
        interp = _interpolator.idw(req.latitude, req.longitude)
        station_data = {
            "aqi": interp["estimated_aqi"],
            "pm25": interp["estimated_aqi"] * 0.35,
            "pm10": interp["estimated_aqi"] * 0.65,
            "no2": 45.0, "o3": 20.0, "co": 110.0, "so2": 5.0,
            "temp": 30.0, "humidity": 55.0, "traffic_congestion_score": 50.0
        }
        target_loc = f"Coord ({req.latitude:.3f}, {req.longitude:.3f})"
    elif not station_data:
        # Default to first Pune station
        first_k = list(_all_stations.keys())[0]
        station_data = _all_stations[first_k]
        target_loc = first_k

    res = _predictor.predict(
        current_data=station_data,
        architecture=req.architecture,
        horizon=req.horizon_hours
    )

    ci_list = [
        ConfidenceInterval(
            step_hour=idx + 1,
            lower_bound=res["lower_bound"][idx],
            predicted_aqi=res["aqi_trajectory"][idx],
            upper_bound=res["upper_bound"][idx]
        )
        for idx in range(len(res["aqi_trajectory"]))
    ]

    return ForecastResponse(
        location=target_loc,
        architecture=res["architecture"],
        horizon_hours=res["horizon_hours"],
        current_aqi=res["current_aqi"],
        predicted_endpoint_aqi=res["predicted_aqi_endpoint"],
        aqi_trajectory=res["aqi_trajectory"],
        confidence_intervals=ci_list,
        pollutant_breakdown={
            "pm25": res["pm25_trajectory"],
            "pm10": res["pm10_trajectory"],
            "no2": res["no2_trajectory"]
        },
        health_category=res["category"],
        health_recommendation=res["recommendation"],
        model_status=res["model_status"]
    )


@app.post("/predict/interpolate", response_model=InterpolateResponse, tags=["Spatial Interpolation"])
def interpolate_aqi_point(req: InterpolateRequest):
    """
    Estimates AQI and spatial uncertainty for arbitrary user coordinates
    using Inverse Distance Weighting (IDW) or Ordinary Kriging with a Gaussian Variogram.
    """
    if req.method.lower() == "kriging":
        res = _interpolator.kriging(req.latitude, req.longitude)
        uncertainty = res.get("standard_error") or res.get("kriging_variance")
    else:
        res = _interpolator.idw(req.latitude, req.longitude, power=req.power)
        uncertainty = res.get("uncertainty_score")

    return InterpolateResponse(
        latitude=req.latitude,
        longitude=req.longitude,
        estimated_aqi=res["estimated_aqi"],
        method=res["method"],
        nearest_station=res.get("nearest_station"),
        distance_km=res.get("distance_km"),
        confidence_score=res.get("confidence", 0.8),
        uncertainty_score=uncertainty,
        contributing_stations=res.get("contributing_stations", {})
    )


@app.post("/route/exposure", tags=["Route Advisory"])
def calculate_route_exposure(req: RouteExposureRequest):
    """
    Evaluates travel routes by sampling waypoints, performing spatial AQI interpolation,
    and calculating cumulative particulate exposure. Compares arterial route vs clean corridor.
    """
    analysis = _route_estimator.estimate_exposure(
        origin=req.origin,
        destination=req.destination,
        transport_mode=req.transport_mode,
        health_profile=req.health_profile
    )
    return analysis


@app.post("/retrain", tags=["Model Lifecycle"])
def trigger_retraining(req: RetrainRequest):
    """
    Triggers automated model retraining pipeline on new batch data.
    Updates LSTM and GRU model checkpoints and outputs validation metrics.
    """
    res = _retrain_pipeline.run_weekly_retraining(
        new_batch_path=req.batch_filename,
        epochs=req.epochs
    )
    # Refresh predictor artifacts
    _predictor._load_artifacts()
    return res
