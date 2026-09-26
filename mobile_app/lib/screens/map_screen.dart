import 'dart:math';
import 'package:flutter/material.dart';
import '../providers/app_state.dart';
import '../config/cpcb_theme.dart';
import '../models/station_model.dart';
import '../widgets/station_bottom_sheet.dart';
import '../services/api_service.dart';
import 'forecast_screen.dart';

class MapScreen extends StatefulWidget {
  final AppState state;
  final Function(int) onNavigateTab;

  const MapScreen({
    super.key,
    required this.state,
    required this.onNavigateTab,
  });

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  bool _showRoutes = true;
  bool _showHotspots = true;
  double _zoomLevel = 1.0;
  Offset _panOffset = Offset.zero;

  // Selected interpolated point
  Map<String, dynamic>? _interpolatedPoint;
  bool _isInterpolating = false;

  @override
  Widget build(BuildContext context) {
    final state = widget.state;
    final stations = state.stations;
    final routeAnalysis = state.routeAnalysis;

    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      body: Stack(
        children: [
          // 1. Interactive GIS Canvas Map
          GestureDetector(
            onScaleUpdate: (details) {
              setState(() {
                _zoomLevel = (_zoomLevel * details.scale).clamp(0.8, 3.5);
                _panOffset += details.focalPointDelta;
              });
            },
            onTapUp: (details) {
              _handleMapTap(details.localPosition, stations);
            },
            child: ClipRect(
              child: CustomPaint(
                size: Size.infinite,
                painter: _PuneGisMapPainter(
                  stations: stations,
                  selectedStation: state.selectedStation,
                  routeAnalysis: _showRoutes ? routeAnalysis : null,
                  showHotspots: _showHotspots,
                  zoom: _zoomLevel,
                  pan: _panOffset,
                ),
              ),
            ),
          ),

          // 2. Map Control Floating Bar (Top)
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.08),
                          blurRadius: 10,
                          offset: const Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.map_outlined, color: CpcbTheme.primaryBlue, size: 20),
                        const SizedBox(width: 8),
                        const Expanded(
                          child: Text(
                            'Pune SmartCity Mesh Network',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w800,
                              color: CpcbTheme.textPrimary,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFDCFCE7),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            '${stations.length} Nodes',
                            style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF15803D),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          // 3. Map Layers Overlay Toggles (Right Side)
          Positioned(
            right: 16,
            top: 76,
            child: Column(
              children: [
                _buildMapFloatingButton(
                  icon: Icons.alt_route,
                  label: 'Routes',
                  isActive: _showRoutes,
                  onTap: () => setState(() => _showRoutes = !_showRoutes),
                ),
                const SizedBox(height: 8),
                _buildMapFloatingButton(
                  icon: Icons.bubble_chart,
                  label: 'Hotspots',
                  isActive: _showHotspots,
                  onTap: () => setState(() => _showHotspots = !_showHotspots),
                ),
                const SizedBox(height: 8),
                _buildMapFloatingButton(
                  icon: Icons.zoom_in,
                  label: '+',
                  isActive: false,
                  onTap: () => setState(() => _zoomLevel = (_zoomLevel + 0.3).clamp(0.8, 3.5)),
                ),
                const SizedBox(height: 8),
                _buildMapFloatingButton(
                  icon: Icons.zoom_out,
                  label: '-',
                  isActive: false,
                  onTap: () => setState(() => _zoomLevel = (_zoomLevel - 0.3).clamp(0.8, 3.5)),
                ),
                const SizedBox(height: 8),
                _buildMapFloatingButton(
                  icon: Icons.center_focus_strong,
                  label: 'Reset',
                  isActive: false,
                  onTap: () => setState(() {
                    _zoomLevel = 1.0;
                    _panOffset = Offset.zero;
                  }),
                ),
              ],
            ),
          ),

          // 4. Interpolated Coordinate Callout Card
          if (_interpolatedPoint != null)
            Positioned(
              left: 16,
              right: 16,
              bottom: 96,
              child: _buildInterpolatedCallout(),
            ),

          // 5. CPCB Standard Legend (Bottom)
          Positioned(
            left: 16,
            right: 16,
            bottom: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.95),
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.06),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildLegendItem(CpcbTheme.cpcbGood, '0-50 Good'),
                  _buildLegendItem(CpcbTheme.cpcbSatisfactory, '51-100 Mod'),
                  _buildLegendItem(CpcbTheme.cpcbSensitive, '101-150 Sens'),
                  _buildLegendItem(CpcbTheme.cpcbPoor, '151-200 Poor'),
                  _buildLegendItem(CpcbTheme.cpcbVeryPoor, '201+ V.Poor'),
                ],
              ),
            ),
          ),

          if (_isInterpolating)
            const Positioned(
              top: 80,
              left: 0,
              right: 0,
              child: Center(
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2)),
                        SizedBox(width: 10),
                        Text('Running Ordinary Kriging Interpolation...', style: TextStyle(fontSize: 11)),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildMapFloatingButton({
    required IconData icon,
    required String label,
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: isActive ? CpcbTheme.primaryBlue : Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(
          icon,
          size: 20,
          color: isActive ? Colors.white : CpcbTheme.textPrimary,
        ),
      ),
    );
  }

  Widget _buildLegendItem(Color color, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          text,
          style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w600, color: CpcbTheme.textPrimary),
        ),
      ],
    );
  }

  Widget _buildInterpolatedCallout() {
    final aqi = _interpolatedPoint?['estimated_aqi'] ?? 80.0;
    final cat = CpcbTheme.getCategory(aqi.toDouble());
    final lat = _interpolatedPoint?['latitude'] ?? 18.52;
    final lon = _interpolatedPoint?['longitude'] ?? 73.85;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.12),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: cat.backgroundColor,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              aqi.round().toString(),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w900,
                color: cat.color,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Ordinary Kriging Spatial Estimate',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
                ),
                Text(
                  'Target: (${lat.toStringAsFixed(3)}, ${lon.toStringAsFixed(3)}) • Nearest node: ${_interpolatedPoint?['distance_km']}km',
                  style: const TextStyle(fontSize: 10, color: CpcbTheme.textSecondary),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 16),
            onPressed: () => setState(() => _interpolatedPoint = null),
          ),
        ],
      ),
    );
  }

  void _handleMapTap(Offset localPos, List<StationModel> stations) async {
    // Check if clicked near an existing station
    final size = MediaQuery.of(context).size;
    for (var s in stations) {
      final pos = _PuneGisMapPainter.latLonToScreen(
        s.lat,
        s.lon,
        size,
        _zoomLevel,
        _panOffset,
      );
      if ((pos - localPos).distance < 24) {
        widget.state.selectStation(s);
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Colors.transparent,
          builder: (_) => StationBottomSheet(
            station: s,
            onSelectForForecast: () {
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
              widget.state.setRouteParams(destination: s.id);
              widget.onNavigateTab(2); // Routes tab is index 2
            },
          ),
        );
        return;
      }
    }

    // Otherwise calculate Kriging Interpolation at this clicked coordinate!
    final coords = _PuneGisMapPainter.screenToLatLon(
      localPos,
      size,
      _zoomLevel,
      _panOffset,
    );

    setState(() => _isInterpolating = true);
    final res = await ApiService.interpolatePoint(lat: coords[0], lon: coords[1]);
    setState(() {
      _isInterpolating = false;
      _interpolatedPoint = res;
    });
  }
}

class _PuneGisMapPainter extends CustomPainter {
  final List<StationModel> stations;
  final StationModel? selectedStation;
  final dynamic routeAnalysis;
  final bool showHotspots;
  final double zoom;
  final Offset pan;

  // Pune Geographic Bounds
  static const double minLat = 18.440;
  static const double maxLat = 18.640;
  static const double minLon = 73.720;
  static const double maxLon = 73.950;

  _PuneGisMapPainter({
    required this.stations,
    required this.selectedStation,
    required this.routeAnalysis,
    required this.showHotspots,
    required this.zoom,
    required this.pan,
  });

  static Offset latLonToScreen(
    double lat,
    double lon,
    Size size,
    double zoom,
    Offset pan,
  ) {
    final xNorm = (lon - minLon) / (maxLon - minLon);
    final yNorm = 1.0 - ((lat - minLat) / (maxLat - minLat)); // Flip Y for screen coords

    final cx = size.width / 2;
    final cy = size.height / 2;

    final x = (xNorm * size.width - cx) * zoom + cx + pan.dx;
    final y = (yNorm * size.height - cy) * zoom + cy + pan.dy;
    return Offset(x, y);
  }

  static List<double> screenToLatLon(
    Offset screen,
    Size size,
    double zoom,
    Offset pan,
  ) {
    final cx = size.width / 2;
    final cy = size.height / 2;

    final xNorm = ((screen.dx - cx - pan.dx) / zoom + cx) / size.width;
    final yNorm = ((screen.dy - cy - pan.dy) / zoom + cy) / size.height;

    final lon = minLon + xNorm * (maxLon - minLon);
    final lat = minLat + (1.0 - yNorm) * (maxLat - minLat);
    return [lat, lon];
  }

  @override
  void paint(Canvas canvas, Size size) {
    // 1. Draw River & Geography Background Features
    _drawBaseGeography(canvas, size);

    // 2. Draw Route Polylines if available
    if (routeAnalysis != null) {
      _drawRoutePolylines(canvas, size);
    }

    // 3. Draw Station Hotspot Glows
    if (showHotspots) {
      for (var s in stations) {
        if (s.aqi > 100) {
          final pos = latLonToScreen(s.lat, s.lon, size, zoom, pan);
          final paint = Paint()
            ..color = const Color(0xFFEA580C).withOpacity(0.18)
            ..style = PaintingStyle.fill;
          canvas.drawCircle(pos, 32 * zoom, paint);
        }
      }
    }

    // 4. Draw Station Pins & Labels
    for (var s in stations) {
      final pos = latLonToScreen(s.lat, s.lon, size, zoom, pan);
      final isSelected = selectedStation?.id == s.id;
      final cat = CpcbTheme.getCategory(s.aqi);

      // Pin base shadow
      canvas.drawCircle(
        pos + const Offset(0, 2),
        14,
        Paint()..color = Colors.black.withOpacity(0.15),
      );

      // Pin circle
      final pinPaint = Paint()..color = cat.color;
      canvas.drawCircle(pos, isSelected ? 15 : 12, pinPaint);

      // Inner white dot
      canvas.drawCircle(pos, 4, Paint()..color = Colors.white);

      // Pin label
      final textPainter = TextPainter(
        text: TextSpan(
          text: '${s.cleanName}\n${s.aqi.round()} AQI',
          style: TextStyle(
            color: CpcbTheme.textPrimary,
            fontSize: 9,
            fontWeight: FontWeight.w800,
            backgroundColor: Colors.white.withOpacity(0.85),
          ),
        ),
        textAlign: TextAlign.center,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();
      textPainter.paint(canvas, pos + Offset(-textPainter.width / 2, 14));
    }
  }

  void _drawBaseGeography(Canvas canvas, Size size) {
    // Waterway / Mula-Mutha river path across Pune
    final riverPoints = [
      latLonToScreen(18.570, 73.740, size, zoom, pan),
      latLonToScreen(18.540, 73.800, size, zoom, pan),
      latLonToScreen(18.528, 73.840, size, zoom, pan),
      latLonToScreen(18.535, 73.880, size, zoom, pan),
      latLonToScreen(18.545, 73.930, size, zoom, pan),
    ];

    final riverPath = Path();
    riverPath.moveTo(riverPoints.first.dx, riverPoints.first.dy);
    for (int i = 1; i < riverPoints.length; i++) {
      riverPath.lineTo(riverPoints[i].dx, riverPoints[i].dy);
    }

    final riverPaint = Paint()
      ..color = const Color(0xFFBAE6FD).withOpacity(0.7)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 14 * zoom
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    canvas.drawPath(riverPath, riverPaint);
  }

  void _drawRoutePolylines(Canvas canvas, Size size) {
    final r1 = routeAnalysis.directRoute;
    final r2 = routeAnalysis.alternativeRoute;
    final r3 = routeAnalysis.cleanCorridorRoute;

    // Draw Route 1 (Arterial - Red)
    _drawPolyline(canvas, size, r1.polyline, const Color(0xFFDC2626), 4.0, isDashed: false);

    // Draw Route 2 (Alternative - Blue)
    _drawPolyline(canvas, size, r2.polyline, const Color(0xFF2563EB), 3.5, isDashed: false);

    // Draw Route 3 (Clean Eco Corridor - Green)
    _drawPolyline(canvas, size, r3.polyline, const Color(0xFF10B981), 5.5, isDashed: false);

    // Draw Start ('S') and Destination ('D') Badges
    if (r3.polyline.isNotEmpty) {
      final startPos = latLonToScreen(r3.polyline.first.lat, r3.polyline.first.lon, size, zoom, pan);
      final destPos = latLonToScreen(r3.polyline.last.lat, r3.polyline.last.lon, size, zoom, pan);

      _drawEndpointMarker(canvas, startPos, 'S', const Color(0xFF15803D));
      _drawEndpointMarker(canvas, destPos, 'D', const Color(0xFFDC2626));
    }
  }

  void _drawPolyline(
    Canvas canvas,
    Size size,
    List<dynamic> points,
    Color color,
    double width, {
    bool isDashed = false,
  }) {
    if (points.length < 2) return;

    final path = Path();
    final first = latLonToScreen(points.first.lat, points.first.lon, size, zoom, pan);
    path.moveTo(first.dx, first.dy);

    for (int i = 1; i < points.length; i++) {
      final pt = latLonToScreen(points[i].lat, points[i].lon, size, zoom, pan);
      path.lineTo(pt.dx, pt.dy);
    }

    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = width * zoom
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    canvas.drawPath(path, paint);
  }

  void _drawEndpointMarker(Canvas canvas, Offset pos, String text, Color color) {
    canvas.drawCircle(pos, 13, Paint()..color = color);
    canvas.drawCircle(pos, 10, Paint()..color = Colors.white);

    final textPainter = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w900,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, pos - Offset(textPainter.width / 2, textPainter.height / 2));
  }

  @override
  bool shouldRepaint(covariant _PuneGisMapPainter old) => true;
}
