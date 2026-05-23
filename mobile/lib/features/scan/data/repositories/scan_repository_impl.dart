import 'package:dio/dio.dart';

import '../../../../core/env/env.dart';
import '../../domain/models/scan_model.dart';

abstract class ScanRepository {
  Future<Map<String, dynamic>> uploadScan(ScanModel scan);
  Future<Map<String, dynamic>> pollScanResult(String scanId);
}

class ScanRepositoryImpl implements ScanRepository {
  final Dio _dio;
  static const String _baseUrl = '/api/v1/scans';

  ScanRepositoryImpl({required Dio dio}) : _dio = dio;

  @override
  Future<Map<String, dynamic>> uploadScan(ScanModel scan) async {
    if (Env.useMockApi) {
      await Future<void>.delayed(const Duration(milliseconds: 800));
      return {
        'scan_id': 'mock-scan-${DateTime.now().millisecondsSinceEpoch}',
        'session_id': scan.sessionId,
        'status': 'processing',
      };
    }
    try {
      final response = await _dio.post(
        '$_baseUrl/upload',
        data: {
          'session_id': scan.sessionId,
          'base64_image': scan.base64Image,
        },
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<Map<String, dynamic>> pollScanResult(String scanId) async {
    if (Env.useMockApi) {
      await Future<void>.delayed(const Duration(milliseconds: 600));
      return {
        'scan_id': scanId,
        'status': 'done',
        'detection_type': 'success',
        'diagnostic_id': 'mock-diagnostic-001',
        'session_id': 'mock-session-001',
        'ocr_confidence': 0.92,
        'quota_remaining_after': 2,
        'summary_text': 'Difficulté détectée : addition avec retenue.',
      };
    }
    try {
      final response = await _dio.get('$_baseUrl/$scanId/result');
      return response.data as Map<String, dynamic>;
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
