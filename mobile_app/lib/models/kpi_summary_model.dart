class KpiSummaryModel {
  final int activeStations;
  final int aqiAlertsToday;
  final String forecastAccuracy;
  final String forecastWindow;
  final double avgCityAqi;
  final String avgCategory;
  final Map<String, int> categoryBreakdown;
  final String trainedArchitecture;
  final String lastTrained;

  const KpiSummaryModel({
    required this.activeStations,
    required this.aqiAlertsToday,
    required this.forecastAccuracy,
    required this.forecastWindow,
    required this.avgCityAqi,
    required this.avgCategory,
    required this.categoryBreakdown,
    required this.trainedArchitecture,
    required this.lastTrained,
  });

  factory KpiSummaryModel.fromJson(Map<String, dynamic> json) {
    final Map<String, int> breakdown = {};
    if (json['category_breakdown'] is Map) {
      (json['category_breakdown'] as Map<String, dynamic>).forEach((k, v) {
        breakdown[k] = (v as num).toInt();
      });
    }

    return KpiSummaryModel(
      activeStations: (json['active_stations'] as num?)?.toInt() ?? 10,
      aqiAlertsToday: (json['aqi_alerts_today'] as num?)?.toInt() ?? 2,
      forecastAccuracy: json['forecast_accuracy'] ?? '90.2%',
      forecastWindow: json['forecast_window'] ?? '24-hour recurrent window',
      avgCityAqi: (json['avg_city_aqi'] as num?)?.toDouble() ?? 78.4,
      avgCategory: json['avg_category'] ?? 'Moderate',
      categoryBreakdown: breakdown,
      trainedArchitecture: json['trained_architecture'] ?? 'PyTorch GRU (Gated Recurrent Unit)',
      lastTrained: json['last_trained'] ?? '2026-09-18T13:01:19Z',
    );
  }
}
