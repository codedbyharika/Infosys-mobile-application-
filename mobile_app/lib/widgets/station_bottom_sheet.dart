import 'package:flutter/material.dart';
import '../models/station_model.dart';
import '../config/cpcb_theme.dart';
import 'pollutant_card.dart';

class StationBottomSheet extends StatelessWidget {
  final StationModel station;
  final VoidCallback onSelectForForecast;
  final VoidCallback onSelectForRoute;

  const StationBottomSheet({
    super.key,
    required this.station,
    required this.onSelectForForecast,
    required this.onSelectForRoute,
  });

  @override
  Widget build(BuildContext context) {
    final category = CpcbTheme.getCategory(station.aqi);

    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFCBD5E1),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Header
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      station.cleanName,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: CpcbTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${station.city} SmartCity Mesh • Coord (${station.lat.toStringAsFixed(3)}, ${station.lon.toStringAsFixed(3)})',
                      style: const TextStyle(
                        fontSize: 11,
                        color: CpcbTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: category.backgroundColor,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: category.color.withOpacity(0.4)),
                ),
                child: Column(
                  children: [
                    Text(
                      station.aqi.round().toString(),
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        color: category.color,
                        height: 1.0,
                      ),
                    ),
                    Text(
                      'AQI',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        color: category.color,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          // Health Advisory Callout
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: category.backgroundColor.withOpacity(0.5),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: category.color.withOpacity(0.2)),
            ),
            child: Row(
              children: [
                Icon(Icons.health_and_safety_outlined, color: category.color, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    category.healthAdvisory,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: category.color.withAlpha(220),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Weather & Traffic Quick Metrics
          Row(
            children: [
              _buildMetricChip(Icons.thermostat, '${station.temp}°C', 'Temp'),
              const SizedBox(width: 8),
              _buildMetricChip(Icons.water_drop_outlined, '${station.humidity}%', 'Humidity'),
              const SizedBox(width: 8),
              _buildMetricChip(Icons.volume_up_outlined, '${station.soundDb} dB', 'Noise'),
              const SizedBox(width: 8),
              _buildMetricChip(Icons.traffic_outlined, '${station.trafficScore.round()}/100', 'Traffic'),
            ],
          ),

          const SizedBox(height: 16),

          // Sub-pollutants Mini Grid
          SizedBox(
            height: 90,
            child: Row(
              children: [
                Expanded(
                  child: PollutantCard(
                    title: 'PM2.5',
                    value: station.pm25,
                    unit: 'µg/m³',
                    safeLimit: 60.0,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: PollutantCard(
                    title: 'PM10',
                    value: station.pm10,
                    unit: 'µg/m³',
                    safeLimit: 100.0,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: PollutantCard(
                    title: 'NO2',
                    value: station.no2,
                    unit: 'µg/m³',
                    safeLimit: 80.0,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Action Buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                    onSelectForForecast();
                  },
                  icon: const Icon(Icons.insights, size: 18),
                  label: const Text('24h Forecast'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: CpcbTheme.primaryBlue,
                    side: const BorderSide(color: CpcbTheme.primaryBlue),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                    onSelectForRoute();
                  },
                  icon: const Icon(Icons.directions, size: 18),
                  label: const Text('Plan Route'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: CpcbTheme.primaryBlue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricChip(IconData icon, String value, String label) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Column(
          children: [
            Icon(icon, size: 16, color: CpcbTheme.textSecondary),
            const SizedBox(height: 2),
            Text(
              value,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: CpcbTheme.textPrimary,
              ),
            ),
            Text(
              label,
              style: const TextStyle(
                fontSize: 9,
                color: CpcbTheme.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
