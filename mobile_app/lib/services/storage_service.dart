import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/trip_record_model.dart';

class NotificationPrefs {
  final int aqiThreshold;
  final String healthProfile;
  final bool pushEnabled;
  final bool alertRouteHazards;
  final bool alertDailyDigest;
  final bool alertGeofencing;

  const NotificationPrefs({
    this.aqiThreshold = 120,
    this.healthProfile = 'General User',
    this.pushEnabled = true,
    this.alertRouteHazards = true,
    this.alertDailyDigest = true,
    this.alertGeofencing = true,
  });

  Map<String, dynamic> toJson() => {
        'aqiThreshold': aqiThreshold,
        'healthProfile': healthProfile,
        'pushEnabled': pushEnabled,
        'alertRouteHazards': alertRouteHazards,
        'alertDailyDigest': alertDailyDigest,
        'alertGeofencing': alertGeofencing,
      };

  factory NotificationPrefs.fromJson(Map<String, dynamic> json) =>
      NotificationPrefs(
        aqiThreshold: json['aqiThreshold'] ?? 120,
        healthProfile: json['healthProfile'] ?? 'General User',
        pushEnabled: json['pushEnabled'] ?? true,
        alertRouteHazards: json['alertRouteHazards'] ?? true,
        alertDailyDigest: json['alertDailyDigest'] ?? true,
        alertGeofencing: json['alertGeofencing'] ?? true,
      );
}

class StorageService {
  static const String _keyTrips = 'ecoair_trips_history';
  static const String _keyPrefs = 'ecoair_notification_prefs';
  static const String _keyBaseUrl = 'ecoair_api_base_url';
  static const String _keySelectedStation = 'ecoair_selected_station';

  static Future<List<TripRecord>> loadTrips() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final String? jsonStr = prefs.getString(_keyTrips);
      if (jsonStr != null && jsonStr.isNotEmpty) {
        final List<dynamic> list = jsonDecode(jsonStr);
        return list.map((e) => TripRecord.fromJson(e as Map<String, dynamic>)).toList();
      }
    } catch (e) {
      print('[StorageService] Error loading trips: $e');
    }

    // Default sample trip if fresh install
    final defaultTrips = [
      TripRecord(
        id: '1711200000001',
        timestamp: DateTime.now().subtract(const Duration(hours: 4)),
        origin: 'Kothrud Depot, Pune',
        destination: 'Hinjawadi Phase 1, Pune',
        mode: 'Car',
        distanceKm: 16.4,
        durationMin: 32.0,
        avgAqi: 74.0,
        category: 'Moderate',
        exposureUg: 36.5,
        exposureScore: 42.0,
        healthProfile: 'General User',
        recommendation: 'Use Clean-Air Route C for 18% lower particulate intake.',
      ),
      TripRecord(
        id: '1711200000002',
        timestamp: DateTime.now().subtract(const Duration(days: 1, hours: 2)),
        origin: 'Hadapsar Gadital, Pune',
        destination: 'Bopodi Square, Pune',
        mode: 'Public Transport',
        distanceKm: 14.8,
        durationMin: 45.0,
        avgAqi: 82.0,
        category: 'Moderate',
        exposureUg: 52.0,
        exposureScore: 56.0,
        healthProfile: 'General User',
        recommendation: 'Corridor saved 24% PM inhalation compared to arterial road.',
      ),
    ];
    await saveTrips(defaultTrips);
    return defaultTrips;
  }

  static Future<void> saveTrips(List<TripRecord> trips) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonStr = jsonEncode(trips.map((t) => t.toJson()).toList());
      await prefs.setString(_keyTrips, jsonStr);
    } catch (e) {
      print('[StorageService] Error saving trips: $e');
    }
  }

  static Future<void> addTrip(TripRecord trip) async {
    final list = await loadTrips();
    list.insert(0, trip); // Most recent first
    await saveTrips(list);
  }

  static Future<void> deleteTrip(String id) async {
    final list = await loadTrips();
    list.removeWhere((t) => t.id == id);
    await saveTrips(list);
  }

  static Future<void> clearAllTrips() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyTrips);
  }

  static Future<NotificationPrefs> loadNotificationPrefs() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final String? jsonStr = prefs.getString(_keyPrefs);
      if (jsonStr != null && jsonStr.isNotEmpty) {
        return NotificationPrefs.fromJson(jsonDecode(jsonStr));
      }
    } catch (e) {
      print('[StorageService] Error loading notification prefs: $e');
    }
    return const NotificationPrefs();
  }

  static Future<void> saveNotificationPrefs(NotificationPrefs prefsObj) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_keyPrefs, jsonEncode(prefsObj.toJson()));
    } catch (e) {
      print('[StorageService] Error saving notification prefs: $e');
    }
  }

  static Future<String?> loadApiBaseUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_keyBaseUrl);
    } catch (e) {
      return null;
    }
  }

  static Future<void> saveApiBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyBaseUrl, url);
  }

  static Future<String?> loadSelectedStation() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keySelectedStation);
  }

  static Future<void> saveSelectedStation(String stationId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keySelectedStation, stationId);
  }
}
