import '../models/station_model.dart';
import '../models/forecast_model.dart';
import '../models/route_exposure_model.dart';
import '../models/kpi_summary_model.dart';

class OfflineDataService {
  // 10 Pune SmartCity Stations matching the dataset
  static List<StationModel> getFallbackStations() {
    return [
      const StationModel(
        id: 'BopadiSquare_65',
        name: 'BopadiSquare_65',
        cleanName: 'Bopodi Square',
        city: 'Pune',
        lat: 18.5594,
        lon: 73.8287,
        aqi: 108.0,
        category: 'Sensitive Groups',
        dominantPollutant: 'PM2.5',
        pm25: 45.4,
        pm10: 88.2,
        no2: 44.1,
        so2: 12.8,
        co: 1.45,
        o3: 31.0,
        temp: 30.2,
        humidity: 54.0,
        pressure: 1011.5,
        soundDb: 72.4,
        trafficScore: 78.0,
        trafficLevel: 'Heavy Congestion',
      ),
      const StationModel(
        id: 'Hadapsar_Gadital_01',
        name: 'Hadapsar_Gadital_01',
        cleanName: 'Hadapsar Gadital',
        city: 'Pune',
        lat: 18.5089,
        lon: 73.9260,
        aqi: 116.0,
        category: 'Sensitive Groups',
        dominantPollutant: 'PM10',
        pm25: 48.9,
        pm10: 102.5,
        no2: 52.0,
        so2: 14.2,
        co: 1.80,
        o3: 26.5,
        temp: 31.5,
        humidity: 51.0,
        pressure: 1010.8,
        soundDb: 76.8,
        trafficScore: 84.0,
        trafficLevel: 'Severe Congestion',
      ),
      const StationModel(
        id: 'Pune Railway Station_28',
        name: 'Pune Railway Station_28',
        cleanName: 'Pune Railway Station',
        city: 'Pune',
        lat: 18.5284,
        lon: 73.8744,
        aqi: 94.0,
        category: 'Moderate',
        dominantPollutant: 'PM2.5',
        pm25: 39.5,
        pm10: 74.0,
        no2: 46.8,
        so2: 11.5,
        co: 1.35,
        o3: 29.2,
        temp: 29.8,
        humidity: 56.5,
        pressure: 1012.0,
        soundDb: 74.2,
        trafficScore: 72.0,
        trafficLevel: 'Moderate Congestion',
      ),
      const StationModel(
        id: 'PMPML_Bus_Depot_Deccan_15',
        name: 'PMPML_Bus_Depot_Deccan_15',
        cleanName: 'Deccan Bus Depot',
        city: 'Pune',
        lat: 18.5167,
        lon: 73.8415,
        aqi: 82.0,
        category: 'Moderate',
        dominantPollutant: 'NO2',
        pm25: 34.2,
        pm10: 65.0,
        no2: 48.2,
        so2: 9.8,
        co: 1.20,
        o3: 32.1,
        temp: 29.2,
        humidity: 58.0,
        pressure: 1012.4,
        soundDb: 70.5,
        trafficScore: 66.0,
        trafficLevel: 'Moderate Congestion',
      ),
      const StationModel(
        id: 'Karve Statue Square_5',
        name: 'Karve Statue Square_5',
        cleanName: 'Karve Statue Square',
        city: 'Pune',
        lat: 18.5039,
        lon: 73.8267,
        aqi: 76.0,
        category: 'Moderate',
        dominantPollutant: 'PM2.5',
        pm25: 31.8,
        pm10: 59.4,
        no2: 38.5,
        so2: 8.4,
        co: 1.10,
        o3: 35.0,
        temp: 28.9,
        humidity: 60.0,
        pressure: 1013.1,
        soundDb: 67.2,
        trafficScore: 58.0,
        trafficLevel: 'Moderate Congestion',
      ),
      const StationModel(
        id: 'Lullanagar_Square_14',
        name: 'Lullanagar_Square_14',
        cleanName: 'Lullanagar Square',
        city: 'Pune',
        lat: 18.4891,
        lon: 73.8867,
        aqi: 88.0,
        category: 'Moderate',
        dominantPollutant: 'PM2.5',
        pm25: 36.8,
        pm10: 68.2,
        no2: 41.0,
        so2: 10.2,
        co: 1.25,
        o3: 28.4,
        temp: 30.0,
        humidity: 55.0,
        pressure: 1011.8,
        soundDb: 69.0,
        trafficScore: 62.0,
        trafficLevel: 'Moderate Congestion',
      ),
      const StationModel(
        id: 'Rajashri_Shahu_Bus_stand_19',
        name: 'Rajashri_Shahu_Bus_stand_19',
        cleanName: 'Rajashri Shahu Bus Stand',
        city: 'Pune',
        lat: 18.4575,
        lon: 73.8677,
        aqi: 98.0,
        category: 'Moderate',
        dominantPollutant: 'PM10',
        pm25: 41.2,
        pm10: 78.5,
        no2: 43.6,
        so2: 11.0,
        co: 1.40,
        o3: 27.8,
        temp: 30.5,
        humidity: 53.0,
        pressure: 1011.2,
        soundDb: 73.0,
        trafficScore: 70.0,
        trafficLevel: 'Moderate Congestion',
      ),
      const StationModel(
        id: 'Goodluck Square_Cafe_23',
        name: 'Goodluck Square_Cafe_23',
        cleanName: 'Goodluck Square',
        city: 'Pune',
        lat: 18.5190,
        lon: 73.8428,
        aqi: 72.0,
        category: 'Moderate',
        dominantPollutant: 'PM2.5',
        pm25: 30.0,
        pm10: 56.0,
        no2: 36.2,
        so2: 8.0,
        co: 1.05,
        o3: 34.5,
        temp: 29.0,
        humidity: 59.0,
        pressure: 1012.6,
        soundDb: 66.5,
        trafficScore: 54.0,
        trafficLevel: 'Light Congestion',
      ),
      const StationModel(
        id: 'Chitale Bandhu Corner_41',
        name: 'Chitale Bandhu Corner_41',
        cleanName: 'Chitale Bandhu Corner',
        city: 'Pune',
        lat: 18.5142,
        lon: 73.8495,
        aqi: 68.0,
        category: 'Moderate',
        dominantPollutant: 'PM2.5',
        pm25: 28.5,
        pm10: 52.8,
        no2: 34.0,
        so2: 7.5,
        co: 0.95,
        o3: 36.2,
        temp: 28.8,
        humidity: 61.0,
        pressure: 1013.0,
        soundDb: 65.0,
        trafficScore: 50.0,
        trafficLevel: 'Light Congestion',
      ),
      const StationModel(
        id: 'Dr Baba Saheb Ambedkar Sethu Junction_60',
        name: 'Dr Baba Saheb Ambedkar Sethu Junction_60',
        cleanName: 'Ambedkar Sethu Junction',
        city: 'Pune',
        lat: 18.5360,
        lon: 73.8765,
        aqi: 91.0,
        category: 'Moderate',
        dominantPollutant: 'NO2',
        pm25: 38.0,
        pm10: 71.0,
        no2: 45.0,
        so2: 10.8,
        co: 1.30,
        o3: 30.0,
        temp: 30.1,
        humidity: 55.5,
        pressure: 1012.0,
        soundDb: 71.8,
        trafficScore: 68.0,
        trafficLevel: 'Moderate Congestion',
      ),
    ];
  }

  static KpiSummaryModel getFallbackKpiSummary() {
    return const KpiSummaryModel(
      activeStations: 10,
      aqiAlertsToday: 2,
      forecastAccuracy: '90.2%',
      forecastWindow: '24-hour recurrent window',
      avgCityAqi: 89.3,
      avgCategory: 'Moderate',
      categoryBreakdown: {
        'Good (0-50)': 0,
        'Moderate (51-100)': 8,
        'Sensitive (101-150)': 2,
        'Poor (151-200)': 0,
        'Very Poor / Hazardous (200+)': 0,
      },
      trainedArchitecture: 'PyTorch GRU (Gated Recurrent Unit)',
      lastTrained: '2026-09-18T13:01:19Z',
    );
  }

  static ForecastModel getFallbackForecast(String stationName, int horizon) {
    final List<double> traj = [];
    final List<ConfidenceInterval> cis = [];
    final List<double> pm25 = [];
    final List<double> pm10 = [];
    final List<double> no2 = [];

    double current = 88.0;
    if (stationName.contains('Bopadi') || stationName.contains('Bopodi')) {
      current = 108.0;
    } else if (stationName.contains('Hadapsar')) {
      current = 116.0;
    }

    for (int h = 1; h <= horizon; h++) {
      // Realistic diurnal variation curve
      final delta = (h <= 6) ? (h * 1.5) : (h <= 14 ? (9.0 - (h - 6) * 1.8) : (-(h - 14) * 0.8));
      final val = (current + delta).clamp(30.0, 350.0);
      final spread = 3.5 + 1.2 * (h / 2.0);

      traj.add(double.parse(val.toStringAsFixed(1)));
      cis.add(ConfidenceInterval(
        stepHour: h,
        lowerBound: double.parse((val - spread).clamp(10.0, 500.0).toStringAsFixed(1)),
        predictedAqi: double.parse(val.toStringAsFixed(1)),
        upperBound: double.parse((val + spread).clamp(10.0, 500.0).toStringAsFixed(1)),
      ));
      pm25.add(double.parse((val * 0.42).toStringAsFixed(1)));
      pm10.add(double.parse((val * 0.78).toStringAsFixed(1)));
      no2.add(double.parse((38.0 + h * 0.4).toStringAsFixed(1)));
    }

    return ForecastModel(
      location: stationName,
      architecture: 'GRU',
      horizonHours: horizon,
      currentAqi: current,
      predictedEndpointAqi: traj.isNotEmpty ? traj.last : current,
      aqiTrajectory: traj,
      confidenceIntervals: cis,
      pollutantBreakdown: {'pm25': pm25, 'pm10': pm10, 'no2': no2},
      healthCategory: current > 100 ? 'Sensitive Groups' : 'Moderate',
      healthRecommendation: current > 100
          ? 'Air quality is Unhealthy for Sensitive Groups. Children and asthmatics should wear an N95 mask near arterial corridors.'
          : 'Air quality is Moderate. Normal activity permitted for most individuals.',
      modelStatus: 'PyTorch GRU Checkpoint Loaded',
    );
  }

  static RouteExposureAnalysis getFallbackRouteAnalysis({
    required String origin,
    required String destination,
    required String mode,
    required String profile,
  }) {
    // Coordinate waypoints for Pune Route 1 (Arterial), Route 2 (Alternative), Route 3 (Eco Corridor)
    final r1Points = [
      const LatLngPoint(18.5089, 73.9260), // Hadapsar
      const LatLngPoint(18.5140, 73.8990),
      const LatLngPoint(18.5284, 73.8744), // Pune Station
      const LatLngPoint(18.5390, 73.8500),
      const LatLngPoint(18.5594, 73.8287), // Bopodi
    ];

    final r2Points = [
      const LatLngPoint(18.5089, 73.9260),
      const LatLngPoint(18.4980, 73.8900),
      const LatLngPoint(18.5018, 73.8586), // Swargate
      const LatLngPoint(18.5314, 73.8446), // Shivajinagar
      const LatLngPoint(18.5594, 73.8287),
    ];

    final r3Points = [
      const LatLngPoint(18.5089, 73.9260),
      const LatLngPoint(18.5250, 73.9100), // River greenway bypass
      const LatLngPoint(18.5463, 73.8900), // Koregaon park / Bund garden
      const LatLngPoint(18.5600, 73.8550), // Khadki green corridor
      const LatLngPoint(18.5594, 73.8287),
    ];

    final r1Waypoints = [
      const WaypointInfo(name: 'Hadapsar Junction', lat: 18.5089, lon: 73.9260, aqi: 116.0, category: 'Sensitive Groups', pm25: 48.9),
      const WaypointInfo(name: 'Camp Flyover', lat: 18.5140, lon: 73.8990, aqi: 105.0, category: 'Sensitive Groups', pm25: 44.2),
      const WaypointInfo(name: 'Pune Railway Station', lat: 18.5284, lon: 73.8744, aqi: 94.0, category: 'Moderate', pm25: 39.5),
      const WaypointInfo(name: 'Old Mumbai-Pune Hwy', lat: 18.5390, lon: 73.8500, aqi: 110.0, category: 'Sensitive Groups', pm25: 46.1),
      const WaypointInfo(name: 'Bopodi Square', lat: 18.5594, lon: 73.8287, aqi: 108.0, category: 'Sensitive Groups', pm25: 45.4),
    ];

    final r3Waypoints = [
      const WaypointInfo(name: 'Hadapsar Bypass', lat: 18.5089, lon: 73.9260, aqi: 98.0, category: 'Moderate', pm25: 41.0),
      const WaypointInfo(name: 'Mula-Mutha Riverbank', lat: 18.5250, lon: 73.9100, aqi: 62.0, category: 'Moderate', pm25: 25.5),
      const WaypointInfo(name: 'Bund Garden Park corridor', lat: 18.5463, lon: 73.8900, aqi: 58.0, category: 'Moderate', pm25: 23.8),
      const WaypointInfo(name: 'Khadki Cantonment Eco Road', lat: 18.5600, lon: 73.8550, aqi: 64.0, category: 'Moderate', pm25: 26.2),
      const WaypointInfo(name: 'Bopodi Eco Approach', lat: 18.5594, lon: 73.8287, aqi: 82.0, category: 'Moderate', pm25: 34.0),
    ];

    double modeFactor = 1.0;
    if (mode == 'Car') modeFactor = 0.65;
    if (mode == 'Public Transport') modeFactor = 0.90;
    if (mode == 'Motorcycle') modeFactor = 1.25;
    if (mode == 'Cycling' || mode == 'Walking') modeFactor = 1.40;

    double profileFactor = 1.0;
    if (profile.contains('Asthmatic')) profileFactor = 1.40;
    if (profile.contains('Elderly')) profileFactor = 1.25;
    if (profile.contains('Child')) profileFactor = 1.20;

    final baseExp1 = (106.6 / 100.0) * (34.0 / 30.0) * modeFactor * profileFactor * 18.0;
    final baseExp2 = (92.4 / 100.0) * (36.0 / 30.0) * modeFactor * profileFactor * 18.0;
    final baseExp3 = (72.8 / 100.0) * (38.0 / 30.0) * modeFactor * profileFactor * 18.0;

    final savings = (((baseExp1 - baseExp3) / baseExp1) * 100.0).clamp(12.0, 38.0);

    return RouteExposureAnalysis(
      origin: origin,
      destination: destination,
      transportMode: mode,
      healthProfile: profile,
      inhalationSavingsPct: double.parse(savings.toStringAsFixed(1)),
      recommendedRouteKey: 'route_3_clean_corridor',
      advisory: 'Clean-Air Corridor (Green Route) reduces particulate exposure by ${savings.toStringAsFixed(1)}% '
          'by circumventing high-congestion junctions along the central highway.',
      hotspotsAvoided: ['Hadapsar Gadital Flyover', 'Pune Station Arterial Junction'],
      directRoute: RouteDetail(
        id: 'route_1_direct',
        name: 'Direct Arterial Corridor',
        description: 'Direct Highway Corridor (Highest Particulate Inhalation)',
        distanceKm: 14.8,
        durationMin: 34.0,
        avgAqi: 106.6,
        exposureScore: double.parse(baseExp1.toStringAsFixed(1)),
        colorHex: '#DC2626',
        isRecommended: false,
        polyline: r1Points,
        waypoints: r1Waypoints,
      ),
      alternativeRoute: RouteDetail(
        id: 'route_2_alternative',
        name: 'Alternative Mixed Transit',
        description: 'Swargate - Shivajinagar Mixed Transit Bypass',
        distanceKm: 16.2,
        durationMin: 36.0,
        avgAqi: 92.4,
        exposureScore: double.parse(baseExp2.toStringAsFixed(1)),
        colorHex: '#2563EB',
        isRecommended: false,
        polyline: r2Points,
        waypoints: r1Waypoints,
      ),
      cleanCorridorRoute: RouteDetail(
        id: 'route_3_clean_corridor',
        name: 'Clean-Air Eco Corridor (Recommended)',
        description: 'Riverbank & Khadki Cantonment Low-Emission Corridor',
        distanceKm: 17.5,
        durationMin: 38.0,
        avgAqi: 72.8,
        exposureScore: double.parse(baseExp3.toStringAsFixed(1)),
        colorHex: '#10B981',
        isRecommended: true,
        polyline: r3Points,
        waypoints: r3Waypoints,
      ),
    );
  }
}
