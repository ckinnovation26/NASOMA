import 'package:flutter_riverpod/flutter_riverpod.dart';

enum AuthState {
  idle,
  loading,
  sendingOtp,
  verifyingOtp,
  authenticated,
  error,
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState.idle);

  String? _phoneNumber;
  String? _userId;
  String? _jwtToken;
  String? _errorMessage;

  String? get phoneNumber => _phoneNumber;
  String? get userId => _userId;
  String? get jwtToken => _jwtToken;
  String? get errorMessage => _errorMessage;

  bool get isAuthenticated => state == AuthState.authenticated;

  Future<void> startOtpFlow(String phoneNumber) async {
    _phoneNumber = phoneNumber;
    state = AuthState.sendingOtp;
    _errorMessage = null;
    // appel à repository se fera via un autre provider (voir M5)
  }

  Future<void> verifyOtp(String otp) async {
    state = AuthState.verifyingOtp;
    _errorMessage = null;
    // appel à repository se fera via un autre provider (voir M5)
  }

  void setAuthenticated(String userId, String jwtToken) {
    _userId = userId;
    _jwtToken = jwtToken;
    state = AuthState.authenticated;
  }

  void setError(String message) {
    _errorMessage = message;
    state = AuthState.error;
  }

  void logout() {
    _phoneNumber = null;
    _userId = null;
    _jwtToken = null;
    _errorMessage = null;
    state = AuthState.idle;
  }

  void reset() {
    state = AuthState.idle;
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
