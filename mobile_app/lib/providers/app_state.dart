import 'package:flutter/material.dart';
import '../config/api_config.dart';
import '../models/station_model.dart';
import '../models/forecast_model.dart';
import '../models/route_exposure_model.dart';
import '../models/trip_record_model.dart';
import '../models/kpi_summary_model.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class AppState extends ChangeNotifier {
  // Authentication State
  UserModel? _currentUser;
  bool _isLoggedIn = false;

  // State variables
  List<StationModel> _stations = [];
  StationModel? _selectedStation;
  KpiSummaryModel? _kpiSummary;
  ForecastModel? _forecast;
  RouteExposureAnalysis? _routeAnalysis;
  List<TripRecord> _tripHistory = [];

  String _selectedModeFilter = 'all';
  NotificationPrefs _notificationPrefs = const NotificationPrefs();
  bool _isLiveBackend = false;
  bool _isLoadingDashboard = false;
  bool _isLoadingForecast = false;
  bool _isLoadingRoute = false;
  String _apiBaseUrl = ApiConfig.defaultEmulatorBaseUrl;

  // Selected parameters for Route Planning
  String _routeOrigin = 'Hadapsar_Gadital_01';
  String _routeDestination = 'BopadiSquare_65';
  String _routeMode = 'Car';
  String _routeHealthProfile = 'General User';

  // Getters
  UserModel? get currentUser => _currentUser;
  bool get isLoggedIn => _isLoggedIn;
  List<StationModel> get stations => _stations;
  StationModel? get selectedStation => _selectedStation;
  KpiSummaryModel? get kpiSummary => _kpiSummary;
  ForecastModel? get forecast => _forecast;
  RouteExposureAnalysis? get routeAnalysis => _routeAnalysis;
  List<TripRecord> get tripHistory => _tripHistory;
  String get selectedModeFilter => _selectedModeFilter;
  NotificationPrefs get notificationPrefs => _notificationPrefs;
  bool get isLiveBackend => _isLiveBackend;
  bool get isLoadingDashboard => _isLoadingDashboard;
  bool get isLoadingForecast => _isLoadingForecast;
  bool get isLoadingRoute => _isLoadingRoute;
  String get apiBaseUrl => _apiBaseUrl;

  String get routeOrigin => _routeOrigin;
  String get routeDestination => _routeDestination;
  String get routeMode => _routeMode;
  String get routeHealthProfile => _routeHealthProfile;

  List<TripRecord> get filteredTrips {
    if (_selectedModeFilter == 'all') return _tripHistory;
    return _tripHistory
        .where((t) => t.mode.toLowerCase() == _selectedModeFilter.toLowerCase())
        .toList();
  }

  // Summary Metrics for Personal Exposure History
  int get totalTripsCount => _tripHistory.length;

  double get lifetimeInhaledMassUg =>
      _tripHistory.fold(0.0, (acc, t) => acc + t.exposureUg);

  double get averageTripAqi => _tripHistory.isEmpty
      ? 0.0
      : (_tripHistory.fold(0.0, (acc, t) => acc + t.avgAqi) / _tripHistory.length);

  double get bestTripAqi {
    if (_tripHistory.isEmpty) return 0.0;
    return _tripHistory.map((t) => t.avgAqi).reduce((a, b) => a < b ? a : b);
  }

  // Initialization
  Future<void> init() async {
    // 0. Load saved User Session
    final savedUser = await StorageService.loadUserSession();
    if (savedUser != null) {
      _currentUser = savedUser;
      _isLoggedIn = true;
      _routeHealthProfile = savedUser.healthProfile;
    }

    // 1. Load saved API base URL
    final savedUrl = await StorageService.loadApiBaseUrl();
    if (savedUrl != null && savedUrl.isNotEmpty) {
      _apiBaseUrl = savedUrl;
      ApiConfig.currentBaseUrl = savedUrl;
    }

    // 2. Load Notification Preferences
    _notificationPrefs = await StorageService.loadNotificationPrefs();

    // 3. Load Trip History
    _tripHistory = await StorageService.loadTrips();

    // 4. Fetch Stations & KPI
    await refreshDashboard();

    // 5. Pre-calculate default Route exposure
    await calculateRoute(
      origin: _routeOrigin,
      destination: _routeDestination,
      mode: _routeMode,
      profile: _routeHealthProfile,
    );
  }

  // Refresh Dashboard
  Future<void> refreshDashboard() async {
    _isLoadingDashboard = true;
    notifyListeners();

    try {
      final stnRes = await ApiService.getStations();
      _stations = stnRes.data;
      _isLiveBackend = stnRes.isLive;

      // Select first station or retain saved
      if (_stations.isNotEmpty) {
        final savedStationId = await StorageService.loadSelectedStation();
        _selectedStation = _stations.firstWhere(
          (s) => s.id == savedStationId,
          orElse: () => _stations.first,
        );
      }

      final kpiRes = await ApiService.getKpiSummary();
      _kpiSummary = kpiRes.data;

      // Fetch forecast for selected station
      if (_selectedStation != null) {
        await fetchForecast(location: _selectedStation!.id, horizon: 24, architecture: 'GRU');
      }
    } catch (e) {
      print('[AppState] Error refreshing dashboard: $e');
    } finally {
      _isLoadingDashboard = false;
      notifyListeners();
    }
  }

  // Select Station
  void selectStation(StationModel station) {
    _selectedStation = station;
    StorageService.saveSelectedStation(station.id);
    fetchForecast(location: station.id, horizon: 24, architecture: 'GRU');
    notifyListeners();
  }

  // Fetch Forecast
  Future<void> fetchForecast({
    required String location,
    int horizon = 24,
    String architecture = 'GRU',
  }) async {
    _isLoadingForecast = true;
    notifyListeners();

    final res = await ApiService.getForecast(
      locationName: location,
      horizonHours: horizon,
      architecture: architecture,
    );

    _forecast = res.data;
    _isLoadingForecast = false;
    notifyListeners();
  }

  // Set Route parameters
  void setRouteParams({
    String? origin,
    String? destination,
    String? mode,
    String? profile,
  }) {
    if (origin != null) _routeOrigin = origin;
    if (destination != null) _routeDestination = destination;
    if (mode != null) _routeMode = mode;
    if (profile != null) _routeHealthProfile = profile;
    notifyListeners();
  }

  void swapRouteEndpoints() {
    final temp = _routeOrigin;
    _routeOrigin = _routeDestination;
    _routeDestination = temp;
    calculateRoute(
      origin: _routeOrigin,
      destination: _routeDestination,
      mode: _routeMode,
      profile: _routeHealthProfile,
    );
  }

  // Calculate Route Exposure
  Future<void> calculateRoute({
    String? origin,
    String? destination,
    String? mode,
    String? profile,
  }) async {
    _isLoadingRoute = true;
    notifyListeners();

    final org = origin ?? _routeOrigin;
    final dst = destination ?? _routeDestination;
    final m = mode ?? _routeMode;
    final p = profile ?? _routeHealthProfile;

    final res = await ApiService.calculateRouteExposure(
      origin: org,
      destination: dst,
      transportMode: m,
      healthProfile: p,
    );

    _routeAnalysis = res.data;
    _isLoadingRoute = false;
    notifyListeners();
  }

  // Log Journey to Exposure History
  Future<void> logCurrentRouteToHistory() async {
    if (_routeAnalysis == null) return;

    final recRoute = _routeAnalysis!.cleanCorridorRoute;
    final trip = TripRecord(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      timestamp: DateTime.now(),
      origin: _cleanName(_routeAnalysis!.origin),
      destination: _cleanName(_routeAnalysis!.destination),
      mode: _routeAnalysis!.transportMode,
      distanceKm: recRoute.distanceKm,
      durationMin: recRoute.durationMin,
      avgAqi: recRoute.avgAqi,
      category: recRoute.avgAqi <= 50 ? 'Good' : (recRoute.avgAqi <= 100 ? 'Moderate' : 'Sensitive Groups'),
      exposureUg: double.parse((recRoute.exposureScore * 0.85).toStringAsFixed(1)),
      exposureScore: recRoute.exposureScore,
      healthProfile: _routeAnalysis!.healthProfile,
      recommendation: _routeAnalysis!.advisory,
    );

    await StorageService.addTrip(trip);
    _tripHistory.insert(0, trip);
    notifyListeners();
  }

  Future<void> addCustomTrip(TripRecord trip) async {
    await StorageService.addTrip(trip);
    _tripHistory.insert(0, trip);
    notifyListeners();
  }

  Future<void> deleteTrip(String id) async {
    await StorageService.deleteTrip(id);
    _tripHistory.removeWhere((t) => t.id == id);
    notifyListeners();
  }

  Future<void> clearAllTrips() async {
    await StorageService.clearAllTrips();
    _tripHistory.clear();
    notifyListeners();
  }

  void setModeFilter(String filter) {
    _selectedModeFilter = filter;
    notifyListeners();
  }

  // Update Notification Preferences
  Future<void> updateNotificationPrefs(NotificationPrefs newPrefs) async {
    _notificationPrefs = newPrefs;
    await StorageService.saveNotificationPrefs(newPrefs);
    notifyListeners();
  }

  // Update API Base URL
  Future<void> updateApiBaseUrl(String newUrl) async {
    _apiBaseUrl = newUrl;
    ApiConfig.currentBaseUrl = newUrl;
    await StorageService.saveApiBaseUrl(newUrl);
    await refreshDashboard();
  }

  String _cleanName(String raw) {
    return raw
        .replaceAll(RegExp(r'_\d+$'), '')
        .replaceAll('_', ' ')
        .replaceAll('BopadiSquare', 'Bopodi Square')
        .trim();
  }

  // ── Authentication Methods ───────────────────────────────────────────────
  Future<String?> login(String email, String password, {bool rememberMe = true}) async {
    final cleanEmail = email.trim().toLowerCase();
    final cleanPassword = password.trim();

    if (cleanEmail.isEmpty || cleanPassword.isEmpty) {
      return 'Please enter both email and password.';
    }

    try {
      final registeredUsers = await StorageService.loadRegisteredUsers();
      if (!registeredUsers.containsKey(cleanEmail)) {
        return 'No account found with this email. Please sign up.';
      }

      final userData = registeredUsers[cleanEmail]!;
      if (userData['password'] != cleanPassword) {
        return 'Incorrect password. Please try again.';
      }

      final user = UserModel(
        id: 'usr_${cleanEmail.hashCode.abs()}',
        email: cleanEmail,
        name: userData['name'] ?? 'AirSense User',
        healthProfile: userData['healthProfile'] ?? _routeHealthProfile,
        lastLogin: DateTime.now(),
      );

      _currentUser = user;
      _isLoggedIn = true;
      _routeHealthProfile = user.healthProfile;

      if (rememberMe) {
        await StorageService.saveUserSession(user);
      } else {
        await StorageService.clearUserSession();
      }

      notifyListeners();
      return null; // Success
    } catch (e) {
      return 'Login failed: $e';
    }
  }

  Future<String?> register({
    required String email,
    required String password,
    required String name,
    required String healthProfile,
  }) async {
    final cleanEmail = email.trim().toLowerCase();
    final cleanPassword = password.trim();
    final cleanName = name.trim();

    if (cleanEmail.isEmpty || cleanPassword.isEmpty || cleanName.isEmpty) {
      return 'Please fill in all required fields.';
    }

    if (!cleanEmail.contains('@') || !cleanEmail.contains('.')) {
      return 'Please enter a valid email address.';
    }

    if (cleanPassword.length < 6) {
      return 'Password must be at least 6 characters long.';
    }

    try {
      final registeredUsers = await StorageService.loadRegisteredUsers();
      if (registeredUsers.containsKey(cleanEmail)) {
        return 'An account with this email already exists. Please sign in.';
      }

      registeredUsers[cleanEmail] = {
        'password': cleanPassword,
        'name': cleanName,
        'healthProfile': healthProfile,
      };
      await StorageService.saveRegisteredUsers(registeredUsers);

      final user = UserModel(
        id: 'usr_${cleanEmail.hashCode.abs()}',
        email: cleanEmail,
        name: cleanName,
        healthProfile: healthProfile,
        lastLogin: DateTime.now(),
      );

      _currentUser = user;
      _isLoggedIn = true;
      _routeHealthProfile = healthProfile;
      await StorageService.saveUserSession(user);

      notifyListeners();
      return null; // Success
    } catch (e) {
      return 'Registration failed: $e';
    }
  }

  Future<void> logout() async {
    _currentUser = null;
    _isLoggedIn = false;
    await StorageService.clearUserSession();
    notifyListeners();
  }

  void continueAsGuest() {
    _currentUser = const UserModel(
      id: 'guest_user',
      email: 'guest@ecoair.org',
      name: 'Guest Explorer',
      healthProfile: 'General User',
      isGuest: true,
    );
    _isLoggedIn = true;
    notifyListeners();
  }
}
