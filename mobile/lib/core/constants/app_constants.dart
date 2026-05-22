// Constantes globales — JAMAIS de strings UI ici (utiliser i18n).

class AppConstants {
  AppConstants._();

  // ─── App ───
  static const String appName = 'Nasoma';
  static const String slogan = 'Mimi, Nasoma.';
  static const String version = '0.1.0';

  // ─── Quotas (verrouillés business) ───
  static const int freeTrialScans = 3;          // découverte
  static const int freeTrialTtlDays = 7;        // expiration découverte
  static const int gracePeriodDays = 30;        // lecture seule après expiration
  static const int maxFamilyProfiles = 4;
  static const int maxUploadSizeKb = 200;

  // ─── Image processing ───
  static const int captureMaxDimension = 1024;
  static const int captureJpegQuality = 75;

  // ─── Timeouts ───
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration ocrTimeout = Duration(seconds: 15);

  // ─── Cache ───
  static const Duration scanCacheTtl = Duration(hours: 24);
}
