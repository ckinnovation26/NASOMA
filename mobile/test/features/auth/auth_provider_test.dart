import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nasoma/features/auth/data/providers/auth_provider.dart';

void main() {
  group('AuthProvider', () {
    late ProviderContainer container;

    setUp(() {
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    test('initial state is idle', () {
      final state = container.read(authProvider);
      expect(state, AuthState.idle);
    });

    test('startOtpFlow sets state to sendingOtp', () async {
      const phoneNumber = '+269XXXXXX';
      final notifier = container.read(authProvider.notifier);

      await notifier.startOtpFlow(phoneNumber);
      final state = container.read(authProvider);

      expect(state, AuthState.sendingOtp);
      expect(notifier.phoneNumber, phoneNumber);
    });

    test('setAuthenticated sets state to authenticated', () {
      const userId = 'user123';
      const jwtToken = 'token123';
      final notifier = container.read(authProvider.notifier);

      notifier.setAuthenticated(userId, jwtToken);
      final state = container.read(authProvider);

      expect(state, AuthState.authenticated);
      expect(notifier.isAuthenticated, true);
      expect(notifier.userId, userId);
      expect(notifier.jwtToken, jwtToken);
    });

    test('setError sets state to error', () {
      const errorMessage = 'Erreur authentification';
      final notifier = container.read(authProvider.notifier);

      notifier.setError(errorMessage);
      final state = container.read(authProvider);

      expect(state, AuthState.error);
      expect(notifier.errorMessage, errorMessage);
    });

    test('logout resets all state', () {
      const userId = 'user123';
      const jwtToken = 'token123';
      final notifier = container.read(authProvider.notifier);

      notifier.setAuthenticated(userId, jwtToken);
      notifier.logout();

      expect(notifier.userId, null);
      expect(notifier.jwtToken, null);
      expect(notifier.phoneNumber, null);
      expect(notifier.isAuthenticated, false);
    });
  });
}
