class StationModel {
  final String id;
  final String name;
  final String cleanName;
  final String city;
  final double lat;
  final double lon;
  final double aqi;
  final String category;
  final String dominantPollutant;
  final double pm25;
  final double pm10;
  final double no2;
  final double so2;
  final double co;
  final double o3;
  final double temp;
  final double humidity;
  final double pressure;
  final double soundDb;
  final double trafficScore;
  final String trafficLevel;

  const StationModel({
    required this.id,
    required this.name,
    required this.cleanName,
    required this.city,
    required this.lat,
    required this.lon,
    required this.aqi,
    required this.category,
    required this.dominantPollutant,
    required this.pm25,
    required this.pm10,
    required this.no2,
    required this.so2,
    required this.co,
    required this.o3,
    required this.temp,
    required this.humidity,
    required this.pressure,
    required this.soundDb,
    required this.trafficScore,
    required this.trafficLevel,
  });

  factory StationModel.fromJson(String id, Map<String, dynamic> json) {
    // Generate clean human-readable name from station ID
    String clean = json['clean_name'] ?? id;
    if (clean == id) {
      clean = id
          .replaceAll(RegExp(r'_\d+$'), '')
          .replaceAllMapped(RegExp(r'([a-z])([A-Z])'), (m) => '${m[1]} ${m[2]}')
          .replaceAll('_', ' ')
          .replaceAll('BopadiSquare', 'Bopodi Square')
          .trim();
    }

    final double aqiVal = (json['aqi'] is num) ? (json['aqi'] as num).toDouble() : 75.0;

    return StationModel(
      id: id,
      name: json['name'] ?? id,
      cleanName: clean,
      city: json['city'] ?? 'Pune',
      lat: (json['lat'] is num) ? (json['lat'] as num).toDouble() : 18.5204,
      lon: (json['lon'] is num) ? (json['lon'] as num).toDouble() : 73.8567,
      aqi: aqiVal,
      category: json['category'] ?? 'Moderate',
      dominantPollutant: json['dominant_pollutant'] ?? 'PM2.5',
      pm25: (json['pm25'] is num) ? (json['pm25'] as num).toDouble() : (aqiVal * 0.42),
      pm10: (json['pm10'] is num) ? (json['pm10'] as num).toDouble() : (aqiVal * 0.78),
      no2: (json['no2'] is num) ? (json['no2'] as num).toDouble() : 38.0,
      so2: (json['so2'] is num) ? (json['so2'] as num).toDouble() : 12.0,
      co: (json['co'] is num) ? (json['co'] as num).toDouble() : 1.2,
      o3: (json['o3'] is num) ? (json['o3'] as num).toDouble() : 28.0,
      temp: (json['temp'] is num) ? (json['temp'] as num).toDouble() : 29.5,
      humidity: (json['humidity'] is num) ? (json['humidity'] as num).toDouble() : 58.0,
      pressure: (json['pressure'] is num) ? (json['pressure'] as num).toDouble() : 1012.0,
      soundDb: (json['sound_db'] is num) ? (json['sound_db'] as num).toDouble() : 68.0,
      trafficScore: (json['traffic_congestion_score'] is num)
          ? (json['traffic_congestion_score'] as num).toDouble()
          : 55.0,
      trafficLevel: json['traffic_congestion_level'] ?? 'Moderate',
    );
  }
}
