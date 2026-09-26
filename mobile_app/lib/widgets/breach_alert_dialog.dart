import 'package:flutter/material.dart';
import '../config/cpcb_theme.dart';

class BreachAlertDialog extends StatelessWidget {
  final int threshold;
  final double currentAqi;
  final String location;

  const BreachAlertDialog({
    super.key,
    required this.threshold,
    required this.currentAqi,
    required this.location,
  });

  @override
  Widget build(BuildContext context) {
    final category = CpcbTheme.getCategory(currentAqi);

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Alert Icon
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFEE2E2),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.warning_amber_rounded,
                color: Color(0xFFDC2626),
                size: 36,
              ),
            ),
            const SizedBox(height: 16),

            const Text(
              'AQI Hazard Breach Alert',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                color: CpcbTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 6),

            Text(
              'Breach simulation for $location',
              style: const TextStyle(
                fontSize: 12,
                color: CpcbTheme.textSecondary,
              ),
            ),
            const SizedBox(height: 16),

            // Value badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: category.backgroundColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: category.color.withOpacity(0.4)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Reported Sensor AQI',
                        style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
                      ),
                      Text(
                        currentAqi.round().toString(),
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w900,
                          color: category.color,
                        ),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text(
                        'Hazard Threshold',
                        style: TextStyle(fontSize: 11, color: CpcbTheme.textSecondary),
                      ),
                      Text(
                        '$threshold AQI',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFFDC2626),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // Recommendations
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '🛡️ IMMEDIATE HEALTH ACTIONS:',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: CpcbTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '• Wear an N95/FFP2 respirator before leaving indoors.\n'
                    '• Asthmatic and elderly users: avoid arterial highways.\n'
                    '• Switch travel to Route 3 (Clean-Air Eco Corridor).',
                    style: const TextStyle(
                      fontSize: 12,
                      height: 1.4,
                      color: CpcbTheme.textPrimary,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFDC2626),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 13),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Acknowledge & Close'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
