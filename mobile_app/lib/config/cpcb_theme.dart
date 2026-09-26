import 'package:flutter/material.dart';

class CpcbCategory {
  final String label;
  final Color color;
  final Color backgroundColor;
  final String description;
  final String healthAdvisory;
  final String maskRecommendation;
  final int minAqi;
  final int maxAqi;

  const CpcbCategory({
    required this.label,
    required this.color,
    required this.backgroundColor,
    required this.description,
    required this.healthAdvisory,
    required this.maskRecommendation,
    required this.minAqi,
    required this.maxAqi,
  });
}

class CpcbTheme {
  // Official CPCB 6-Tier Color Palette
  static const Color cpcbGood = Color(0xFF16A34A);         // 0 - 50
  static const Color cpcbSatisfactory = Color(0xFFCA8A04); // 51 - 100
  static const Color cpcbSensitive = Color(0xFFEA580C);    // 101 - 150
  static const Color cpcbPoor = Color(0xFFDC2626);         // 151 - 200
  static const Color cpcbVeryPoor = Color(0xFF7C3AED);     // 201 - 300
  static const Color cpcbHazardous = Color(0xFF991B1B);    // 301+

  // App Aesthetic Colors
  static const Color primaryBlue = Color(0xFF2563EB);
  static const Color primaryDark = Color(0xFF0F172A);
  static const Color surfaceDark = Color(0xFF1E293B);
  static const Color surfaceCard = Color(0xFFFFFFFF);
  static const Color backgroundLight = Color(0xFFF8FAFC);
  static const Color borderSubtle = Color(0xFFE2E8F0);
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textMuted = Color(0xFF94A3B8);
  static const Color accentCyan = Color(0xFF06B6D4);
  static const Color accentGreen = Color(0xFF10B981);

  static CpcbCategory getCategory(double aqi) {
    if (aqi <= 50) {
      return const CpcbCategory(
        label: 'Good',
        color: cpcbGood,
        backgroundColor: Color(0xFFDCFCE7),
        description: 'Air quality is considered satisfactory, and air pollution poses little or no risk.',
        healthAdvisory: 'Ideal for all outdoor activities. Enjoy the fresh air!',
        maskRecommendation: 'No mask required',
        minAqi: 0,
        maxAqi: 50,
      );
    } else if (aqi <= 100) {
      return const CpcbCategory(
        label: 'Moderate',
        color: cpcbSatisfactory,
        backgroundColor: Color(0xFFFEF9C3),
        description: 'Air quality is acceptable; however, moderate breathing discomfort may occur for hypersensitive individuals.',
        healthAdvisory: 'Sensitive individuals should limit prolonged outdoor exertion.',
        maskRecommendation: 'Mask optional, recommended for respiratory patients',
        minAqi: 51,
        maxAqi: 100,
      );
    } else if (aqi <= 150) {
      return const CpcbCategory(
        label: 'Sensitive Groups',
        color: cpcbSensitive,
        backgroundColor: Color(0xFFFFEDD5),
        description: 'Members of sensitive groups may experience health effects. The general public is less likely to be affected.',
        healthAdvisory: 'Children, asthmatics, and elderly individuals should avoid intense outdoor sports.',
        maskRecommendation: 'N95 mask recommended along busy roads',
        minAqi: 101,
        maxAqi: 150,
      );
    } else if (aqi <= 200) {
      return const CpcbCategory(
        label: 'Poor',
        color: cpcbPoor,
        backgroundColor: Color(0xFFFEE2E2),
        description: 'Breathing discomfort to most people on prolonged exposure. Triggers asthma attacks.',
        healthAdvisory: 'Avoid strenuous outdoor activities. Use air purifiers indoors.',
        maskRecommendation: 'N95 or FFP2 mask strongly advised',
        minAqi: 151,
        maxAqi: 200,
      );
    } else if (aqi <= 300) {
      return const CpcbCategory(
        label: 'Very Poor',
        color: cpcbVeryPoor,
        backgroundColor: Color(0xFFEDE9FE),
        description: 'Respiratory illness on prolonged exposure. Significant risk of bronchial irritation.',
        healthAdvisory: 'Remain indoors. Keep windows closed and avoid non-essential transit.',
        maskRecommendation: 'N95 / N99 mask mandatory outdoors',
        minAqi: 201,
        maxAqi: 300,
      );
    } else {
      return const CpcbCategory(
        label: 'Hazardous',
        color: cpcbHazardous,
        backgroundColor: Color(0xFFFFE4E6),
        description: 'Severe health alert! Emergency conditions. The entire population is more likely to be affected.',
        healthAdvisory: 'Emergency health alert. Stay strictly indoors with high-efficiency air purification.',
        maskRecommendation: 'High-grade N99 respirator mandatory',
        minAqi: 301,
        maxAqi: 500,
      );
    }
  }

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      primaryColor: primaryBlue,
      scaffoldBackgroundColor: backgroundLight,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryBlue,
        brightness: Brightness.light,
        surface: surfaceCard,
        onSurface: textPrimary,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: surfaceCard,
        foregroundColor: textPrimary,
        elevation: 0,
        scrolledUnderElevation: 1,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.2,
        ),
      ),
      cardTheme: CardTheme(
        color: surfaceCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: borderSubtle, width: 1),
        ),
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surfaceCard,
        selectedItemColor: primaryBlue,
        unselectedItemColor: textSecondary,
        elevation: 8,
        type: BottomNavigationBarType.fixed,
        selectedLabelStyle: TextStyle(fontWeight: FontWeight.w700, fontSize: 11),
        unselectedLabelStyle: TextStyle(fontWeight: FontWeight.w500, fontSize: 11),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryBlue,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
        ),
      ),
    );
  }
}
