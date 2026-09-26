class LatLngPoint {
  final double lat;
  final double lon;

  const LatLngPoint(this.lat, this.lon);

  factory LatLngPoint.fromJson(dynamic item) {
    if (item is List && item.length >= 2) {
      return LatLngPoint(
        (item[0] as num).toDouble(),
        (item[1] as num).toDouble(),
      );
    } else if (item is Map) {
      return LatLngPoint(
        (item['lat'] as num).toDouble(),
        (item['lon'] ?? item['lng'] as num).toDouble(),
      );
    }
    return const LatLngPoint(18.5204, 73.8567);
  }
}

class WaypointInfo {
  final String name;
  final double lat;
  final double lon;
  final double aqi;
  final String category;
  final double pm25;

  const WaypointInfo({
    required this.name,
    required this.lat,
    required this.lon,
    required this.aqi,
    required this.category,
    required this.pm25,
  });

  factory WaypointInfo.fromJson(Map<String, dynamic> json) {
    return WaypointInfo(
      name: json['name'] ?? 'Waypoint',
      lat: (json['lat'] as num?)?.toDouble() ?? 18.5204,
      lon: (json['lon'] ?? json['lng'] as num?)?.toDouble() ?? 73.8567,
      aqi: (json['aqi'] as num?)?.toDouble() ?? 70.0,
      category: json['category'] ?? 'Moderate',
      pm25: (json['pm25'] as num?)?.toDouble() ?? 32.0,
    );
  }
}

class RouteDetail {
  final String id;
  final String name;
  final String description;
  final double distanceKm;
  final double durationMin;
  final double avgAqi;
  final double exposureScore;
  final String colorHex;
  final bool isRecommended;
  final List<LatLngPoint> polyline;
  final List<WaypointInfo> waypoints;

  const RouteDetail({
    required this.id,
    required this.name,
    required this.description,
    required this.distanceKm,
    required this.durationMin,
    required this.avgAqi,
    required this.exposureScore,
    required this.colorHex,
    required this.isRecommended,
    required this.polyline,
    required this.waypoints,
  });

  factory RouteDetail.fromJson(String id, Map<String, dynamic> json, {bool recommended = false}) {
    final pts = (json['polyline'] as List<dynamic>?)
            ?.map((e) => LatLngPoint.fromJson(e))
            .toList() ??
        [];

    final wps = (json['waypoints'] as List<dynamic>?)
            ?.map((e) => WaypointInfo.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];

    return RouteDetail(
      id: id,
      name: json['name'] ?? 'Route',
      description: json['corridor_type'] ?? json['description'] ?? '',
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 10.0,
      durationMin: (json['duration_min'] as num?)?.toDouble() ?? 25.0,
      avgAqi: (json['avg_aqi'] as num?)?.toDouble() ?? 80.0,
      exposureScore: (json['exposure_score'] as num?)?.toDouble() ?? 45.0,
      colorHex: json['color'] ?? (recommended ? '#10B981' : '#3B82F6'),
      isRecommended: recommended || (json['is_recommended'] == true),
      polyline: pts,
      waypoints: wps,
    );
  }
}

class RouteExposureAnalysis {
  final String origin;
  final String destination;
  final String transportMode;
  final String healthProfile;
  final double inhalationSavingsPct;
  final String recommendedRouteKey;
  final String advisory;
  final List<String> hotspotsAvoided;
  final RouteDetail directRoute;
  final RouteDetail alternativeRoute;
  final RouteDetail cleanCorridorRoute;

  const RouteExposureAnalysis({
    required this.origin,
    required this.destination,
    required this.transportMode,
    required this.healthProfile,
    required this.inhalationSavingsPct,
    required this.recommendedRouteKey,
    required this.advisory,
    required this.hotspotsAvoided,
    required this.directRoute,
    required this.alternativeRoute,
    required this.cleanCorridorRoute,
  });

  factory RouteExposureAnalysis.fromJson(Map<String, dynamic> json) {
    final routesMap = json['routes'] as Map<String, dynamic>? ?? {};

    final r1 = RouteDetail.fromJson(
      'route_1_direct',
      routesMap['route_1_direct'] ?? {},
      recommended: false,
    );
    final r2 = RouteDetail.fromJson(
      'route_2_alternative',
      routesMap['route_2_alternative'] ?? {},
      recommended: false,
    );
    final r3 = RouteDetail.fromJson(
      'route_3_clean_corridor',
      routesMap['route_3_clean_corridor'] ?? {},
      recommended: true,
    );

    final avoidedList = (json['hotspots_avoided'] as List<dynamic>?)
            ?.map((e) => e.toString())
            .toList() ??
        [];

    return RouteExposureAnalysis(
      origin: json['origin'] ?? 'Origin',
      destination: json['destination'] ?? 'Destination',
      transportMode: json['transport_mode'] ?? 'Car',
      healthProfile: json['health_profile'] ?? 'General User',
      inhalationSavingsPct: (json['inhalation_savings_pct'] as num?)?.toDouble() ?? 24.5,
      recommendedRouteKey: json['recommended_route'] ?? 'route_3_clean_corridor',
      advisory: json['advisory'] ??
          'Selecting Route 3 (Clean-Air Corridor) optimizes inhalation by avoiding arterial traffic corridors.',
      hotspotsAvoided: avoidedList,
      directRoute: r1,
      alternativeRoute: r2,
      cleanCorridorRoute: r3,
    );
  }
}
