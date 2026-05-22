import 'package:dio/dio.dart';
import '../../domain/models/session_model.dart';
import '../../domain/models/exercise_model.dart';

abstract class SessionRepository {
  Future<SessionModel> createSession(String diagnosticId);
  Future<List<ExerciseModel>> fetchExercises(String sessionId);
  Future<Map<String, dynamic>> submitAnswer(
    String sessionId,
    String exerciseId,
    String answer,
  );
  Future<SessionModel> completeSession(String sessionId);
}

class SessionRepositoryImpl implements SessionRepository {
  final Dio _dio;
  static const String _baseUrl = '/api/v1/sessions';

  SessionRepositoryImpl({required Dio dio}) : _dio = dio;

  @override
  Future<SessionModel> createSession(String diagnosticId) async {
    try {
      final response = await _dio.post(
        _baseUrl,
        data: {'diagnostic_id': diagnosticId},
      );
      return SessionModel.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<List<ExerciseModel>> fetchExercises(String sessionId) async {
    try {
      final response = await _dio.get('$_baseUrl/$sessionId/exercises');
      final list = response.data as List<dynamic>;
      return list
          .map((e) => ExerciseModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<Map<String, dynamic>> submitAnswer(
    String sessionId,
    String exerciseId,
    String answer,
  ) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/$sessionId/exercises/$exerciseId/answer',
        data: {'answer': answer},
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<SessionModel> completeSession(String sessionId) async {
    try {
      final response = await _dio.post('$_baseUrl/$sessionId/complete');
      return SessionModel.fromJson(response.data as Map<String, dynamic>);
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
