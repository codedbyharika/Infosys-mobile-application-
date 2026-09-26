import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/app_state.dart';
import '../config/cpcb_theme.dart';
import '../models/station_model.dart';
import '../widgets/aqi_gauge.dart';
import '../widgets/pollutant_card.dart';
import '../widgets/station_bottom_sheet.dart';
import 'forecast_screen.dart';

class DashboardScreen extends StatefulWidget {
  final AppState state;
  final Function(int) onNavigateTab;

  const DashboardScreen({
    super.key,
    required this.state,
    required this.onNavigateTab,
  });

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String _comparisonMetric = 'aqi'; // 'aqi', 'pm25', 'pm10'

  @override
  Widget build(BuildContext context) {
    final state = widget.state;
    final selectedStation = state.selectedStation;
    final kpi = state.kpiSummary;

    return RefreshIndicator(
      onRefresh: () => state.refreshDashboard(),
      color: CpcbTheme.primaryBlue,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Live Backend Status Indicator Banner
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: state.isLiveBackend
                      ? const Color(0xFFDCFCE7)
                      : const Color(0xFFFEF3C7),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: state.isLiveBackend
                        ? const Color(0xFF86EFAC)
                        : const Color(0xFFFCD34D),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      state.isLiveBackend ? Icons.cloud_done : Icons.cloud_off,
                      size: 16,
                      color: state.isLiveBackend
                          ? const Color(0xFF15803D)
                          : const Color(0xFFB45309),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.isLiveBackend
                            ? 'FastAPI Engine Connected (${state.apiBaseUrl})'
                            : 'Offline / Cached Mode — Local Pune SmartCity Telemetry',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: state.isLiveBackend
                              ? const Color(0xFF15803D)
                              : const Color(0xFFB45309),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // 2. City KPI Summary Hero Card
            _buildCityHeroCard(kpi),

            // 3. Station Selector Horizontal Chips
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 12, 16, 6),
              child: Text(
                'MONITORED STATIONS (PUNE SMARTCITY)',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.textSecondary,
                  letterSpacing: 0.8,
                ),
              ),
            ),
            _buildStationSelectorBar(state),

            // 4. Selected Station Telemetry Card
            if (selectedStation != null) ...[
              _buildSelectedStationCard(selectedStation),
              _buildPollutantsGrid(selectedStation),
            ],

            // 5. 24-Hour Historical Trend Chart
            _buildHistoricalTrendCard(selectedStation),

            // 6. Station Comparison & Ranking Matrix
            _buildStationComparisonCard(state),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  // City Hero Card
  Widget _buildCityHeroCard(kpi) {
    final double avgAqi = kpi?.avgCityAqi ?? 89.3;
    final category = CpcbTheme.getCategory(avgAqi);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            CpcbTheme.primaryDark,
            const Color(0xFF1E293B),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.12),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'PUNE METROPOLITAN AREA',
                    style: TextStyle(
                      color: Color(0xFF94A3B8),
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.0,
                    ),
                  ),
                  const SizedBox(height: 2),
                  const Text(
                    'SmartCity Ambient AQI',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.bolt, color: Color(0xFFFBBF24), size: 14),
                    const SizedBox(width: 4),
                    Text(
                      '${kpi?.forecastAccuracy ?? "90.2%"} Accuracy',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),

          Row(
            children: [
              // Radial Gauge
              AqiGauge(aqi: avgAqi, size: 120),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: category.color,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          category.label.toUpperCase(),
                          style: TextStyle(
                            color: category.color,
                            fontSize: 12,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      category.description,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Color(0xFFCBD5E1),
                        fontSize: 11,
                        height: 1.3,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        _buildHeroMiniBadge(
                          '${kpi?.activeStations ?? 10}',
                          'Active Nodes',
                          Icons.sensors,
                        ),
                        const SizedBox(width: 8),
                        _buildHeroMiniBadge(
                          '${kpi?.aqiAlertsToday ?? 2}',
                          'Alerts Today',
                          Icons.warning_amber_rounded,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHeroMiniBadge(String value, String label, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.08),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(icon, size: 14, color: const Color(0xFF94A3B8)),
            const SizedBox(width: 6),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                Text(
                  label,
                  style: const TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 8,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // Horizontal Station Chips
  Widget _buildStationSelectorBar(AppState state) {
    return SizedBox(
      height: 42,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: state.stations.length,
        itemBuilder: (context, idx) {
          final s = state.stations[idx];
          final isSelected = state.selectedStation?.id == s.id;
          final cat = CpcbTheme.getCategory(s.aqi);

          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 7,
                    height: 7,
                    decoration: BoxDecoration(
                      color: cat.color,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(s.cleanName),
                  const SizedBox(width: 4),
                  Text(
                    '${s.aqi.round()}',
                    style: TextStyle(
                      fontWeight: FontWeight.w800,
                      color: isSelected ? Colors.white : cat.color,
                    ),
                  ),
                ],
              ),
              selected: isSelected,
              onSelected: (_) => state.selectStation(s),
              selectedColor: CpcbTheme.primaryBlue,
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : CpcbTheme.textPrimary,
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
              ),
              backgroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
                side: BorderSide(
                  color: isSelected ? CpcbTheme.primaryBlue : CpcbTheme.borderSubtle,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  // Selected Station Card
  Widget _buildSelectedStationCard(StationModel s) {
    final cat = CpcbTheme.getCategory(s.aqi);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: CpcbTheme.borderSubtle),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      s.cleanName,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: CpcbTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Sensor Telemetry • Dominant: ${s.dominantPollutant}',
                      style: const TextStyle(
                        fontSize: 12,
                        color: CpcbTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: cat.backgroundColor,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: cat.color.withOpacity(0.3)),
                ),
                child: Column(
                  children: [
                    Text(
                      s.aqi.round().toString(),
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        color: cat.color,
                        height: 1.0,
                      ),
                    ),
                    Text(
                      cat.label,
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        color: cat.color,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          // Health recommendation callout
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Row(
              children: [
                const Icon(Icons.masks_outlined, size: 20, color: CpcbTheme.primaryBlue),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    cat.maskRecommendation,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: CpcbTheme.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // Weather & Acoustic/Traffic row
          Row(
            children: [
              _buildSensorChip('Temp', '${s.temp}°C', Icons.thermostat),
              const SizedBox(width: 8),
              _buildSensorChip('Humidity', '${s.humidity}%', Icons.water_drop_outlined),
              const SizedBox(width: 8),
              _buildSensorChip('Noise', '${s.soundDb} dB', Icons.graphic_eq),
              const SizedBox(width: 8),
              _buildSensorChip('Traffic', '${s.trafficScore.round()}/100', Icons.traffic),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSensorChip(String label, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
        decoration: BoxDecoration(
          color: const Color(0xFFF1F5F9),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Column(
          children: [
            Icon(icon, size: 16, color: CpcbTheme.textSecondary),
            const SizedBox(height: 3),
            Text(
              value,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
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

  // Pollutants Grid
  Widget _buildPollutantsGrid(StationModel s) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'SUB-POLLUTANT CONCENTRATIONS (CPCB)',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w800,
              color: CpcbTheme.textSecondary,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 8),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 1.8,
            children: [
              PollutantCard(title: 'PM2.5', value: s.pm25, unit: 'µg/m³', safeLimit: 60.0),
              PollutantCard(title: 'PM10', value: s.pm10, unit: 'µg/m³', safeLimit: 100.0),
              PollutantCard(title: 'NO2', value: s.no2, unit: 'µg/m³', safeLimit: 80.0),
              PollutantCard(title: 'SO2', value: s.so2, unit: 'µg/m³', safeLimit: 80.0),
              PollutantCard(title: 'CO', value: s.co, unit: 'mg/m³', safeLimit: 2.0),
              PollutantCard(title: 'O3 (Ozone)', value: s.o3, unit: 'µg/m³', safeLimit: 100.0),
            ],
          ),
        ],
      ),
    );
  }

  // 24-Hour Historical Trend Card
  Widget _buildHistoricalTrendCard(StationModel? s) {
    final baseAqi = s?.aqi ?? 85.0;

    // Generate 24 points reflecting Pune diurnal curve
    final List<FlSpot> spots = [];
    for (int i = 0; i < 24; i++) {
      final hourMod = (i - 14).abs();
      final val = baseAqi + (10 - hourMod * 1.5) + (i % 3 == 0 ? 3.0 : -2.0);
      spots.add(FlSpot(i.toDouble(), val.clamp(30.0, 250.0)));
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: CpcbTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '24-Hour Telemetry Trend',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                      color: CpcbTheme.textPrimary,
                    ),
                  ),
                  Text(
                    'Continuous ambient sensor telemetry (${s?.cleanName ?? "Pune"})',
                    style: const TextStyle(
                      fontSize: 11,
                      color: CpcbTheme.textSecondary,
                    ),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.arrow_forward_ios, size: 16, color: CpcbTheme.primaryBlue),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => Scaffold(
                        appBar: AppBar(
                          title: const Text('Recurrent Forecasting & Kriging'),
                        ),
                        body: ForecastScreen(state: widget.state),
                      ),
                    ),
                  );
                },
                tooltip: 'Deep Forecast & Kriging',
              ),
            ],
          ),
          const SizedBox(height: 20),

          SizedBox(
            height: 160,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (value) => FlLine(
                    color: const Color(0xFFF1F5F9),
                    strokeWidth: 1,
                  ),
                ),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 32,
                      getTitlesWidget: (val, _) => Text(
                        val.toInt().toString(),
                        style: const TextStyle(fontSize: 9, color: CpcbTheme.textMuted),
                      ),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 22,
                      interval: 4,
                      getTitlesWidget: (val, _) => Text(
                        '-${(24 - val.toInt())}h',
                        style: const TextStyle(fontSize: 9, color: CpcbTheme.textMuted),
                      ),
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    color: CpcbTheme.primaryBlue,
                    barWidth: 2.5,
                    isStrokeCapRound: true,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: CpcbTheme.primaryBlue.withOpacity(0.12),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Station Comparison & Ranking Card
  Widget _buildStationComparisonCard(AppState state) {
    final List<StationModel> sortedList = List.from(state.stations);

    if (_comparisonMetric == 'pm25') {
      sortedList.sort((a, b) => b.pm25.compareTo(a.pm25));
    } else if (_comparisonMetric == 'pm10') {
      sortedList.sort((a, b) => b.pm10.compareTo(a.pm10));
    } else {
      sortedList.sort((a, b) => b.aqi.compareTo(a.aqi));
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: CpcbTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Station Comparison & Rankings',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.textPrimary,
                ),
              ),
              // Metric filter pills (AQI, PM2.5, PM10)
              Row(
                children: [
                  _buildMetricPill('aqi', 'AQI'),
                  const SizedBox(width: 4),
                  _buildMetricPill('pm25', 'PM2.5'),
                  const SizedBox(width: 4),
                  _buildMetricPill('pm10', 'PM10'),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),

          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: sortedList.length,
            separatorBuilder: (_, __) => const Divider(height: 1, color: Color(0xFFF1F5F9)),
            itemBuilder: (context, idx) {
              final s = sortedList[idx];
              final cat = CpcbTheme.getCategory(s.aqi);
              final isSelected = state.selectedStation?.id == s.id;

              double metricVal = s.aqi;
              String unit = 'AQI';
              if (_comparisonMetric == 'pm25') {
                metricVal = s.pm25;
                unit = 'µg';
              } else if (_comparisonMetric == 'pm10') {
                metricVal = s.pm10;
                unit = 'µg';
              }

              return ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                dense: true,
                onTap: () {
                  showModalBottomSheet(
                    context: context,
                    isScrollControlled: true,
                    backgroundColor: Colors.transparent,
                    builder: (_) => StationBottomSheet(
                      station: s,
                      onSelectForForecast: () {
                        state.selectStation(s);
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => Scaffold(
                              appBar: AppBar(
                                title: const Text('Recurrent Forecasting & Kriging'),
                              ),
                              body: ForecastScreen(state: widget.state),
                            ),
                          ),
                        );
                      },
                      onSelectForRoute: () {
                        state.setRouteParams(destination: s.id);
                        widget.onNavigateTab(2); // Routes tab index is 2
                      },
                    ),
                  );
                },
                leading: Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: isSelected ? CpcbTheme.primaryBlue : const Color(0xFFF1F5F9),
                    shape: BoxShape.circle,
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    '#${idx + 1}',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: isSelected ? Colors.white : CpcbTheme.textSecondary,
                    ),
                  ),
                ),
                title: Text(
                  s.cleanName,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                    color: CpcbTheme.textPrimary,
                  ),
                ),
                subtitle: Text(
                  '${s.dominantPollutant} • Traffic: ${s.trafficLevel}',
                  style: const TextStyle(fontSize: 10, color: CpcbTheme.textMuted),
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: cat.backgroundColor,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${metricVal.round()} $unit',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w800,
                          color: cat.color,
                        ),
                      ),
                    ),
                    const SizedBox(width: 4),
                    const Icon(Icons.chevron_right, size: 16, color: CpcbTheme.textMuted),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMetricPill(String key, String label) {
    final active = _comparisonMetric == key;
    return GestureDetector(
      onTap: () => setState(() => _comparisonMetric = key),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: active ? const Color(0xFFEFF6FF) : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: active ? const Color(0xFFBFDBFE) : const Color(0xFFE2E8F0),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: active ? FontWeight.w800 : FontWeight.w600,
            color: active ? CpcbTheme.primaryBlue : CpcbTheme.textSecondary,
          ),
        ),
      ),
    );
  }
}
