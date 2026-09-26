class ApiConfig {
  // Default for Android Emulator is 10.0.2.2; for iOS/Web/Desktop is 127.0.0.1
  static const String defaultEmulatorBaseUrl = 'http://10.0.2.2:8000';
  static const String defaultLocalhostBaseUrl = 'http://127.0.0.1:8000';

  static String currentBaseUrl = defaultEmulatorBaseUrl;

  // Endpoint paths
  static const String healthPath = '/health';
  static const String kpiSummaryPath = '/api/kpi-summary';
  static const String stationsPath = '/api/stations';
  static const String stationComparisonPath = '/api/station-comparison';
  static const String forecastPath = '/api/predict/forecast';
  static const String interpolatePath = '/api/predict/interpolate';
  static const String routeExposurePath = '/api/route/exposure';
  static const String healthProfilesPath = '/api/health-profiles';
  static const String systemStatusPath = '/api/system/status';
  static const String runTestsPath = '/api/system/tests/run';

  static String stationHistoryPath(String stationName, {int lookback = 24}) {
    return '/api/stations/$stationName/history?lookback=$lookback';
  }

  static String buildUrl(String path) {
    final cleanBase = currentBaseUrl.endsWith('/')
        ? currentBaseUrl.substring(0, currentBaseUrl.length - 1)
        : currentBaseUrl;
    final cleanPath = path.startsWith('/') ? path : '/$path';
    return '$cleanBase$cleanPath';
  }
}
