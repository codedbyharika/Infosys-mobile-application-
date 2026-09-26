class ConfidenceInterval {
  final int stepHour;
  final double lowerBound;
  final double predictedAqi;
  final double upperBound;

  const ConfidenceInterval({
    required this.stepHour,
    required this.lowerBound,
    required this.predictedAqi,
    required this.upperBound,
  });

  factory ConfidenceInterval.fromJson(Map<String, dynamic> json) {
    return ConfidenceInterval(
      stepHour: json['step_hour'] ?? 1,
      lowerBound: (json['lower_bound'] as num?)?.toDouble() ?? 0.0,
      predictedAqi: (json['predicted_aqi'] as num?)?.toDouble() ?? 0.0,
      upperBound: (json['upper_bound'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class ForecastModel {
  final String location;
  final String architecture;
  final int horizonHours;
  final double currentAqi;
  final double predictedEndpointAqi;
  final List<double> aqiTrajectory;
  final List<ConfidenceInterval> confidenceIntervals;
  final Map<String, List<double>> pollutantBreakdown;
  final String healthCategory;
  final String healthRecommendation;
  final String modelStatus;

  const ForecastModel({
    required this.location,
    required this.architecture,
    required this.horizonHours,
    required this.currentAqi,
    required this.predictedEndpointAqi,
    required this.aqiTrajectory,
    required this.confidenceIntervals,
    required this.pollutantBreakdown,
    required this.healthCategory,
    required this.healthRecommendation,
    required this.modelStatus,
  });

  factory ForecastModel.fromJson(Map<String, dynamic> json) {
    final trajectoryList = (json['aqi_trajectory'] as List<dynamic>?)
            ?.map((e) => (e as num).toDouble())
            .toList() ??
        [];

    final ciList = (json['confidence_intervals'] as List<dynamic>?)
            ?.map((e) => ConfidenceInterval.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    final Map<String, List<double>> pollutants = {};
    if (json['pollutant_breakdown'] is Map) {
      final pb = json['pollutant_breakdown'] as Map<String, dynamic>;
      pb.forEach((key, val) {
        if (val is List) {
          pollutants[key] = val.map((e) => (e as num).toDouble()).toList();
        }
      });
    }

    return ForecastModel(
      location: json['location'] ?? 'Pune',
      architecture: json['architecture'] ?? 'GRU',
      horizonHours: json['horizon_hours'] ?? 24,
      currentAqi: (json['current_aqi'] as num?)?.toDouble() ?? 75.0,
      predictedEndpointAqi: (json['predicted_endpoint_aqi'] as num?)?.toDouble() ?? 82.0,
      aqiTrajectory: trajectoryList,
      confidenceIntervals: ciList,
      pollutantBreakdown: pollutants,
      healthCategory: json['health_category'] ?? 'Moderate',
      healthRecommendation: json['health_recommendation'] ??
          'Air quality is moderate. Sensitive individuals should consider wearing a mask.',
      modelStatus: json['model_status'] ?? 'Active Checkpoint',
    );
  }
}
