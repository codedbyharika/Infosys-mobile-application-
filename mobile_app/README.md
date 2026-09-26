# EcoAir Intelligence (AirSense Mobile) — Flutter Application

[![Flutter](https://img.shields.io/badge/Flutter-3.0%2B-02569B.svg?style=flat&logo=flutter)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![CPCB Standard](https://img.shields.io/badge/Standard-CPCB%20NAAQI-16A34A.svg?style=flat)](https://cpcb.nic.in)
[![Cross Platform](https://img.shields.io/badge/Platform-Android%20%7C%20iOS%20%7C%20Web-blue.svg?style=flat)]()

**EcoAir Intelligence Mobile** is the cross-platform mobile frontend for the EcoAir Intelligence (AirSense) environmental platform and predictive smart-mobility system. Built with **Flutter**, it connects directly to the production **FastAPI** backend microservice to deliver real-time sensor telemetry, deep recurrent AQI forecasts, interactive GIS pollution maps, travel route particulate exposure optimization, personal exposure history tracking, and notification preference management.

---

## 📱 Mobile Architecture & Feature Matrix

The Flutter mobile application completely transforms the web application into a native mobile experience organized across 5 core views:

### 1. 📊 Executive Dashboard (`dashboard_screen.dart`)
- **City Summary Hero Card:** Displays Pune SmartCity average AQI with an animated radial CPCB gauge, dominant pollutant, active alerts count, and neural model accuracy (`90.2% Accuracy`).
- **Station Selector:** Horizontal chip carousel to instantly switch between all 10 monitored Pune SmartCity nodes.
- **Detailed Station Telemetry:** Real-time sensor metrics for the selected station:
  - Sub-pollutants: $PM_{2.5}, PM_{10}, NO_2, SO_2, CO, O_3$ with safe limit comparison bars.
  - Meteorological conditions: Temperature ($^\circ\text{C}$), Relative Humidity ($\%$), Inversion Pressure ($\text{hPa}$).
  - Acoustic & Traffic Index: Junction acoustic noise level ($\text{dB}$) and vehicular combustion congestion score ($15\text{–}95$).
- **24-Hour Telemetry Trend Chart:** High-performance line chart displaying past 24-hour sensor trends using `fl_chart`.
- **Station Comparison & Ranking Matrix:** Sortable ranking across stations by AQI, $PM_{2.5}$, or $PM_{10}$.

### 2. 🗺️ Interactive GIS Pollution Map (`map_screen.dart`)
- **Geographic Canvas of Pune:** Geolocated bounding box ($18.440^\circ\text{N}\text{–}18.640^\circ\text{N}$, $73.720^\circ\text{E}\text{–}73.950^\circ\text{E}$) with riverway corridor and terrain features.
- **Color-Coded Station Markers:** Stations plotted with official CPCB 6-tier status colors (Good, Moderate, Sensitive, Poor, Very Poor, Hazardous).
- **High-Pollution Hotspot Glows:** Pulsing halo rings for nodes with elevated particulate levels ($AQI > 100$).
- **Tri-Route Polyline Overlays:** Visual rendering of Route 1 (Red Arterial), Route 2 (Blue Alternative), and Route 3 (Green Eco Corridor) with Start (`S`) and Destination (`D`) badges.
- **Interactive Taps & Bottom Sheet:** Tap any station to open `StationBottomSheet` with full sensor telemetry, weather, and instant action buttons ("24h Forecast", "Plan Route").
- **On-Map Spatial Ordinary Kriging:** Tap anywhere on the map canvas to trigger geostatistical interpolation for that exact coordinate!

### 3. 🛣️ Travel Route Particulate Exposure Estimator (`route_screen.dart`)
- **Origin & Destination Selector:** Select journey endpoints with instant swap (`⇄`) button.
- **Respiratory Ventilation Modifiers:**
  - Car: `0.65x`
  - Public Transport: `0.90x`
  - Motorcycle: `1.25x`
  - Cycling: `1.40x`
  - Walking: `1.40x`
- **Vulnerability Profiling:** Adjusts exposure calculation for General Users (`1.0x`), Asthmatic/Respiratory (`1.40x`), Elderly (`1.25x`), and Children (`1.20x`).
- **Clean Corridor Inhalation Savings Banner:** Highlights particulate reduction percentage (e.g. `24.3% Inhalation Reduction`).
- **Tri-Route Comparison Cards:**
  - **Route 3 (Clean-Air Eco Corridor):** Recommended low-emission path (Green).
  - **Route 2 (Alternative Transit Route):** Balanced secondary corridor (Blue).
  - **Route 1 (Direct Arterial Corridor):** Highest particulate exposure corridor (Red).
  - Each card details: Distance ($\text{km}$), Travel time ($\text{min}$), Average $AQI$, and Cumulative Particulate Exposure Score.
- **Sampled Waypoints Breakdown:** Localized $AQI$ and $PM_{2.5}$ at each waypoint along the route.
- **"Save Journey to My Exposure History" Action:** One-tap persistence to local journal.

### 4. 📈 Deep Recurrent AQI Forecasting (`forecast_screen.dart`)
- **PyTorch GRU & LSTM Architectures:** Multi-step ahead forecasting ($1\text{–}24\text{ hours}$).
- **95% Expanding Confidence Interval Cone:** Visual dashed confidence bands showing variance propagation.
- **Multi-Pollutant Trajectories:** Multi-line projections for $PM_{2.5}$, $PM_{10}$, and $NO_2$.
- **Spatial Kriging & IDW GIS Tool:** Coordinate input with Pune landmark presets (Hinjawadi, Swargate, Viman Nagar, Kothrud) estimating $AQI$ and spatial uncertainty score ($\pm \text{AQI}$).

### 5. 🛡️ Personal Exposure History (`history_screen.dart`)
- **Aggregated Lifetime Metrics:** Total Journeys count, Lifetime Inhaled Particulate Mass ($\mu\text{g}$), Average Journey $AQI$, and Cleanest Trip $AQI$.
- **Mode Filter Chips:** Filter journeys by transit mode (All, Car, Public Transit, Motorcycle, Cycling, Walking).
- **Persistent Storage:** Stored locally via `SharedPreferences`.
- **CSV Data Export:** Compiles complete exposure history into standard CSV format and copies to clipboard for sharing/export.
- **Manual Journey Logging:** Quick custom trip entry dialog.

### 6. ⚙️ Notification Preferences & Settings (`settings_screen.dart`)
- **Interactive AQI Hazard Alert Threshold Slider:** Configurable from $50$ to $250\text{ AQI}$ with dynamic CPCB color feedback.
- **Alert Toggles:** Push Notifications, Route Hazard Warnings, Daily Morning Digest ($7:30\text{ AM}$).
- **Breach Alert Simulation:** "Simulate AQI Hazard Breach Alert" triggers an emergency modal dialog (`BreachAlertDialog`) with recommended protective actions (e.g., N95 mask mandate, corridor rerouting).
- **FastAPI Endpoint Configuration:** In-app switch between Android Emulator (`http://10.0.2.2:8000`), Localhost (`http://127.0.0.1:8000`), or custom local network Wi-Fi IP with live ping latency check.
- **Module 4 Automated QA Test Runner:** Executes all 24 QA integration tests against `/api/system/tests/run` and displays test verdicts.

---

## 🎨 Official Indian CPCB 6-Tier Standard

The mobile application strictly implements the official Central Pollution Control Board (CPCB) National Air Quality Index color palette:

| Tier | AQI Range | Color | Hex Code | Category Label |
| :--- | :---: | :---: | :---: | :--- |
| **1** | $0 - 50$ | 🟢 Green | `#16A34A` | Good |
| **2** | $51 - 100$ | 🟡 Yellow / Mustard | `#CA8A04` | Satisfactory / Moderate |
| **3** | $101 - 150$ | 🟠 Orange | `#EA580C` | Moderately Polluted / Sensitive |
| **4** | $151 - 200$ | 🔴 Red | `#DC2626` | Poor / Unhealthy |
| **5** | $201 - 300$ | 🟣 Purple | `#7C3AED` | Very Poor |
| **6** | $301+$ | 🟤 Maroon / Dark Red | `#991B1B` | Severe / Hazardous |

---

## 🚀 How to Run the Application

### Step 1: Start the FastAPI Backend Microservice
Ensure your Python virtual environment is active and launch the server:

```powershell
cd c:\Users\Harika\OneDrive\Desktop\AQI_INFOSYS(app)\aqi-infosys
.\.venv\Scripts\python.exe run.py
```

The server binds to `0.0.0.0:8000` listening on:
- Local Web & Swagger: `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/docs`
- Android Emulator Endpoint: `http://10.0.2.2:8000/`
- Monitored Stations Telemetry: `http://127.0.0.1:8000/api/stations`

---

### Step 2: Run the Flutter Mobile App

Open the `mobile_app` folder in your terminal or IDE (Android Studio / VS Code):

```powershell
cd c:\Users\Harika\OneDrive\Desktop\AQI_INFOSYS(app)\aqi-infosys\mobile_app
flutter pub get
```

#### Run on Android Emulator:
```powershell
flutter run -d emulator
```
*(The mobile app defaults to `http://10.0.2.2:8000`, connecting immediately to your running FastAPI service)*

#### Run on Chrome / Web:
```powershell
flutter run -d chrome
```
*(In Settings, select `127.0.0.1:8000`)*

#### Run on Windows Desktop:
```powershell
flutter run -d windows
```

#### Run on Physical Mobile Device (Wi-Fi):
1. Connect your phone and PC to the same Wi-Fi network.
2. Find your PC's IP address (e.g., `ipconfig` -> `192.168.1.105`).
3. In the mobile app's **Alerts & Settings** tab, set API Base URL to `http://192.168.1.105:8000` and tap **Save & Ping**.

---

## 📦 Offline Resilience & Fallback Mode

If the FastAPI backend is temporarily offline or unreachable:
- The mobile app displays an amber **"Offline / Cached Mode — Local Pune SmartCity Telemetry"** indicator.
- All 10 Pune stations with real coordinates, CPCB sub-indices, historical trends, route simulations, and spatial interpolation continue operating seamlessly with zero crashes.
- Once the backend is restarted, tapping refresh or testing the connection automatically reconnects and switches to **"FastAPI Connected"** live mode!
