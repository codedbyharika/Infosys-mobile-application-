# EcoAir Intelligence (AirSense) — AI Environmental Platform & Smart Mobility System

[![Flutter](https://img.shields.io/badge/Flutter-3.0%2B-02569B.svg?style=flat&logo=flutter)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?style=flat&logo=python)](https://www.python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-LSTM%20%2F%20GRU-EE4C2C.svg?style=flat&logo=pytorch)](https://pytorch.org)
[![CPCB Standard](https://img.shields.io/badge/Air%20Quality%20Standard-CPCB%20NAAQI-16A34A.svg?style=flat)](https://cpcb.nic.in)
[![QA Test Suite](https://img.shields.io/badge/QA%20Tests-24%2F24%20PASS%20(100%25)-success.svg?style=flat)]()

**EcoAir Intelligence** (AirSense) is a full-stack, enterprise-grade environmental intelligence and predictive smart-mobility platform. Built using **FastAPI (ASGI microservice)**, a native **Flutter Cross-Platform Mobile Application (`mobile_app/`)**, and **Deep Recurrent Neural Networks (PyTorch LSTM/GRU with pure-NumPy runtime fallback)**, the platform ingests multi-station urban sensor telemetry, performs geostatistical spatial interpolation, projects multi-step ahead air quality trajectories, and optimizes travel routes to minimize human particulate inhalation.

---

## 🌟 Executive Architectural Overview

```
                          ┌────────────────────────────────────────────────────────┐
                          │         Pune SmartCity Telemetry Mesh Network          │
                          │   (10 Continuous Ambient Air Quality Stations, 103k rows)│
                          └───────────────────────────┬────────────────────────────┘
                                                      │
                                                      ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                       Data Processing & CPCB Engine                                    │
 │  • Sub-index Piecewise Linear Interpolation (PM2.5, PM10, NO2, SO2, CO, O3)                            │
 │  • Acoustic Decibel & Vehicular Combustion Traffic Correlation (Congestion Score 15-95)                │
 │  • Meteorological Vector Ingestion (Temperature, Relative Humidity, Inversion Pressure)                │
 └────────────────────────────┬───────────────────────────────────────────────┬───────────────────────────┘
                              │                                               │
                              ▼                                               ▼
 ┌───────────────────────────────────────────────┐     ┌──────────────────────────────────────────────────┐
 │       Deep Recurrent Forecasting Engine       │     │        Spatial Geostatistical GIS Engine         │
 │  • Stacked 2-Layer PyTorch GRU & LSTM         │     │  • Inverse Distance Weighting (IDW, power p=2.0) │
 │  • Anchored Continuous Delta Math (Zero-jump) │     │  • Ordinary Kriging (Gaussian Variogram)         │
 │  • Expanding 95% Confidence Interval Bands    │     │  • Estimation Variance & Spatial Uncertainty     │
 └────────────────────────────┬──────────────────┘     └──────────────────────┬───────────────────────────┘
                              │                                               │
                              └───────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                              Travel Route Particulate Exposure Estimator                               │
 │  • 3 Distinct Routes: Route 1 (Arterial), Route 2 (Alternative), Route 3 (Clean-Air Eco Corridor)      │
 │  • Waypoint Polyline Discretization & Spatial Interpolation                                            │
 │  • Respiratory Ventilation Modifiers (Walking: 1.4x, Cycling: 1.4x, Motorcycle: 1.25x, Car: 0.65x)     │
 │  • Vulnerability Profiling (Asthmatic: 1.4x, Elderly: 1.25x, Child: 1.20x, General: 1.0x)              │
 └────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘
                                              │
                                              ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                              Production FastAPI Microservice & REST APIs                               │
 │  • OpenAPI Swagger Documentation (/docs) & JSON Schemas                                                │
 │  • Telemetry endpoints (/api/stations, /api/stations/{id}/history, /api/station-comparison)           │
 │  • Predictive endpoints (/api/predict/forecast, /api/predict/interpolate, /api/route/exposure)         │
 └────────────────────────────────────────────┬───────────────────────────────────────────────────────────┘
                                              │
                                              ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                Modern Responsive Single Page Web App (SPA)                             │
 │  • High-Contrast Professional Surface Adhering to CPCB Indian Standards                                │
 │  • Real-time Metric Filters (AQI, PM2.5, PM10) & Station Selectors                                     │
 │  • Interactive GIS Leaflet Maps with Waypoints, Pins, and Hotspot Glow Zones                           │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Core Modules (Academic Milestone Alignment)

The platform is organized strictly across **4 Core Engineering Modules** (Weeks 1–8):

### 📍 Module 1: Location & AQI Real-Time Data Integration (Weeks 1–2)
- **Pune SmartCity Telemetry Network:** Ingests live and cached observations from 10 urban nodes (Bopodi Square, Deccan Bus Depot, Pune Railway Station, Hadapsar Gadital, etc.).
- **CPCB 6-Tier National Air Quality Standard:** Complete implementation of official Indian CPCB sub-index breakpoints:
  - `0–50`: **Good** (`#16A34A`)
  - `51–100`: **Satisfactory / Moderate** (`#CA8A04`)
  - `101–150`: **Unhealthy for Sensitive Groups** (`#EA580C`)
  - `151–200`: **Unhealthy / Poor** (`#DC2626`)
  - `201–300`: **Very Unhealthy / Very Poor** (`#7C3AED`)
  - `301+`: **Hazardous / Severe** (`#991B1B`)
- **Multi-Pollutant Sub-Index Analytics:** Breakdowns for $PM_{2.5}$, $PM_{10}$, $NO_2$, $SO_2$, $CO$, and $O_3$ with dominant pollutant tracking.
- **Traffic Congestion Index:** Correlates junction acoustic noise ($\text{dB}$) and vehicular combustion gases ($NO_2, CO$) into a normalized congestion score (15–95).
- **Personalized Health Profiles:** Tailored guidance and alert thresholds for General Users, Asthmatics, Elderly Individuals, and Children.

### 📈 Module 2: Predictive Recurrent Forecasting & Spatial Interpolation (Weeks 3–4)
- **Recurrent Neural Architectures:** Fully trained 2-layer stacked PyTorch `GRU` and `LSTM` networks with hidden projection heads and dropout regularization.
- **Anchored Continuous Delta Math:** Resolves training cluster bias by anchoring the forecast to the station's actual sensor baseline:
  $$\mathbf{Y}_h = y_0 + (\mathbf{\hat{Y}}_h - \mathbf{\hat{Y}}_0)$$
  Eliminates artificial jumps, ensuring that low-AQI stations (e.g. 28–34) and high-AQI stations (e.g. 108) evolve smoothly along their neural diurnal trajectories.
- **95% Confidence Interval Cone:** Temporal variance expansion based on error propagation:
  $$\sigma_h = \sigma_0 + \gamma \sqrt{h}, \quad \text{CI}_{0.95} = \hat{y}_h \pm 1.96 \cdot \sigma_h$$
- **Geostatistical Spatial Interpolation:**
  - **Inverse Distance Weighting (IDW):** Fast distance-decay interpolation ($p=2.0$).
  - **Ordinary Kriging:** Gaussian semivariogram modeling with estimation variance and spatial uncertainty quantification.
- **Automated Model Retraining:** Weekly batch retraining pipeline (`/api/retrain`) with automated feature normalization, validation loss tracking, and versioned checkpoint registry.

### 🗺️ Module 3: Travel Route Particulate Exposure Estimator (Weeks 5–6)
- **Tri-Route Comparative Analysis:** Compares Route 1 (Direct Arterial Corridor), Route 2 (Alternative Mixed Corridor), and Route 3 (Clean-Air Eco Corridor).
- **Inhalation Quantification:** Computes cumulative particulate exposure incorporating duration, ambient $AQI$, physical ventilation factor, and user vulnerability profile:
  $$\text{Exposure Score} = \frac{\overline{\text{AQI}}}{100} \cdot \left(\frac{\min(90, T)}{30}\right) \cdot M_{\text{mode}} \cdot H_{\text{profile}} \cdot 18.0$$
- **Interactive Mobility GIS:** Leaflet map with custom Start ('S') and Destination ('D') pins, colored geometric route polylines, recommended eco-corridor halos, and high-pollution hotspot exclusion rings.
- **Instant Controls:** Synchronized origin/destination dropdowns, quick station pickers, and route swap (`⇄`) buttons.

### ⚙️ Module 4: System Integration, Operational Matrix & QA Testing (Weeks 7–8)
- **Subsystem Status Matrix:** Real-time health monitoring across all subsystems (Ingestion, Weather, Inference, Routing, Push Notifications, Web SPA).
- **8-Step Visual Pipeline Flow:** Visual execution flow from GPS coordinate capture to advisory notification dispatch.
- **Live Automated QA Test Suite:** Integrated testing harness directly executable from both the web interface and the CLI.

### 📱 Milestone 3: Progressive Web Application (PWA) & Mobile Dashboard (Weeks 9–10)
- **Native Mobile Experience:** Responsive mobile-first interface featuring a sticky bottom navigation bar (Dashboard, AQI Map, Routes, My AQI, Alerts) and app install prompt (`beforeinstallprompt`).
- **Offline Reliability & Service Worker:** Cache-first strategy for static resources, network-first for telemetry APIs, and full offline fallback caching (`sw.js`, `manifest.json`).
- **Personal AQI Exposure History:** Persistent journal (`localStorage`) calculating cumulative inhaled particulate mass ($\mu\text{g}$), trip exposure scores, filterable by transit mode (Car, Metro, Bus, Bike, Walk) with CSV export.
- **Dynamic Travel Advisory Overlays:** Real-time color-coded waypoint circles and health advisories projected onto the Leaflet mobility map with instant "Save to History" logging.
- **Notification Preference Management:** Interactive AQI hazard threshold slider (50–300 AQI), sensitive health profile configuration, browser Web Push alerts, and threshold breach simulations.

---

## 📁 Repository Structure

```
aqi-infosys/
│
├── run.py                              # Production server launcher (FastAPI + SPA)
├── requirements.txt                    # Python runtime dependencies
├── README.md                           # Comprehensive documentation & architecture guide
│
├── api/
│   ├── __init__.py
│   └── main.py                         # FastAPI ASGI microservice & REST endpoints
│
├── ml/
│   ├── __init__.py
│   ├── models.py                       # PyTorch LSTM/GRU & NumPy recurrent predictor
│   ├── spatial_interpolation.py        # IDW & Ordinary Kriging geostatistical engines
│   ├── route_exposure.py               # Route particulate exposure estimator & waypoints
│   ├── train.py                        # Model training on historical sequences
│   └── retrain_pipeline.py             # Automated weekly batch retraining pipeline
│
├── models/
│   ├── aqi_lstm.pt                     # PyTorch LSTM checkpoint weights
│   ├── aqi_gru.pt                      # PyTorch GRU checkpoint weights
│   ├── numpy_recurrent_weights.pkl     # Pure-NumPy instant inference weights
│   ├── scaler.pkl                      # Fitted MinMaxScaler for 10 environmental features
│   └── model_meta.json                 # Training history, sample count, and validation metrics
│
├── data/
│   ├── __init__.py
│   ├── Pune_Dataset(processed).xlsx    # Raw multi-station Pune SmartCity dataset (103k rows)
│   ├── pune_aqi_ml_clean.csv           # Preprocessed ML tabular dataset
│   ├── pune_dataset_cache.pkl          # Cached station dictionary for instant startup
│   ├── pune_preprocessing_summary.json # Feature statistics and outlier metadata
│   ├── custom_dataset.py               # CPCB sub-index calculations & station aggregator
│   └── custom_dataset.py               # Pune dataset ingestion, health profiles, and CPCB tables
├── mobile_app/                         # Flutter Cross-Platform Mobile Application (Android / iOS / Web)
│   ├── pubspec.yaml                    # Flutter dependencies (http, fl_chart, shared_preferences, intl)
│   ├── README.md                       # Mobile app architecture & emulator setup instructions
│   └── lib/
│       ├── main.dart                   # Mobile app entrypoint & AppState binder
│       ├── config/                     # CPCB 6-tier theme, colors & dynamic API endpoint config
│       ├── models/                     # Station, Forecast, RouteExposure, TripRecord, KPISummary
│       ├── providers/                  # Central reactive AppState ChangeNotifier
│       ├── services/                   # ApiService, StorageService (SharedPreferences), OfflineDataService
│       ├── widgets/                    # AqiGauge, PollutantCard, StationBottomSheet, BreachAlertDialog
│       └── screens/                    # Dashboard, GIS Map, Route Advisory, History, Forecast, Settings
│
├── static/
│   ├── index.html                      # Modern Responsive Single Page Application (SPA)
│   ├── css/
│   │   └── style.css                   # High-contrast CSS design system adhering to CPCB
│   └── js/
│       ├── api.js                      # REST client communicating with FastAPI microservice
│       ├── app.js                      # Application controller, tab router, and state management
│       ├── charts.js                   # Chart.js line and bar chart renderers
│       └── map.js                      # Leaflet GIS engine, polyline drawers, and station markers
│
└── tests/
    ├── __init__.py
    ├── test_ml_engine.py               # Unit tests: GRU/LSTM models, IDW, Kriging, Route Exposure
    ├── test_api_endpoints.py           # Integration tests: All FastAPI REST endpoints
    ├── test_frontend_integrity.py      # Contract tests: HTML DOM IDs, API endpoints, CSS tokens
    └── run_all_tests.py                # Master executive test runner & formatted QA reporter
```

---

## 🔌 Complete REST API Reference

The FastAPI server provides automated OpenAPI Swagger documentation at `/docs` and ReDoc at `/redoc`.

| Method | Endpoint | Description | Sample Request / Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves modern Single Page Web Application | Browser access |
| `GET` | `/health` or `/api/health` | System health, registered stations, loaded models | None |
| `GET` | `/api/stations` | All 10 monitoring stations with complete telemetry | `?limit=50` |
| `GET` | `/api/stations/{name}` | Individual station telemetry and meteorological data | `name="BopadiSquare_65"` |
| `GET` | `/api/stations/{name}/history` | Chronological sensor records (24–72 hours) | `lookback=24` |
| `GET` | `/api/station-comparison` | Comparative telemetry sorted descending by AQI | None |
| `GET` | `/api/kpi-summary` | Executive dashboard KPI statistics and CPCB distribution | None |
| `GET` | `/api/predictions-vs-actual` | Validation table comparing predictions vs actuals | None |
| `POST` | `/api/predict/forecast` | Multi-step recurrent forecast (1–24h) with 95% CI | `{"location_name": "BopadiSquare_65", "architecture": "GRU", "horizon_hours": 24}` |
| `POST` | `/api/predict/interpolate` | Spatial AQI interpolation (IDW or Ordinary Kriging) | `{"latitude": 18.5204, "longitude": 73.8567, "method": "kriging"}` |
| `POST` | `/api/route/exposure` | 3-route exposure calculation and eco corridor advisory | `{"origin": "Swargate", "destination": "Viman Nagar", "transport_mode": "Car", "health_profile": "General User"}` |
| `GET` | `/api/health-profiles` | Configurable health profiles and alert thresholds | None |
| `GET` | `/api/system/status` | Subsystem operational matrix (Module 4) | None |
| `POST` | `/api/system/tests/run` | Executes automated integration test harness | None |
| `POST` | `/api/retrain` | Triggers weekly automated model retraining pipeline | `{"epochs": 12}` |

---

## 🧪 Comprehensive Testing Suite

The repository includes an enterprise-grade automated testing suite designed by senior test engineering standards:

### 1. Test Suite Modules
- **`tests/test_ml_engine.py`**:
  - Telemetry dataset ingestion integrity
  - CPCB 6-tier breakpoint boundaries and color mapping
  - PyTorch/NumPy GRU and LSTM 24-step forecast validation
  - Mathematical monotonicity of confidence bounds ($\text{lower} \le \text{pred} \le \text{upper}$)
  - Haversine geographic distance verification
  - IDW interpolation at exact station coordinates
  - Ordinary Kriging Gaussian variogram estimation and variance scores
  - Multi-route particulate exposure calculation and clean-air reduction verification
  - Transport mode ventilation and health vulnerability multipliers
- **`tests/test_api_endpoints.py`**:
  - Static SPA HTML delivery and critical container existence
  - Static asset accessibility (`style.css`, `api.js`, `app.js`, `charts.js`, `map.js`)
  - Operational health check endpoints (`/health` and `/api/health`)
  - Stations telemetry list and individual station lookups (valid + 404 cases)
  - Station historical timeseries API
  - Station comparison analytics with descending sort verification
  - Forecast endpoints across GRU and LSTM with 6h, 12h, and 24h horizons
  - Spatial interpolation endpoints (IDW and Kriging)
  - Route exposure analysis endpoint
  - Executive KPI summary and Predictions vs Actual validation tables
- **`tests/test_frontend_integrity.py`**:
  - HTML/JavaScript DOM contract: Asserts that every DOM ID queried by JS exists in `index.html`
  - REST API contract: Asserts that every API endpoint invoked in `api.js` is registered on FastAPI
  - CSS design system token verification: Asserts required design variables exist in `style.css`

### 2. Executing the Test Suite
Run the master executive test runner:
```bash
python tests/run_all_tests.py
```
*(Or via Python's built-in unittest runner:)*
```bash
python -m unittest discover -s tests -p "test_*.py"
```

Expected Output:
```
==============================================================================
      ECOAIR INTELLIGENCE (AIRSENSE) — EXECUTIVE QA VERIFICATION SUITE
==============================================================================
  Target Environment: win32 | Python 3.12.x
  Project Root:       C:\Users\...\aqi-infosys
==============================================================================

==> Running: 1. ML & Geostatistical Engines Suite (9 test cases)...
    [PASS] Completed 9/9 tests passed in this suite.

==> Running: 2. REST API Microservice Suite (12 test cases)...
    [PASS] Completed 12/12 tests passed in this suite.

==> Running: 3. Frontend Integrity & Design System Suite (3 test cases)...
    [PASS] Completed 3/3 tests passed in this suite.

==============================================================================
                          FINAL QA SUMMARY REPORT
==============================================================================
  Total Test Cases Executed: 24
  Passed:                    24
  Failures:                  0
  Errors:                    0
  Total Execution Duration:  1.14s
  Success Rate:              100.0%
==============================================================================
  [SUCCESS] All system suites passed! Application is 100% demo-ready.
==============================================================================
```

---

## 🚀 Installation & Running

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Modern web browser (Chrome, Edge, Firefox, Safari).

### 2. Setup Virtual Environment & Dependencies
```bash
# Clone the repository
git clone https://github.com/YourUsername/aqi-infosys.git
cd aqi-infosys

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Launch the Production Application
```bash
python run.py
```
*(Or run directly via Uvicorn):*
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Access the Application
- **Interactive Web Application:** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web browser.
- **Interactive OpenAPI Swagger Docs:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- **ReDoc API Documentation:** Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

---

## 📊 Evaluation & Mathematical Formulation

### 1. CPCB Breakpoint Formulation
Each pollutant $p$ with observed concentration $C_p$ is mapped to a sub-index $I_p$ via piecewise linear interpolation:
$$I_p = I_{\text{low}} + \frac{I_{\text{high}} - I_{\text{low}}}{C_{\text{high}} - C_{\text{low}}} \left(C_p - C_{\text{low}}\right)$$
The composite Air Quality Index is determined by the dominant pollutant:
$$\text{AQI} = \max_{p \in \mathcal{P}} \left(I_p\right)$$

### 2. Continuous Anchored Neural Trajectory
Let $\mathbf{X} \in \mathbb{R}^{24 \times 10}$ be the normalized 24-hour lag feature sequence ending at current observation $y_0$. The recurrent network outputs unscaled prediction $\mathbf{\hat{Y}} \in \mathbb{R}^{24 \times 4}$. The anchored forecast at horizon step $h \in [0, 23]$ is:
$$\mathbf{Y}_h = y_0 + (\mathbf{\hat{Y}}_h - \mathbf{\hat{Y}}_0)$$
This ensures zero step-1 discontinuity, preserving the station's actual micro-climate while dynamically adopting the recurrent diurnal trajectory.

### 3. Ordinary Kriging Geostatistics
For target coordinate $\mathbf{x}_0$, Ordinary Kriging estimates:
$$\hat{Z}(\mathbf{x}_0) = \sum_{i=1}^n \lambda_i Z(\mathbf{x}_i) \quad \text{subject to} \quad \sum_{i=1}^n \lambda_i = 1$$
Solving the Kriging system yields weights $\lambda_i$ and the estimation variance $\sigma_K^2(\mathbf{x}_0)$:
$$\sigma_K^2(\mathbf{x}_0) = \sum_{i=1}^n \lambda_i \gamma(\mathbf{x}_i - \mathbf{x}_0) + \mu$$
where $\gamma(h)$ is the fitted Gaussian semivariogram.

---

## 👥 Contributors & Academic Acknowledgments

Developed under the **AI-Powered Environmental Intelligence System for Air Quality Prediction and Smart Mobility Recommendations** project initiative for **Infosys Springboard**.
- **Supervising Faculty & Industry Mentors**
- **Pune Smart City Development Corporation Limited (PSCDCL)** for ambient urban IoT sensor dataset.
- **Central Pollution Control Board (CPCB)** for NAAQI technical standards and breakpoints.
