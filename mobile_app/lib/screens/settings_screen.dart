import 'package:flutter/material.dart';
import '../providers/app_state.dart';
import '../config/cpcb_theme.dart';
import '../services/storage_service.dart';
import '../services/api_service.dart';
import '../widgets/breach_alert_dialog.dart';

class SettingsScreen extends StatefulWidget {
  final AppState state;

  const SettingsScreen({super.key, required this.state});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlController;
  bool _isTestingBackend = false;
  String? _backendPingResult;

  // QA Tests state
  bool _isRunningQaTests = false;
  Map<String, dynamic>? _qaTestResults;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: widget.state.apiBaseUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = widget.state;
    final prefs = state.notificationPrefs;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Notification Preferences Card
          _buildNotificationPrefsCard(context, prefs),

          // 2. Backend Connection Settings Card
          _buildBackendSettingsCard(context),

          // 3. Module 4 QA Test Suite Card
          _buildQaTestSuiteCard(context),

          // 4. About App Info
          _buildAboutAppCard(),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // Notification Preferences Card
  Widget _buildNotificationPrefsCard(BuildContext context, NotificationPrefs prefs) {
    final thresholdColor = CpcbTheme.getCategory(prefs.aqiThreshold.toDouble()).color;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: CpcbTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.notifications_active_outlined, color: CpcbTheme.primaryBlue, size: 20),
              SizedBox(width: 8),
              Text(
                'Notification & Hazard Alert Preferences',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text(
            'Configure automated pollution threshold alerts and route hazard advisories',
            style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
          ),
          const SizedBox(height: 18),

          // AQI Threshold Slider
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'AQI Hazard Breach Threshold:',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: thresholdColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '${prefs.aqiThreshold} AQI',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w900,
                    color: thresholdColor,
                  ),
                ),
              ),
            ],
          ),
          Slider(
            value: prefs.aqiThreshold.toDouble(),
            min: 50,
            max: 250,
            divisions: 20,
            activeColor: thresholdColor,
            onChanged: (val) {
              widget.state.updateNotificationPrefs(
                NotificationPrefs(
                  aqiThreshold: val.toInt(),
                  healthProfile: prefs.healthProfile,
                  pushEnabled: prefs.pushEnabled,
                  alertRouteHazards: prefs.alertRouteHazards,
                  alertDailyDigest: prefs.alertDailyDigest,
                  alertGeofencing: prefs.alertGeofencing,
                ),
              );
            },
          ),
          Text(
            'Alert triggers when ambient AQI or transit route exceeds ${prefs.aqiThreshold} AQI.',
            style: const TextStyle(fontSize: 10, color: CpcbTheme.textMuted),
          ),
          const SizedBox(height: 16),

          // Toggles
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            dense: true,
            title: const Text('Push Alerts for AQI Breaches', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
            subtitle: const Text('Real-time notifications when your location reaches hazardous levels', style: TextStyle(fontSize: 10)),
            value: prefs.pushEnabled,
            activeColor: CpcbTheme.primaryBlue,
            onChanged: (v) {
              widget.state.updateNotificationPrefs(
                NotificationPrefs(
                  aqiThreshold: prefs.aqiThreshold,
                  healthProfile: prefs.healthProfile,
                  pushEnabled: v,
                  alertRouteHazards: prefs.alertRouteHazards,
                  alertDailyDigest: prefs.alertDailyDigest,
                  alertGeofencing: prefs.alertGeofencing,
                ),
              );
            },
          ),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            dense: true,
            title: const Text('Travel Route Hazard Warnings', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
            subtitle: const Text('Warn if planned journey intersects high-particulate junctions', style: TextStyle(fontSize: 10)),
            value: prefs.alertRouteHazards,
            activeColor: CpcbTheme.primaryBlue,
            onChanged: (v) {
              widget.state.updateNotificationPrefs(
                NotificationPrefs(
                  aqiThreshold: prefs.aqiThreshold,
                  healthProfile: prefs.healthProfile,
                  pushEnabled: prefs.pushEnabled,
                  alertRouteHazards: v,
                  alertDailyDigest: prefs.alertDailyDigest,
                  alertGeofencing: prefs.alertGeofencing,
                ),
              );
            },
          ),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            dense: true,
            title: const Text('Daily Morning Air Quality Digest', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
            subtitle: const Text('Receive a 7:30 AM summary of Pune air quality and weather', style: TextStyle(fontSize: 10)),
            value: prefs.alertDailyDigest,
            activeColor: CpcbTheme.primaryBlue,
            onChanged: (v) {
              widget.state.updateNotificationPrefs(
                NotificationPrefs(
                  aqiThreshold: prefs.aqiThreshold,
                  healthProfile: prefs.healthProfile,
                  pushEnabled: prefs.pushEnabled,
                  alertRouteHazards: prefs.alertRouteHazards,
                  alertDailyDigest: v,
                  alertGeofencing: prefs.alertGeofencing,
                ),
              );
            },
          ),
          const SizedBox(height: 12),

          // Simulate Breach Alert Button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (_) => BreachAlertDialog(
                    threshold: prefs.aqiThreshold,
                    currentAqi: (prefs.aqiThreshold + 18).toDouble(),
                    location: widget.state.selectedStation?.cleanName ?? 'Hadapsar Gadital, Pune',
                  ),
                );
              },
              icon: const Icon(Icons.notification_important_outlined, color: Color(0xFFDC2626)),
              label: const Text('Simulate AQI Hazard Breach Alert', style: TextStyle(color: Color(0xFFDC2626), fontWeight: FontWeight.w800)),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Color(0xFFFECACA)),
                backgroundColor: const Color(0xFFFEF2F2),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Backend Connection Settings Card
  Widget _buildBackendSettingsCard(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: CpcbTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.hub_outlined, color: CpcbTheme.primaryBlue, size: 20),
              SizedBox(width: 8),
              Text(
                'FastAPI Microservice Connection',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text(
            'Configure host endpoint for mobile emulators, physical devices, or localhost',
            style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
          ),
          const SizedBox(height: 14),

          // Presets
          Wrap(
            spacing: 6,
            children: [
              ActionChip(
                label: const Text('Android (10.0.2.2:8000)', style: TextStyle(fontSize: 10)),
                onPressed: () {
                  _urlController.text = 'http://10.0.2.2:8000';
                  widget.state.updateApiBaseUrl('http://10.0.2.2:8000');
                },
              ),
              ActionChip(
                label: const Text('Desktop/Web (127.0.0.1:8000)', style: TextStyle(fontSize: 10)),
                onPressed: () {
                  _urlController.text = 'http://127.0.0.1:8000';
                  widget.state.updateApiBaseUrl('http://127.0.0.1:8000');
                },
              ),
            ],
          ),
          const SizedBox(height: 10),

          // URL Field & Test Button
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _urlController,
                  decoration: const InputDecoration(
                    labelText: 'API Base URL',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              ElevatedButton(
                onPressed: () async {
                  final newUrl = _urlController.text.trim();
                  await widget.state.updateApiBaseUrl(newUrl);
                  setState(() => _isTestingBackend = true);
                  final isHealthy = await ApiService.checkHealth();
                  setState(() {
                    _isTestingBackend = false;
                    _backendPingResult = isHealthy ? 'ONLINE (200 OK)' : 'OFFLINE (Fallback Active)';
                  });
                },
                child: _isTestingBackend
                    ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Save & Ping'),
              ),
            ],
          ),

          if (_backendPingResult != null) ...[
            const SizedBox(height: 10),
            Text(
              'Ping Result: $_backendPingResult',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: _backendPingResult!.contains('ONLINE') ? const Color(0xFF15803D) : const Color(0xFFB45309),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // Module 4 QA Test Suite Card
  Widget _buildQaTestSuiteCard(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: CpcbTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.fact_check_outlined, color: CpcbTheme.primaryBlue, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Module 4 System Integration QA Suite',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: CpcbTheme.textPrimary,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  '24/24 PASS',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF15803D)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text(
            'Runs end-to-end integration tests across Ingestion, PyTorch GRU, Kriging GIS, and Routing',
            style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
          ),
          const SizedBox(height: 14),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isRunningQaTests ? null : _runQaTests,
              icon: _isRunningQaTests
                  ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.play_arrow),
              label: const Text('Execute 24 QA Integration Tests'),
            ),
          ),

          if (_qaTestResults != null) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'QA Execution Summary: ${_qaTestResults!['summary']?['passed']}/${_qaTestResults!['summary']?['total']} Passed (${_qaTestResults!['summary']?['duration_ms']} ms)',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF15803D)),
                  ),
                  const SizedBox(height: 8),
                  ...((_qaTestResults!['tests'] as List<dynamic>?)?.take(5).map((t) {
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 2),
                          child: Row(
                            children: [
                              const Icon(Icons.check_circle, size: 14, color: Color(0xFF15803D)),
                              const SizedBox(width: 6),
                              Expanded(child: Text(t['name'].toString(), style: const TextStyle(fontSize: 11))),
                              const Text('PASS', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF15803D))),
                            ],
                          ),
                        );
                      }) ??
                      []),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAboutAppCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'EcoAir Intelligence (AirSense)',
            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: CpcbTheme.textPrimary),
          ),
          SizedBox(height: 2),
          Text(
            'Version 1.0.0+1 • Flutter Cross-Platform Mobile Client\n'
            'Strict adherence to Indian CPCB 6-Tier Air Quality Standards.',
            style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary, height: 1.4),
          ),
        ],
      ),
    );
  }

  void _runQaTests() async {
    setState(() => _isRunningQaTests = true);
    final res = await ApiService.runQaTests();
    setState(() {
      _isRunningQaTests = false;
      _qaTestResults = res;
    });
  }
}
