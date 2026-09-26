import 'package:flutter/material.dart';
import '../providers/app_state.dart';
import '../config/cpcb_theme.dart';
import '../widgets/breach_alert_dialog.dart';
import 'dashboard_screen.dart';
import 'map_screen.dart';
import 'route_screen.dart';
import 'history_screen.dart';
import 'forecast_screen.dart';
import 'settings_screen.dart';

class MainScreen extends StatefulWidget {
  final AppState state;

  const MainScreen({super.key, required this.state});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentTabIndex = 0;

  void _onTabTapped(int index) {
    setState(() => _currentTabIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    final state = widget.state;
    final selectedStation = state.selectedStation;

    final screens = [
      DashboardScreen(state: state, onNavigateTab: _onTabTapped),
      MapScreen(state: state, onNavigateTab: _onTabTapped),
      RouteScreen(state: state, onNavigateTab: _onTabTapped),
      HistoryScreen(state: state),
      SettingsScreen(state: state),
    ];

    final titles = [
      'EcoAir Intelligence',
      'GIS Pollution Map',
      'Travel Route Advisory',
      'Exposure History',
      'Alerts & Settings',
    ];

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              titles[_currentTabIndex],
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: CpcbTheme.textPrimary,
              ),
            ),
            Row(
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(
                    color: state.isLiveBackend ? const Color(0xFF16A34A) : const Color(0xFFF59E0B),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  state.isLiveBackend ? 'FastAPI Connected' : 'Local Pune Telemetry',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: state.isLiveBackend ? const Color(0xFF16A34A) : const Color(0xFFD97706),
                  ),
                ),
                if (selectedStation != null) ...[
                  const Text(' • ', style: TextStyle(fontSize: 10, color: CpcbTheme.textMuted)),
                  Text(
                    selectedStation.cleanName,
                    style: const TextStyle(fontSize: 10, color: CpcbTheme.textSecondary),
                  ),
                ],
              ],
            ),
          ],
        ),
        actions: [
          // Station quick selector popup
          if (state.stations.isNotEmpty)
            PopupMenuButton<String>(
              icon: const Icon(Icons.location_on_outlined, color: CpcbTheme.primaryBlue),
              tooltip: 'Switch Active Station',
              onSelected: (id) {
                final target = state.stations.firstWhere((s) => s.id == id);
                state.selectStation(target);
              },
              itemBuilder: (context) {
                return state.stations.map((s) {
                  final cat = CpcbTheme.getCategory(s.aqi);
                  return PopupMenuItem<String>(
                    value: s.id,
                    child: Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(color: cat.color, shape: BoxShape.circle),
                        ),
                        const SizedBox(width: 8),
                        Expanded(child: Text(s.cleanName, style: const TextStyle(fontSize: 12))),
                        Text(
                          '${s.aqi.round()} AQI',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: cat.color),
                        ),
                      ],
                    ),
                  );
                }).toList();
              },
            ),

          // Simulate Breach Alert Bell
          IconButton(
            icon: const Icon(Icons.notifications_outlined, color: CpcbTheme.textPrimary),
            tooltip: 'Simulate AQI Hazard Alert',
            onPressed: () {
              showDialog(
                context: context,
                builder: (_) => BreachAlertDialog(
                  threshold: state.notificationPrefs.aqiThreshold,
                  currentAqi: (state.notificationPrefs.aqiThreshold + 22).toDouble(),
                  location: selectedStation?.cleanName ?? 'Hadapsar Gadital, Pune',
                ),
              );
            },
          ),

          // User Profile Quick Menu
          PopupMenuButton<String>(
            icon: CircleAvatar(
              radius: 14,
              backgroundColor: (state.currentUser?.isGuest ?? true)
                  ? const Color(0xFF64748B)
                  : CpcbTheme.primaryBlue,
              child: Text(
                state.currentUser?.initials ?? 'G',
                style: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
              ),
            ),
            tooltip: 'Account Profile (${state.currentUser?.name ?? "Guest"})',
            onSelected: (val) async {
              if (val == 'settings') {
                _onTabTapped(4); // Switch to Alerts & Settings tab
              } else if (val == 'logout') {
                await state.logout();
              }
            },
            itemBuilder: (ctx) => [
              PopupMenuItem(
                enabled: false,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      state.currentUser?.name ?? 'Guest Explorer',
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 13,
                        color: CpcbTheme.textPrimary,
                      ),
                    ),
                    Text(
                      state.currentUser?.email.isNotEmpty == true
                          ? state.currentUser!.email
                          : 'Guest Mode',
                      style: const TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Sensitivity: ${state.currentUser?.healthProfile ?? "General"}',
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF0284C7),
                      ),
                    ),
                  ],
                ),
              ),
              const PopupMenuDivider(),
              const PopupMenuItem(
                value: 'settings',
                child: Row(
                  children: [
                    Icon(Icons.tune_outlined, size: 16, color: CpcbTheme.textSecondary),
                    SizedBox(width: 8),
                    Text('Preferences & Alert Config', style: TextStyle(fontSize: 12)),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(
                      (state.currentUser?.isGuest ?? true) ? Icons.login : Icons.logout,
                      size: 16,
                      color: const Color(0xFFDC2626),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      (state.currentUser?.isGuest ?? true) ? 'Sign In' : 'Sign Out',
                      style: const TextStyle(fontSize: 12, color: Color(0xFFDC2626), fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: IndexedStack(
        index: _currentTabIndex,
        children: screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTabIndex,
        onTap: _onTabTapped,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: CpcbTheme.primaryBlue,
        unselectedItemColor: CpcbTheme.textMuted,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map_outlined),
            activeIcon: Icon(Icons.map),
            label: 'AQI Map',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.alt_route_outlined),
            activeIcon: Icon(Icons.alt_route),
            label: 'Routes',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shield_outlined),
            activeIcon: Icon(Icons.shield),
            label: 'My AQI',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings),
            label: 'Alerts',
          ),
        ],
      ),
    );
  }
}
