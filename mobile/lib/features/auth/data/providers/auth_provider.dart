import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/api/auth_repository.dart';
import '../../../../core/api/token_storage.dart';

enum AuthState {
  idle,
  loading,
  sendingOtp,
  verifyingOtp,
  authenticated,
  error,
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._repo, this._storage) : super(AuthState.idle) {
    _restoreSession();
  }

  final AuthRepository _repo;
  final TokenStorage _storage;

  String? _phoneNumber;
  String? _userId;
  String? _jwtToken;
  String? _errorMessage;

  String? get phoneNumber => _phoneNumber;
  String? get userId => _userId;
  String? get jwtToken => _jwtToken;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => state == AuthState.authenticated;

  void _restoreSession() {
    if (_storage.hasToken) {
      _jwtToken = _storage.accessToken;
      _userId = _storage.userId;
      state = AuthState.authenticated;
    }
  }

  Future<void> startOtpFlow(String phone) async {
    _phoneNumber = phone;
    _errorMessage = null;
    state = AuthState.sendingOtp;

    try {
      final result = await _repo.selfSignup(
        phone: phone,
        fullName: '',
        hasWhatsapp: true,
      );
      if (!result.accepted) {
        _errorMessage = result.guidanceText ?? 'Inscription non acceptée.';
        state = AuthState.error;
      } else {
        state = AuthState.idle;
      }
    } catch (e) {
      _errorMessage = e.toString();
      state = AuthState.error;
    }
  }

  Future<void> verifyOtp(String otp) async {
    if (_phoneNumber == null) {
      _errorMessage = 'Numéro de téléphone manquant.';
      state = AuthState.error;
      return;
    }
    _errorMessage = null;
    state = AuthState.verifyingOtp;

    try {
      final result = await _repo.verifyOtp(phone: _phoneNumber!, code: otp);
      final token = result['access_token'] as String? ?? result['token']?['access_token'] as String?;
      final userId = result['user']?['id'] as String? ?? result['user_id'] as String?;

      if (token == null || token.isEmpty) {
        throw Exception('Token absent dans la réponse serveur.');
      }

      _jwtToken = token;
      _userId = userId;
      await _storage.save(token: token, userId: userId ?? '');
      state = AuthState.authenticated;
    } catch (e) {
      _errorMessage = e.toString();
      state = AuthState.error;
    }
  }

  void setAuthenticated(String userId, String token) {
    _userId = userId;
    _jwtToken = token;
    state = AuthState.authenticated;
  }

  void setError(String message) {
    _errorMessage = message;
    state = AuthState.error;
  }

  Future<void> logout() async {
    await _storage.clear();
    _phoneNumber = null;
    _userId = null;
    _jwtToken = null;
    _errorMessage = null;
    state = AuthState.idle;
  }

  void reset() {
    _errorMessage = null;
    state = AuthState.idle;
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.read(authRepositoryProvider),
    ref.read(tokenStorageProvider),
  );
});
