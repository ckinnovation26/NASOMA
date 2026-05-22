import 'package:dio/dio.dart';

abstract class AuthRepository {
  Future<Map<String, dynamic>> sendOtp(String phoneNumber);
  Future<Map<String, dynamic>> verifyOtp(String phoneNumber, String otp);
  Future<void> logout();
}

class AuthRepositoryImpl implements AuthRepository {
  final Dio _dio;
  static const String _baseUrl = '/api/v1/auth';

  AuthRepositoryImpl({required Dio dio}) : _dio = dio;

  @override
  Future<Map<String, dynamic>> sendOtp(String phoneNumber) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/send-otp',
        data: {'phone_number': phoneNumber},
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<Map<String, dynamic>> verifyOtp(String phoneNumber, String otp) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/verify-otp',
        data: {
          'phone_number': phoneNumber,
          'otp': otp,
        },
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<void> logout() async {
    try {
      await _dio.post('$_baseUrl/logout');
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  String _handleDioError(DioException error) {
    if (error.response != null) {
      final message = error.response!.data['detail'] ?? 'Erreur serveur';
      return message;
    }
    return error.message ?? 'Erreur réseau';
  }
}
