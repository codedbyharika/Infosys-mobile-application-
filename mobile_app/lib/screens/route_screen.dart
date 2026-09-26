import 'package:flutter/material.dart';
import '../providers/app_state.dart';
import '../config/cpcb_theme.dart';
import '../models/route_exposure_model.dart';

class RouteScreen extends StatelessWidget {
  final AppState state;
  final Function(int) onNavigateTab;

  const RouteScreen({
    super.key,
    required this.state,
    required this.onNavigateTab,
  });

  @override
  Widget build(BuildContext context) {
    final routeAnalysis = state.routeAnalysis;
    final isLoading = state.isLoadingRoute;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Route Configuration Card
          _buildRouteConfigCard(context),

          // 2. Loading state or Route Analysis Results
          if (isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(color: CpcbTheme.primaryBlue),
                    SizedBox(height: 12),
                    Text(
                      'Discretizing waypoints & estimating particulate inhalation...',
                      style: TextStyle(fontSize: 12, color: CpcbTheme.textSecondary),
                    ),
                  ],
                ),
              ),
            )
          else if (routeAnalysis != null) ...[
            // 3. Clean Corridor Savings Banner
            _buildSavingsBanner(context, routeAnalysis),

            // 4. 3-Route Comparison Cards
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Column(
                children: [
                  _buildRouteCard(
                    route: routeAnalysis.cleanCorridorRoute,
                    title: 'Route 3: Clean-Air Eco Corridor',
                    badge: 'RECOMMENDED',
                    badgeColor: const Color(0xFF10B981),
                    cardColor: const Color(0xFFF0FDF4),
                    borderColor: const Color(0xFF86EFAC),
                    isPrimary: true,
                  ),
                  const SizedBox(height: 12),
                  _buildRouteCard(
                    route: routeAnalysis.alternativeRoute,
                    title: 'Route 2: Alternative Transit Route',
                    badge: 'BALANCED',
                    badgeColor: const Color(0xFF2563EB),
                    cardColor: Colors.white,
                    borderColor: CpcbTheme.borderSubtle,
                    isPrimary: false,
                  ),
                  const SizedBox(height: 12),
                  _buildRouteCard(
                    route: routeAnalysis.directRoute,
                    title: 'Route 1: Direct Arterial Corridor',
                    badge: 'HIGH EXPOSURE',
                    badgeColor: const Color(0xFFDC2626),
                    cardColor: const Color(0xFFFEF2F2),
                    borderColor: const Color(0xFFFECACA),
                    isPrimary: false,
                  ),
                ],
              ),
            ),

            // 5. Waypoints Inspection Tile
            _buildWaypointsList(routeAnalysis),

            // 6. Action Button: Save to Exposure History
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    await state.logCurrentRouteToHistory();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: const Text('Journey successfully logged to Personal Exposure History!'),
                          backgroundColor: const Color(0xFF15803D),
                          action: SnackBarAction(
                            label: 'View History',
                            textColor: Colors.white,
                            onPressed: () => onNavigateTab(3), // History tab
                          ),
                        ),
                      );
                    }
                  },
                  icon: const Icon(Icons.bookmark_add_outlined),
                  label: const Text('Save Journey to My Exposure History'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF15803D),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                ),
              ),
            ),
          ],

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // Route Configuration Card
  Widget _buildRouteConfigCard(BuildContext context) {
    final stations = state.stations;

    final modes = [
      {'name': 'Car', 'factor': '0.65x', 'icon': Icons.directions_car},
      {'name': 'Public Transport', 'factor': '0.90x', 'icon': Icons.directions_bus},
      {'name': 'Motorcycle', 'factor': '1.25x', 'icon': Icons.two_wheeler},
      {'name': 'Cycling', 'factor': '1.40x', 'icon': Icons.pedal_bike},
      {'name': 'Walking', 'factor': '1.40x', 'icon': Icons.directions_walk},
    ];

    final profiles = [
      {'name': 'General User', 'desc': 'Standard healthy adult (1.0x)'},
      {'name': 'Asthmatic / Respiratory', 'desc': 'High particulate sensitivity (1.40x)'},
      {'name': 'Elderly (60+ Years)', 'desc': 'Reduced cardiovascular tolerance (1.25x)'},
      {'name': 'Child / Sensitive', 'desc': 'Higher minute breathing volume (1.20x)'},
    ];

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: CpcbTheme.borderSubtle),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.route, color: CpcbTheme.primaryBlue, size: 20),
              SizedBox(width: 8),
              Text(
                'Travel Route Particulate Exposure Optimizer',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Origin & Destination Selector with Swap Button
          Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    _buildStationDropdown(
                      label: 'Origin (Start)',
                      value: state.routeOrigin,
                      stations: stations,
                      onChanged: (val) {
                        if (val != null) {
                          state.setRouteParams(origin: val);
                          state.calculateRoute();
                        }
                      },
                    ),
                    const SizedBox(height: 10),
                    _buildStationDropdown(
                      label: 'Destination (End)',
                      value: state.routeDestination,
                      stations: stations,
                      onChanged: (val) {
                        if (val != null) {
                          state.setRouteParams(destination: val);
                          state.calculateRoute();
                        }
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                onPressed: () => state.swapRouteEndpoints(),
                icon: const Icon(Icons.swap_vert_circle_rounded, color: CpcbTheme.primaryBlue, size: 36),
                tooltip: 'Swap Origin & Destination',
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Transit Mode Selector Chips
          const Text(
            'TRANSIT MODE (VENTILATION FACTOR)',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              color: CpcbTheme.textSecondary,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 6),
          SizedBox(
            height: 38,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: modes.length,
              itemBuilder: (context, idx) {
                final m = modes[idx];
                final isSelected = state.routeMode == m['name'];

                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    avatar: Icon(m['icon'] as IconData, size: 16, color: isSelected ? Colors.white : CpcbTheme.textPrimary),
                    label: Text('${m['name']} (${m['factor']})'),
                    selected: isSelected,
                    onSelected: (_) {
                      state.setRouteParams(mode: m['name'] as String);
                      state.calculateRoute();
                    },
                    selectedColor: CpcbTheme.primaryBlue,
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : CpcbTheme.textPrimary,
                      fontSize: 11,
                      fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                    ),
                    backgroundColor: const Color(0xFFF1F5F9),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: 14),

          // Health Profile Dropdown
          const Text(
            'HEALTH VULNERABILITY PROFILE',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              color: CpcbTheme.textSecondary,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: state.routeHealthProfile,
                isExpanded: true,
                items: profiles.map((p) {
                  return DropdownMenuItem<String>(
                    value: p['name'],
                    child: Text(
                      '${p['name']} — ${p['desc']}',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    state.setRouteParams(profile: val);
                    state.calculateRoute();
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStationDropdown({
    required String label,
    required String value,
    required List<dynamic> stations,
    required ValueChanged<String?> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: stations.any((s) => s.id == value) ? value : (stations.isNotEmpty ? stations.first.id : null),
          isExpanded: true,
          hint: Text(label, style: const TextStyle(fontSize: 12)),
          items: stations.map((s) {
            return DropdownMenuItem<String>(
              value: s.id,
              child: Text(
                s.cleanName,
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
              ),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  // Savings Banner
  Widget _buildSavingsBanner(BuildContext context, RouteExposureAnalysis analysis) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF065F46), Color(0xFF047857)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF065F46).withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.eco, color: Colors.white, size: 28),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      '${analysis.inhalationSavingsPct}% INHALATION REDUCTION',
                      style: const TextStyle(
                        color: Color(0xFF6EE7B7),
                        fontSize: 11,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 3),
                Text(
                  analysis.advisory,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // Route Detail Card
  Widget _buildRouteCard({
    required RouteDetail route,
    required String title,
    required String badge,
    required Color badgeColor,
    required Color cardColor,
    required Color borderColor,
    required bool isPrimary,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor, width: isPrimary ? 1.5 : 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.textPrimary,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: badgeColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  badge,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    color: badgeColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            route.description,
            style: const TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
          ),
          const SizedBox(height: 14),

          // Metrics Row
          Row(
            children: [
              _buildRouteMetric('Distance', '${route.distanceKm} km', Icons.straighten),
              _buildRouteMetric('Duration', '${route.durationMin.round()} min', Icons.schedule),
              _buildRouteMetric('Avg AQI', '${route.avgAqi.round()}', Icons.air),
              _buildRouteMetric('Exposure', '${route.exposureScore.round()}/100', Icons.shield_outlined),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildRouteMetric(String label, String value, IconData icon) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 12, color: CpcbTheme.textMuted),
              const SizedBox(width: 4),
              Text(label, style: const TextStyle(fontSize: 9, color: CpcbTheme.textMuted)),
            ],
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w800,
              color: CpcbTheme.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  // Waypoints List
  Widget _buildWaypointsList(RouteExposureAnalysis analysis) {
    final waypoints = analysis.cleanCorridorRoute.waypoints;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: CpcbTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Clean-Air Eco Corridor Sampled Waypoints',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
              color: CpcbTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Continuous particulate interpolation along corridor polyline',
            style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
          ),
          const SizedBox(height: 12),

          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: waypoints.length,
            separatorBuilder: (_, __) => const Divider(height: 1, color: Color(0xFFF1F5F9)),
            itemBuilder: (context, idx) {
              final wp = waypoints[idx];
              final cat = CpcbTheme.getCategory(wp.aqi);

              return ListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                leading: Container(
                  width: 24,
                  height: 24,
                  decoration: const BoxDecoration(
                    color: Color(0xFFDCFCE7),
                    shape: BoxShape.circle,
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    '${idx + 1}',
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF15803D),
                    ),
                  ),
                ),
                title: Text(
                  wp.name,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                ),
                subtitle: Text(
                  'PM2.5: ${wp.pm25} µg/m³ • ${cat.label}',
                  style: const TextStyle(fontSize: 10, color: CpcbTheme.textMuted),
                ),
                trailing: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: cat.backgroundColor,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    '${wp.aqi.round()} AQI',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: cat.color,
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
