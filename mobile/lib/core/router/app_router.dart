import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/data/providers/auth_provider.dart';
import '../../features/auth/presentation/otp_screen.dart';
import '../../features/auth/presentation/phone_screen.dart';
import '../../features/auth/presentation/signup_form_screen.dart';
import '../../features/auth/presentation/whatsapp_check_screen.dart';
import '../../features/auth/presentation/whatsapp_guidance_screen.dart';
import '../../features/home/presentation/home_screen.dart';
import '../../features/onboarding/presentation/onboarding_screen.dart';
import '../../features/scan/presentation/diagnostic_screen.dart';
import '../../features/scan/presentation/scan_result_screen.dart';
import '../../features/scan/presentation/scan_screen.dart';
import '../../features/scan/presentation/session_done_screen.dart';
import '../../features/scan/presentation/session_screen.dart';
import '../../features/splash/presentation/splash_screen.dart';

// Routes qui nécessitent d'être authentifié
const _protectedRoutes = {'/home', '/scan', '/scan/diagnostic', '/scan/result', '/scan/session', '/scan/done'};

final appRouterProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    initialLocation: '/',
    debugLogDiagnostics: true,
    redirect: (context, state) {
      final authState = ref.read(authProvider);
      final isAuthenticated = authState == AuthState.authenticated;
      final path = state.uri.path;

      final isProtected = _protectedRoutes.any((r) => path == r || path.startsWith('$r/'));

      if (isProtected && !isAuthenticated) {
        return '/phone';
      }
      // Éviter de renvoyer un utilisateur authentifié vers phone/otp
      if (isAuthenticated && (path == '/phone' || path == '/otp')) {
        return '/home';
      }
      return null;
    },
    refreshListenable: _AuthStateNotifier(ref),
    routes: [
      GoRoute(
        path: '/',
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/whatsapp-check',
        name: 'whatsapp-check',
        builder: (context, state) => const WhatsAppCheckScreen(),
      ),
      GoRoute(
        path: '/whatsapp-guidance',
        name: 'whatsapp-guidance',
        builder: (context, state) {
          final vendors = state.extra as List<Map<String, dynamic>>? ?? const [];
          return WhatsAppGuidanceScreen(nearbyVendors: vendors);
        },
      ),
      GoRoute(
        path: '/signup',
        name: 'signup',
        builder: (context, state) => const SignupFormScreen(),
      ),
      GoRoute(
        path: '/phone',
        name: 'phone',
        builder: (context, state) => const PhoneScreen(),
      ),
      GoRoute(
        path: '/otp',
        name: 'otp',
        builder: (context, state) {
          final phone = state.uri.queryParameters['phone'] ?? '';
          return OtpScreen(phone: phone);
        },
      ),
      GoRoute(
        path: '/home',
        name: 'home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/scan',
        name: 'scan',
        builder: (context, state) => const ScanScreen(),
      ),
      GoRoute(
        path: '/scan/diagnostic',
        name: 'scan-diagnostic',
        builder: (context, state) => const DiagnosticScreen(),
      ),
      GoRoute(
        path: '/scan/result',
        name: 'scan-result',
        builder: (context, state) => const ScanResultScreen(),
      ),
      GoRoute(
        path: '/scan/session',
        name: 'scan-session',
        builder: (context, state) => const SessionScreen(),
      ),
      GoRoute(
        path: '/scan/done',
        name: 'scan-done',
        builder: (context, state) {
          final score = (state.extra as int?) ?? 3;
          return SessionDoneScreen(score: score);
        },
      ),
    ],
  );
  return router;
});

/// Notifier qui écoute authProvider et notifie GoRouter de re-évaluer les redirects.
class _AuthStateNotifier extends ChangeNotifier {
  _AuthStateNotifier(Ref ref) {
    ref.listen<AuthState>(authProvider, (_, __) => notifyListeners());
  }
}
