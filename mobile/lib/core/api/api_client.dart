// Client HTTP unique pour parler au backend FastAPI Nasoma.
// Compatible Flutter Web (utilise dio).

import 'package:dio/dio.dart';
import 'package:dio_smart_retry/dio_smart_retry.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../env/env.dart';

final apiClientProvider = Provider<Dio>((ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: '${Env.apiBaseUrl}/api/v1',
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {
        'Accept': 'application/json',
        'X-App-Version': '0.1.0',
      },
    ),
  );

  dio.interceptors.add(
    RetryInterceptor(
      dio: dio,
      retries: 2,
      retryDelays: const [
        Duration(seconds: 1),
        Duration(seconds: 3),
      ],
    ),
  );

  // Log requests en dev
  if (Env.isDev) {
    dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (obj) {
          // ignore: avoid_print
          print('[API] $obj');
        },
      ),
    );
  }

  return dio;
});
