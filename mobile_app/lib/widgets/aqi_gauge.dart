import 'dart:math';
import 'package:flutter/material.dart';
import '../config/cpcb_theme.dart';

class AqiGauge extends StatelessWidget {
  final double aqi;
  final double size;

  const AqiGauge({
    super.key,
    required this.aqi,
    this.size = 180,
  });

  @override
  Widget build(BuildContext context) {
    final category = CpcbTheme.getCategory(aqi);

    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          CustomPaint(
            size: Size(size, size),
            painter: _AqiGaugePainter(aqi: aqi),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'AQI',
                style: TextStyle(
                  fontSize: size * 0.08,
                  fontWeight: FontWeight.w700,
                  color: CpcbTheme.textSecondary,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                aqi.round().toString(),
                style: TextStyle(
                  fontSize: size * 0.26,
                  fontWeight: FontWeight.w900,
                  color: category.color,
                  height: 1.0,
                ),
              ),
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                decoration: BoxDecoration(
                  color: category.backgroundColor,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: category.color.withOpacity(0.3), width: 1),
                ),
                child: Text(
                  category.label,
                  style: TextStyle(
                    fontSize: size * 0.075,
                    fontWeight: FontWeight.w800,
                    color: category.color,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _AqiGaugePainter extends CustomPainter {
  final double aqi;

  _AqiGaugePainter({required this.aqi});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - 12;

    const startAngle = 135 * (pi / 180);
    const sweepAngle = 270 * (pi / 180);
    const strokeWidth = 14.0;

    // Background Arc
    final bgPaint = Paint()
      ..color = const Color(0xFFE2E8F0)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      bgPaint,
    );

    // Active Gradient Arc
    final double pct = (aqi / 350.0).clamp(0.02, 1.0);
    final activeSweep = sweepAngle * pct;

    final gradient = SweepGradient(
      startAngle: startAngle,
      endAngle: startAngle + sweepAngle,
      colors: const [
        CpcbTheme.cpcbGood,
        CpcbTheme.cpcbSatisfactory,
        CpcbTheme.cpcbSensitive,
        CpcbTheme.cpcbPoor,
        CpcbTheme.cpcbVeryPoor,
        CpcbTheme.cpcbHazardous,
      ],
      stops: const [0.0, 0.25, 0.45, 0.65, 0.85, 1.0],
    );

    final activePaint = Paint()
      ..shader = gradient.createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      activeSweep,
      false,
      activePaint,
    );
  }

  @override
  bool shouldRepaint(covariant _AqiGaugePainter oldDelegate) => oldDelegate.aqi != aqi;
}
