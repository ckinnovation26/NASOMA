// Thème Nasoma — dark mode par défaut, vert lime accent.

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppColors {
  AppColors._();

  static const Color black = Color(0xFF000000);
  static const Color charcoal = Color(0xFF1A1A1A);
  static const Color limeAccent = Color(0xFFD4FF80);
  static const Color white = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFFF5F5F5);
  static const Color textSecondary = Color(0xFFB0B0B0);
  static const Color textTertiary = Color(0xFF6B6B6B);
  static const Color borderSubtle = Color(0xFF2A2A2A);

  static const Color success = Color(0xFFD4FF80);
  static const Color warning = Color(0xFFFFB84A);
  static const Color error = Color(0xFFFF6B6B);
}

class AppTheme {
  AppTheme._();

  static ThemeData get dark {
    final base = ThemeData.dark(useMaterial3: true);
    final textTheme = GoogleFonts.interTextTheme(base.textTheme).apply(
      bodyColor: AppColors.textPrimary,
      displayColor: AppColors.textPrimary,
    );

    return base.copyWith(
      scaffoldBackgroundColor: AppColors.black,
      colorScheme: const ColorScheme.dark(
        surface: AppColors.black,
        primary: AppColors.limeAccent,
        onPrimary: AppColors.black,
        secondary: AppColors.charcoal,
        onSecondary: AppColors.textPrimary,
        error: AppColors.error,
      ),
      textTheme: textTheme,
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.black,
        elevation: 0,
        centerTitle: true,
        iconTheme: IconThemeData(color: AppColors.textPrimary),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.limeAccent,
          foregroundColor: AppColors.black,
          minimumSize: const Size(double.infinity, 56),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.charcoal,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        hintStyle: textTheme.bodyMedium?.copyWith(
          color: AppColors.textTertiary,
        ),
      ),
    );
  }
}
