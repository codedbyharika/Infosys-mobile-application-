# AI-Powered Environmental Intelligence System for Air Quality Prediction and Smart Mobility Recommendations

A full-stack, location-aware environmental intelligence dashboard built with **Python & Streamlit**. This platform integrates real-time air quality monitoring, deep recurrent neural network forecasting, route pollution exposure optimization, and proactive health alerts.

---

## 🌟 Key Modules

The project is structured strictly across **4 Core Modules** corresponding to the academic project requirements:

### 📍 Module 1: Location & AQI Real-Time Data Integration (Weeks 1–2)
- **Geolocation Services:** Live GPS detection and manual location selector for major metropolitan clusters (Delhi NCR, Mumbai, Bengaluru, Hyderabad, Chennai, Kolkata).
- **Multi-Pollutant Telemetry:** Real-time AQI and detailed concentrations for $PM_{2.5}$, $PM_{10}$, $NO_2$, $O_3$, $CO$, and $SO_2$.
- **Meteorology Fusion:** Blends temperature, relative humidity, wind speed & vectors, and atmospheric conditions.
- **Neighborhood Map:** Interactive Folium map displaying physical monitoring stations and localized dispersion zones.
- **Health Profile Customization:** Personalized profiles (General, Asthmatic, Elderly, Child) with configurable AQI breach alert thresholds.

### 📈 Module 2: Predictive AQI Forecasting Model (Weeks 3–4) — ✅ Completed
- **Recurrent Neural Architectures:** Fully trained PyTorch `LSTM` and `GRU` models with 2-layer stacked recurrence and dropout projection.
- **Multi-Step 1–24 Hour Forecasting:** Generates forward trajectories for overall AQI and specific chemical pollutants ($PM_{2.5}$, $PM_{10}$, $NO_2$) with dynamic **95% Confidence Interval bands**.
- **Spatial Geostatistical Interpolation:** Implements **Inverse Distance Weighting (IDW)** and **Ordinary Kriging** (Gaussian variogram with estimation variance $\sigma_K^2$) to predict AQI at arbitrary user coordinates between physical monitoring stations.
- **Route Particulate Exposure Engine:** Samples polyline waypoints via Google Directions API, performs spatial AQI interpolation, and computes cumulative particulate exposure indices across travel modes and health profiles.
- **FastAPI Prediction Microservice:** Production-grade REST API server exposing `/predict/forecast`, `/predict/interpolate`, `/route/exposure`, `/retrain`, and `/stations` with interactive OpenAPI Swagger documentation (`/docs`).
- **Weekly Automated Retraining Pipeline:** Automated batch ingestion, schema validation, feature normalization, model fine-tuning, and versioned checkpoint registry.

### 🗺️ Module 3: Route Advisory, Dashboard & Push Notifications (Weeks 5–6)
- **Journey Travel Plan:** Origin, destination, departure time, and transport mode selection (`Car`, `Public Transport`, `Motorcycle`, `Cycling`, `Walking`).
- **Cumulative Exposure Engine:** Numerical exposure index comparing Route A (direct arterial) vs Route B (clean air corridor).
- **Alternative Clean-Air Recommendation:** Visual comparison cards with percentage exposure reduction metrics.
- **Interactive Mobility Map:** Route polylines, start/destination pins, and high-pollution congestion hotspot overlays.
- **Push Notification Hub:** Simulated alert feeds and user notification preference toggles.

### ⚙️ Module 4: System Integration, Testing & Project Finalization (Weeks 7–8)
- **Subsystem Status Matrix:** Operational status monitoring across all services (Location, Ingestion, Weather, ML Inference, Routing, FCM, UI).
- **Visual Pipeline Flow:** 8-step visual execution diagram from geo-capture to proactive mobility alerts.
- **Automated QA Test Suite:** Unit/integration test results dashboard with simulated execution harness.
- **Project Roadmap:** Weekly milestone trackers across Weeks 1–8.
- **Technical Documentation:** Expandable architecture, dataflow diagrams, API contracts, and evaluation methodology.

---

## 📁 Project Directory Structure

```
aqi-infosys/
│
├── app.py                              # Main application entry point & overview hub
├── requirements.txt                    # Production dependencies (PyTorch, FastAPI, Streamlit, etc.)
├── README.md                           # Comprehensive documentation & extension guide
│
├── api/
│   ├── __init__.py
│   └── main.py                         # FastAPI microservice for ML predictions & routing
│
├── ml/
│   ├── __init__.py
│   ├── models.py                       # PyTorch LSTM / GRU architectures & predictor facade
│   ├── train.py                        # Model training on Pune telemetry with sequence creation
│   ├── spatial_interpolation.py        # IDW & Ordinary Kriging geostatistical engines
│   ├── route_exposure.py               # Google Directions API & waypoint exposure estimator
│   └── retrain_pipeline.py             # Weekly automated batch ingestion & retraining
│
├── models/
│   ├── aqi_lstm.pt                     # Trained PyTorch LSTM checkpoint weights
│   ├── aqi_gru.pt                      # Trained PyTorch GRU checkpoint weights
│   ├── numpy_recurrent_weights.pkl     # Pure-NumPy sub-millisecond execution weights
│   ├── scaler.pkl                      # Fitted MinMaxScaler for 10 environmental features
│   └── model_meta.json                 # Training history, sample count, and validation metrics
│
├── pages/
│   ├── 1_Location_AQI_RealTime.py      # Module 1: Location & AQI Real-Time Data Integration
│   ├── 2_Predictive_AQI_Forecasting.py # Module 2: Recurrent Forecasting & Spatial Interpolation UI
│   ├── 3_Route_Advisory_Notifications.py # Module 3: Route Advisory & Cumulative Exposure
│   └── 4_System_Integration_Testing.py # Module 4: System Integration & QA Suite
│
├── components/
│   ├── __init__.py
│   ├── metrics.py                      # Reusable AQI hero & pollutant cards
│   ├── charts.py                       # Plotly historical & predictive forecast charts
│   ├── maps.py                         # Folium interactive pollution & route maps
│   └── alerts.py                       # Health advisories & notification center
│
└── data/
    ├── __init__.py
    ├── Pune_Dataset(processed).xlsx    # Raw multi-station Pune SmartCity dataset (103k rows)
    ├── pune_aqi_ml_clean.csv           # Clean, preprocessed ML-ready tabular dataset
    ├── pune_preprocessing_summary.json # Feature statistics, outlier counts, and metadata
    ├── pune_dataset_cache.pkl          # Cached station dictionary for instant startup
    └── demo_data.py                    # Centralized data models & metro cluster feeds
```

---

## 🚀 Installation & Running

### 1. Prerequisites
Ensure Python (version 3.10, 3.11, 3.12, or 3.13) is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```

*The application will open in your default browser at `http://localhost:8501`.*

---

## 🔌 Future Backend Integration Guide

The application is architected to allow backend modules to be plugged in seamlessly:

1. **Module 1 (Live APIs):** Replace simulated calls in `data/demo_data.py` with calls to:
   - `https://api.openaq.org/v2/` (OpenAQ API)
   - `https://api.waqi.info/feed/` (WAQI API)
   - `https://api.openweathermap.org/data/3.0/` (OpenWeatherMap API)
2. **Module 2 (Trained ML Weights):** Connect your trained PyTorch `LSTM`/`GRU` model `.pt` weights inside `pages/2_📈_Predictive_AQI_Forecasting.py` to replace the mathematical diurnal generator.
3. **Module 3 (Google Directions & FCM):** Plug in Google Maps Directions API for live waypoint polyline decoding and Firebase Cloud Messaging (FCM) SDK for real push tokens.
4. **Module 4 (InfluxDB Database):** Connect the InfluxDB client in `data/` for high-frequency time-series persistence.
