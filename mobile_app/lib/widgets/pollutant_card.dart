import 'package:flutter/material.dart';
import '../config/cpcb_theme.dart';

class PollutantCard extends StatelessWidget {
  final String title;
  final double value;
  final String unit;
  final double safeLimit;
  final IconData icon;

  const PollutantCard({
    super.key,
    required this.title,
    required this.value,
    required this.unit,
    required this.safeLimit,
    this.icon = Icons.bubble_chart_rounded,
  });

  @override
  Widget build(BuildContext context) {
    final double ratio = (value / safeLimit).clamp(0.0, 2.5);
    Color statusColor = CpcbTheme.cpcbGood;
    String statusText = 'Safe';

    if (value > safeLimit * 1.5) {
      statusColor = CpcbTheme.cpcbPoor;
      statusText = 'High';
    } else if (value > safeLimit) {
      statusColor = CpcbTheme.cpcbSensitive;
      statusText = 'Elevated';
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: CpcbTheme.borderSubtle, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.textPrimary,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  statusText,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: statusColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                value.toStringAsFixed(1),
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                  color: statusColor,
                ),
              ),
              const SizedBox(width: 4),
              Text(
                unit,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: CpcbTheme.textMuted,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (ratio / 2.0).clamp(0.05, 1.0),
              backgroundColor: const Color(0xFFF1F5F9),
              valueColor: AlwaysStoppedAnimation<Color>(statusColor),
              minHeight: 5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Limit: $safeLimit $unit',
            style: const TextStyle(
              fontSize: 10,
              color: CpcbTheme.textMuted,
            ),
          ),
        ],
      ),
    );
  }
}
