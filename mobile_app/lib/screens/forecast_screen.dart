import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/app_state.dart';
import '../config/cpcb_theme.dart';
import '../models/forecast_model.dart';
import '../services/api_service.dart';

class ForecastScreen extends StatefulWidget {
  final AppState state;

  const ForecastScreen({super.key, required this.state});

  @override
  State<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends State<ForecastScreen> {
  int _horizon = 24;
  String _architecture = 'GRU'; // 'GRU' or 'LSTM'

  // Spatial Kriging inputs
  final TextEditingController _latController = TextEditingController(text: '18.5204');
  final TextEditingController _lonController = TextEditingController(text: '73.8567');
  String _interpMethod = 'kriging'; // 'kriging' or 'idw'
  Map<String, dynamic>? _interpResult;
  bool _isInterpolating = false;

  @override
  void dispose() {
    _latController.dispose();
    _lonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = widget.state;
    final forecast = state.forecast;
    final isLoading = state.isLoadingForecast;

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Forecast Configuration Header Card
          _buildForecastConfigCard(state),

          // 2. Loading state or Forecast Charts
          if (isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 40),
              child: Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(color: CpcbTheme.primaryBlue),
                    SizedBox(height: 12),
                    Text(
                      'Running multi-step PyTorch GRU recurrent inference...',
                      style: TextStyle(fontSize: 12, color: CpcbTheme.textSecondary),
                    ),
                  ],
                ),
              ),
            )
          else if (forecast != null) ...[
            _buildTrajectoryChartCard(forecast),
            _buildPollutantBreakdownChartCard(forecast),
          ],

          // 3. Spatial Interpolation Tool (Ordinary Kriging / IDW)
          _buildSpatialInterpolationCard(),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildForecastConfigCard(AppState state) {
    final stations = state.stations;
    final selectedStation = state.selectedStation;

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
                  Icon(Icons.timeline, color: CpcbTheme.primaryBlue, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Deep Recurrent AQI Forecasting',
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
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  'Module 2',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    color: CpcbTheme.primaryBlue,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Station Selector
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: selectedStation?.id,
                isExpanded: true,
                items: stations.map((s) {
                  return DropdownMenuItem<String>(
                    value: s.id,
                    child: Text(
                      '${s.cleanName} (${s.aqi.round()} AQI)',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    final target = stations.firstWhere((s) => s.id == val);
                    state.selectStation(target);
                  }
                },
              ),
            ),
          ),
          const SizedBox(height: 14),

          // Architecture Selector (GRU vs LSTM)
          Row(
            children: [
              const Text(
                'Architecture: ',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
              ),
              ChoiceChip(
                label: const Text('PyTorch GRU (Recommended)'),
                selected: _architecture == 'GRU',
                onSelected: (_) {
                  setState(() => _architecture = 'GRU');
                  if (selectedStation != null) {
                    state.fetchForecast(location: selectedStation.id, horizon: _horizon, architecture: 'GRU');
                  }
                },
                selectedColor: CpcbTheme.primaryBlue,
                labelStyle: TextStyle(
                  color: _architecture == 'GRU' ? Colors.white : CpcbTheme.textPrimary,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: const Text('LSTM'),
                selected: _architecture == 'LSTM',
                onSelected: (_) {
                  setState(() => _architecture = 'LSTM');
                  if (selectedStation != null) {
                    state.fetchForecast(location: selectedStation.id, horizon: _horizon, architecture: 'LSTM');
                  }
                },
                selectedColor: CpcbTheme.primaryBlue,
                labelStyle: TextStyle(
                  color: _architecture == 'LSTM' ? Colors.white : CpcbTheme.textPrimary,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Horizon Slider
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Forecast Window Horizon:',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
              ),
              Text(
                '$_horizon Hours Ahead',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: CpcbTheme.primaryBlue),
              ),
            ],
          ),
          Slider(
            value: _horizon.toDouble(),
            min: 4,
            max: 24,
            divisions: 20,
            activeColor: CpcbTheme.primaryBlue,
            onChanged: (val) {
              setState(() => _horizon = val.toInt());
            },
            onChangeEnd: (val) {
              if (selectedStation != null) {
                state.fetchForecast(location: selectedStation.id, horizon: val.toInt(), architecture: _architecture);
              }
            },
          ),
        ],
      ),
    );
  }

  // Trajectory Chart Card with Confidence Intervals
  Widget _buildTrajectoryChartCard(ForecastModel f) {
    final cis = f.confidenceIntervals;
    final List<FlSpot> predSpots = [];
    final List<FlSpot> upperSpots = [];
    final List<FlSpot> lowerSpots = [];

    for (int i = 0; i < cis.length; i++) {
      predSpots.add(FlSpot((i + 1).toDouble(), cis[i].predictedAqi));
      upperSpots.add(FlSpot((i + 1).toDouble(), cis[i].upperBound));
      lowerSpots.add(FlSpot((i + 1).toDouble(), cis[i].lowerBound));
    }

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
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Multi-Step AQI Trajectory',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      color: CpcbTheme.textPrimary,
                    ),
                  ),
                  Text(
                    '${f.architecture} Network with Expanding 95% Confidence Cone',
                    style: const TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0FDF4),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                ),
                child: Text(
                  'End: ${f.predictedEndpointAqi.round()} AQI',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF15803D),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),

          SizedBox(
            height: 180,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (_) => FlLine(color: const Color(0xFFF1F5F9), strokeWidth: 1),
                ),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 32,
                      getTitlesWidget: (v, _) => Text(v.toInt().toString(), style: const TextStyle(fontSize: 9)),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 22,
                      interval: 4,
                      getTitlesWidget: (v, _) => Text('+${v.toInt()}h', style: const TextStyle(fontSize: 9)),
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  // Upper Bound
                  LineChartBarData(
                    spots: upperSpots,
                    isCurved: true,
                    color: const Color(0xFF94A3B8).withOpacity(0.5),
                    barWidth: 1.5,
                    dashArray: [4, 4],
                    dotData: const FlDotData(show: false),
                  ),
                  // Predicted Line
                  LineChartBarData(
                    spots: predSpots,
                    isCurved: true,
                    color: CpcbTheme.primaryBlue,
                    barWidth: 3.0,
                    isStrokeCapRound: true,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: CpcbTheme.primaryBlue.withOpacity(0.12),
                    ),
                  ),
                  // Lower Bound
                  LineChartBarData(
                    spots: lowerSpots,
                    isCurved: true,
                    color: const Color(0xFF94A3B8).withOpacity(0.5),
                    barWidth: 1.5,
                    dashArray: [4, 4],
                    dotData: const FlDotData(show: false),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          // Legend
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildChartLegend(CpcbTheme.primaryBlue, 'Predicted AQI (GRU)'),
              const SizedBox(width: 16),
              _buildChartLegend(const Color(0xFF94A3B8), '95% Confidence Band', isDashed: true),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildChartLegend(Color color, String label, {bool isDashed = false}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 16,
          height: 3,
          color: color,
        ),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 10, color: CpcbTheme.textSecondary)),
      ],
    );
  }

  // Multi-pollutant Breakdown
  Widget _buildPollutantBreakdownChartCard(ForecastModel f) {
    final pb = f.pollutantBreakdown;
    final pm25List = pb['pm25'] ?? [];
    final pm10List = pb['pm10'] ?? [];
    final no2List = pb['no2'] ?? [];

    final List<FlSpot> pm25Spots = [];
    final List<FlSpot> pm10Spots = [];
    final List<FlSpot> no2Spots = [];

    for (int i = 0; i < pm25List.length; i++) {
      pm25Spots.add(FlSpot((i + 1).toDouble(), pm25List[i]));
      if (i < pm10List.length) pm10Spots.add(FlSpot((i + 1).toDouble(), pm10List[i]));
      if (i < no2List.length) no2Spots.add(FlSpot((i + 1).toDouble(), no2List[i]));
    }

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
          const Text(
            'Multi-Pollutant Projection Curves',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w800,
              color: CpcbTheme.textPrimary,
            ),
          ),
          const Text(
            'Projected particulate (PM2.5, PM10) and combustion gas (NO2) concentrations',
            style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
          ),
          const SizedBox(height: 16),

          SizedBox(
            height: 160,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (_) => FlLine(color: const Color(0xFFF1F5F9), strokeWidth: 1),
                ),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 32,
                      getTitlesWidget: (v, _) => Text(v.toInt().toString(), style: const TextStyle(fontSize: 9)),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 22,
                      interval: 4,
                      getTitlesWidget: (v, _) => Text('+${v.toInt()}h', style: const TextStyle(fontSize: 9)),
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: pm10Spots,
                    isCurved: true,
                    color: const Color(0xFFF59E0B),
                    barWidth: 2.2,
                    dotData: const FlDotData(show: false),
                  ),
                  LineChartBarData(
                    spots: pm25Spots,
                    isCurved: true,
                    color: const Color(0xFFDC2626),
                    barWidth: 2.2,
                    dotData: const FlDotData(show: false),
                  ),
                  LineChartBarData(
                    spots: no2Spots,
                    isCurved: true,
                    color: const Color(0xFF8B5CF6),
                    barWidth: 2.2,
                    dotData: const FlDotData(show: false),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildChartLegend(const Color(0xFFDC2626), 'PM2.5'),
              const SizedBox(width: 14),
              _buildChartLegend(const Color(0xFFF59E0B), 'PM10'),
              const SizedBox(width: 14),
              _buildChartLegend(const Color(0xFF8B5CF6), 'NO2'),
            ],
          ),
        ],
      ),
    );
  }

  // Spatial Interpolation Tool
  Widget _buildSpatialInterpolationCard() {
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
              Icon(Icons.location_searching, color: CpcbTheme.primaryBlue, size: 20),
              SizedBox(width: 8),
              Text(
                'Geostatistical Spatial Interpolation',
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
            'Ordinary Kriging & IDW estimation for arbitrary GPS coordinates',
            style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
          ),
          const SizedBox(height: 14),

          // Coordinate Presets
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              _buildCoordPresetChip('Hinjawadi', 18.5913, 73.7389),
              _buildCoordPresetChip('Swargate', 18.5018, 73.8586),
              _buildCoordPresetChip('Viman Nagar', 18.5679, 73.9143),
              _buildCoordPresetChip('Kothrud', 18.5074, 73.8077),
            ],
          ),
          const SizedBox(height: 12),

          // Inputs Row
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _latController,
                  decoration: const InputDecoration(
                    labelText: 'Latitude',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: TextField(
                  controller: _lonController,
                  decoration: const InputDecoration(
                    labelText: 'Longitude',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Method Selector
          Row(
            children: [
              ChoiceChip(
                label: const Text('Ordinary Kriging'),
                selected: _interpMethod == 'kriging',
                onSelected: (_) => setState(() => _interpMethod = 'kriging'),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: const Text('IDW (p=2.0)'),
                selected: _interpMethod == 'idw',
                onSelected: (_) => setState(() => _interpMethod = 'idw'),
              ),
              const Spacer(),
              ElevatedButton(
                onPressed: _isInterpolating ? null : _runInterpolation,
                child: _isInterpolating
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Interpolate'),
              ),
            ],
          ),

          if (_interpResult != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Row(
                children: [
                  Text(
                    '${_interpResult!['estimated_aqi']}',
                    style: const TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.w900,
                      color: CpcbTheme.primaryBlue,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Estimated Ambient AQI (${_interpResult!['method'].toString().toUpperCase()})',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
                        ),
                        Text(
                          'Confidence: ${_interpResult!['confidence_score']} • Uncertainty: ±${_interpResult!['uncertainty_score']} AQI',
                          style: const TextStyle(fontSize: 10, color: CpcbTheme.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCoordPresetChip(String name, double lat, double lon) {
    return ActionChip(
      label: Text(name, style: const TextStyle(fontSize: 11)),
      onPressed: () {
        _latController.text = lat.toString();
        _lonController.text = lon.toString();
        _runInterpolation();
      },
    );
  }

  void _runInterpolation() async {
    final lat = double.tryParse(_latController.text) ?? 18.5204;
    final lon = double.tryParse(_lonController.text) ?? 73.8567;

    setState(() => _isInterpolating = true);
    final res = await ApiService.interpolatePoint(lat: lat, lon: lon, method: _interpMethod);
    setState(() {
      _isInterpolating = false;
      _interpResult = res;
    });
  }
}
