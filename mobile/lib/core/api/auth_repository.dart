// Repository auth — appels backend signup/login.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../env/env.dart';
import 'api_client.dart';

class SelfSignupResult {
  SelfSignupResult({
    required this.accepted,
    this.userId,
    this.requiresWhatsappInstall = false,
    this.guidanceText,
    this.nearbyVendors = const [],
    this.freeTrialScans,
    this.whatsappDeliveryStatus,
  });

  final bool accepted;
  final String? userId;
  final bool requiresWhatsappInstall;
  final String? guidanceText;
  final List<Map<String, dynamic>> nearbyVendors;
  final int? freeTrialScans;
  final String? whatsappDeliveryStatus;
}

class AuthRepository {
  AuthRepository(this._dio);

  final Dio _dio;

  Future<SelfSignupResult> selfSignup({
    required String phone,
    required String fullName,
    required bool hasWhatsapp,
    String? gradeLevel,
    String? homeCity,
    String? homeIsland,
    double? userLatitude,
    double? userLongitude,
  }) async {
    if (Env.useMockApi) {
      await Future<void>.delayed(const Duration(milliseconds: 700));
      if (!hasWhatsapp) {
        return SelfSignupResult(
          accepted: false,
          requiresWhatsappInstall: true,
          guidanceText: 'WhatsApp est requis pour recevoir ton code Nasoma.',
        );
      }
      return SelfSignupResult(
        accepted: true,
        userId: 'mock-user-${DateTime.now().millisecondsSinceEpoch}',
        freeTrialScans: 3,
        whatsappDeliveryStatus: 'sent',
      );
    }

    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/signup/self',
      data: {
        'phone': phone,
        'full_name': fullName,
        'has_whatsapp': hasWhatsapp,
        if (gradeLevel != null) 'grade_level': gradeLevel,
        if (homeCity != null) 'home_city': homeCity,
        if (homeIsland != null) 'home_island': homeIsland,
        if (userLatitude != null) 'user_latitude': userLatitude,
        if (userLongitude != null) 'user_longitude': userLongitude,
        'consent_data_processing': true,
      },
    );

    final body = response.data ?? {};
    final accepted = body['accepted'] as bool? ?? false;

    if (!accepted) {
      return SelfSignupResult(
        accepted: false,
        requiresWhatsappInstall: body['requires_whatsapp_install'] as bool? ?? false,
        guidanceText: body['guidance_text'] as String?,
        nearbyVendors:
            (body['nearby_vendors'] as List?)?.cast<Map<String, dynamic>>() ?? const [],
      );
    }

    return SelfSignupResult(
      accepted: true,
      userId: body['user_id'] as String?,
      freeTrialScans: body['free_trial_scans'] as int?,
      whatsappDeliveryStatus: body['whatsapp_delivery_status'] as String?,
    );
  }

  Future<Map<String, dynamic>> verifyOtp({
    required String phone,
    required String code,
  }) async {
    if (Env.useMockApi) {
      await Future<void>.delayed(const Duration(milliseconds: 500));
      if (code != Env.mockOtpCode) {
        throw DioException(
          requestOptions: RequestOptions(path: '/auth/signup/verify'),
          message: 'Code incorrect (mock : utilise ${Env.mockOtpCode})',
          type: DioExceptionType.badResponse,
        );
      }
      return {
        'access_token': 'mock-jwt-token',
        'user_id': 'mock-user-id',
        'free_trial_scans_remaining': 3,
        'account_state': 'ACTIVE',
      };
    }

    final response = await _dio.post<Map<String, dynamic>>(
      '/auth/signup/verify',
      data: {'phone': phone, 'code': code},
    );
    return response.data ?? {};
  }
}

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(ref.watch(apiClientProvider)),
);
