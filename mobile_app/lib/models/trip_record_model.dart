class TripRecord {
  final String id;
  final DateTime timestamp;
  final String origin;
  final String destination;
  final String mode; // Car, Public Transport, Motorcycle, Cycling, Walking
  final double distanceKm;
  final double durationMin;
  final double avgAqi;
  final String category;
  final double exposureUg; // Cumulative inhaled particulate mass in micrograms
  final double exposureScore; // 0 - 100
  final String healthProfile;
  final String recommendation;

  const TripRecord({
    required this.id,
    required this.timestamp,
    required this.origin,
    required this.destination,
    required this.mode,
    required this.distanceKm,
    required this.durationMin,
    required this.avgAqi,
    required this.category,
    required this.exposureUg,
    required this.exposureScore,
    required this.healthProfile,
    required this.recommendation,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'timestamp': timestamp.toIso8601String(),
      'origin': origin,
      'destination': destination,
      'mode': mode,
      'distance_km': distanceKm,
      'duration_min': durationMin,
      'avg_aqi': avgAqi,
      'category': category,
      'exposure_ug': exposureUg,
      'exposure_score': exposureScore,
      'health_profile': healthProfile,
      'recommendation': recommendation,
    };
  }

  factory TripRecord.fromJson(Map<String, dynamic> json) {
    return TripRecord(
      id: json['id']?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp'].toString()) ?? DateTime.now()
          : DateTime.now(),
      origin: json['origin'] ?? 'Pune Center',
      destination: json['destination'] ?? 'Destination',
      mode: json['mode'] ?? 'Car',
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 8.5,
      durationMin: (json['duration_min'] as num?)?.toDouble() ?? 22.0,
      avgAqi: (json['avg_aqi'] as num?)?.toDouble() ?? 78.0,
      category: json['category'] ?? 'Moderate',
      exposureUg: (json['exposure_ug'] as num?)?.toDouble() ?? 28.5,
      exposureScore: (json['exposure_score'] as num?)?.toDouble() ?? 36.0,
      healthProfile: json['health_profile'] ?? 'General User',
      recommendation: json['recommendation'] ?? 'Clean corridor saved 22% exposure.',
    );
  }

  String toCsvRow() {
    return '"${timestamp.toIso8601String()}","${origin.replaceAll('"', '""')}","${destination.replaceAll('"', '""')}","$mode",$distanceKm,$durationMin,$avgAqi,"$category",$exposureUg,$exposureScore,"$healthProfile"';
  }

  static String csvHeader() {
    return 'Timestamp,Origin,Destination,Mode,Distance_KM,Duration_Min,Avg_AQI,Category,Exposure_UG,Exposure_Score,Health_Profile';
  }
}
