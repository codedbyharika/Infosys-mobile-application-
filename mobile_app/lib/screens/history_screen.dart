import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../providers/app_state.dart';
import '../config/cpcb_theme.dart';
import '../models/trip_record_model.dart';

class HistoryScreen extends StatelessWidget {
  final AppState state;

  const HistoryScreen({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    final filteredTrips = state.filteredTrips;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Aggregated Metrics Header Card
          _buildMetricsSummaryCard(context),

          // 2. Mode Filter Pills
          _buildModeFilterBar(context),

          // 3. Actions Row (Export CSV, Clear All, Add Custom)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                OutlinedButton.icon(
                  onPressed: () => _handleExportCsv(context),
                  icon: const Icon(Icons.file_download_outlined, size: 16),
                  label: const Text('Export CSV'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  onPressed: () => _showAddTripDialog(context),
                  icon: const Icon(Icons.add, size: 16),
                  label: const Text('Log Trip'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
                const Spacer(),
                if (state.tripHistory.isNotEmpty)
                  TextButton.icon(
                    onPressed: () => _confirmClearAll(context),
                    icon: const Icon(Icons.delete_outline, size: 16, color: Color(0xFFDC2626)),
                    label: const Text('Clear All', style: TextStyle(color: Color(0xFFDC2626), fontSize: 12)),
                  ),
              ],
            ),
          ),

          // 4. Trips List or Empty State
          if (filteredTrips.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Column(
                  children: [
                    const Icon(Icons.history_edu, size: 48, color: CpcbTheme.textMuted),
                    const SizedBox(height: 12),
                    const Text(
                      'No journeys recorded in this category',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: CpcbTheme.textSecondary),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Plan a route and tap "Save Journey" to track your exposure history.',
                      style: TextStyle(fontSize: 12, color: CpcbTheme.textMuted),
                    ),
                  ],
                ),
              ),
            )
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: filteredTrips.length,
              itemBuilder: (context, idx) {
                final trip = filteredTrips[idx];
                return _buildTripCard(context, trip);
              },
            ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // Summary Metrics Header Card
  Widget _buildMetricsSummaryCard(BuildContext context) {
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Personal Particulate Exposure History',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: CpcbTheme.textPrimary,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Cumulative inhaled particulate mass & transit journal',
                    style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: const BoxDecoration(
                  color: Color(0xFFEFF6FF),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.shield, color: CpcbTheme.primaryBlue, size: 20),
              ),
            ],
          ),
          const SizedBox(height: 16),

          Row(
            children: [
              _buildSummaryStat(
                '${state.lifetimeInhaledMassUg.round()} µg',
                'Lifetime Inhaled PM',
                Icons.air,
                const Color(0xFFDC2626),
              ),
              const SizedBox(width: 8),
              _buildSummaryStat(
                '${state.averageTripAqi.round()} AQI',
                'Avg Trip Exposure',
                Icons.speed,
                const Color(0xFFF59E0B),
              ),
              const SizedBox(width: 8),
              _buildSummaryStat(
                '${state.totalTripsCount}',
                'Total Journeys',
                Icons.route,
                CpcbTheme.primaryBlue,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryStat(String value, String label, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(height: 6),
            Text(
              value,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w900,
                color: color,
              ),
            ),
            Text(
              label,
              style: const TextStyle(fontSize: 9, color: CpcbTheme.textMuted),
            ),
          ],
        ),
      ),
    );
  }

  // Mode Filter Chips Bar
  Widget _buildModeFilterBar(BuildContext context) {
    final modes = [
      {'key': 'all', 'label': 'All Modes'},
      {'key': 'car', 'label': '🚗 Car'},
      {'key': 'public transport', 'label': '🚌 Public Transit'},
      {'key': 'motorcycle', 'label': '🏍️ Motorcycle'},
      {'key': 'cycling', 'label': '🚲 Cycling'},
      {'key': 'walking', 'label': '🚶 Walking'},
    ];

    return SizedBox(
      height: 38,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: modes.length,
        itemBuilder: (context, idx) {
          final m = modes[idx];
          final isSelected = state.selectedModeFilter == m['key'];

          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(m['label']!),
              selected: isSelected,
              onSelected: (_) => state.setModeFilter(m['key']!),
              selectedColor: CpcbTheme.primaryBlue,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : CpcbTheme.textPrimary,
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
              ),
              backgroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
          );
        },
      ),
    );
  }

  // Trip Record Card
  Widget _buildTripCard(BuildContext context, TripRecord trip) {
    final cat = CpcbTheme.getCategory(trip.avgAqi);
    final dateStr = DateFormat('MMM dd, yyyy • hh:mm a').format(trip.timestamp);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: CpcbTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                dateStr,
                style: const TextStyle(fontSize: 11, color: CpcbTheme.textMuted, fontWeight: FontWeight.w600),
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, size: 18, color: CpcbTheme.textMuted),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
                onPressed: () => state.deleteTrip(trip.id),
                tooltip: 'Delete journey',
              ),
            ],
          ),
          const SizedBox(height: 6),

          // Origin -> Destination
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(color: Color(0xFF15803D), shape: BoxShape.circle),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '${trip.origin} ➔ ${trip.destination}',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: CpcbTheme.textPrimary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),

          // Trip specifics
          Row(
            children: [
              _buildTripPill(trip.mode, Icons.commute),
              const SizedBox(width: 8),
              _buildTripPill('${trip.distanceKm} km', Icons.straighten),
              const SizedBox(width: 8),
              _buildTripPill('${trip.durationMin.round()} min', Icons.schedule),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: cat.backgroundColor,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  '${trip.avgAqi.round()} AQI',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: cat.color,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Exposure Mass Indicator
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Inhaled Particulate Mass', style: TextStyle(fontSize: 10, color: CpcbTheme.textMuted)),
                    Text(
                      '${trip.exposureUg} µg',
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: CpcbTheme.textPrimary),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text('Exposure Score', style: TextStyle(fontSize: 10, color: CpcbTheme.textMuted)),
                    Text(
                      '${trip.exposureScore.round()}/100',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: cat.color),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTripPill(String label, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: CpcbTheme.textSecondary),
          const SizedBox(width: 4),
          Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: CpcbTheme.textSecondary)),
        ],
      ),
    );
  }

  void _handleExportCsv(BuildContext context) {
    final trips = state.tripHistory;
    if (trips.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No trip records to export.')),
      );
      return;
    }

    final buffer = StringBuffer();
    buffer.writeln(TripRecord.csvHeader());
    for (var t in trips) {
      buffer.writeln(t.toCsvRow());
    }

    Clipboard.setData(ClipboardData(text: buffer.toString()));

    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Exposure History CSV Exported'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Your complete travel particulate exposure history has been compiled into CSV format and copied to your clipboard.',
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                buffer.toString().split('\n').take(3).join('\n') + '...',
                style: const TextStyle(fontFamily: 'monospace', fontSize: 10),
              ),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _confirmClearAll(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Clear All Exposure History?'),
        content: const Text('Are you sure you want to permanently delete all recorded travel exposure records?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626)),
            onPressed: () {
              state.clearAllTrips();
              Navigator.pop(context);
            },
            child: const Text('Clear All', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showAddTripDialog(BuildContext context) {
    final originCtrl = TextEditingController(text: 'Shivajinagar, Pune');
    final destCtrl = TextEditingController(text: 'Aundh, Pune');
    final distCtrl = TextEditingController(text: '7.5');
    final durCtrl = TextEditingController(text: '20');
    final aqiCtrl = TextEditingController(text: '78');
    String selectedMode = 'Car';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: const Text('Log Custom Travel Journey'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: originCtrl, decoration: const InputDecoration(labelText: 'Origin', isDense: true)),
                const SizedBox(height: 8),
                TextField(controller: destCtrl, decoration: const InputDecoration(labelText: 'Destination', isDense: true)),
                const SizedBox(height: 8),
                DropdownButton<String>(
                  value: selectedMode,
                  isExpanded: true,
                  items: ['Car', 'Public Transport', 'Motorcycle', 'Cycling', 'Walking']
                      .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                      .toList(),
                  onChanged: (v) {
                    if (v != null) setDialogState(() => selectedMode = v);
                  },
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(child: TextField(controller: distCtrl, decoration: const InputDecoration(labelText: 'Distance (km)', isDense: true), keyboardType: TextInputType.number)),
                    const SizedBox(width: 8),
                    Expanded(child: TextField(controller: durCtrl, decoration: const InputDecoration(labelText: 'Duration (min)', isDense: true), keyboardType: TextInputType.number)),
                  ],
                ),
                const SizedBox(height: 8),
                TextField(controller: aqiCtrl, decoration: const InputDecoration(labelText: 'Average AQI', isDense: true), keyboardType: TextInputType.number),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () {
                final dist = double.tryParse(distCtrl.text) ?? 5.0;
                final dur = double.tryParse(durCtrl.text) ?? 15.0;
                final aqi = double.tryParse(aqiCtrl.text) ?? 75.0;
                final exp = double.parse(((aqi / 100.0) * (dur / 30.0) * 18.0).toStringAsFixed(1));

                state.addCustomTrip(
                  TripRecord(
                    id: DateTime.now().millisecondsSinceEpoch.toString(),
                    timestamp: DateTime.now(),
                    origin: originCtrl.text,
                    destination: destCtrl.text,
                    mode: selectedMode,
                    distanceKm: dist,
                    durationMin: dur,
                    avgAqi: aqi,
                    category: aqi <= 50 ? 'Good' : (aqi <= 100 ? 'Moderate' : 'Sensitive'),
                    exposureUg: exp,
                    exposureScore: exp.clamp(0.0, 100.0),
                    healthProfile: state.routeHealthProfile,
                    recommendation: 'Manual custom journey logged.',
                  ),
                );
                Navigator.pop(ctx);
              },
              child: const Text('Save Journey'),
            ),
          ],
        ),
      ),
    );
  }
}
