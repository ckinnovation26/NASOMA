// Onboarding — 3 slides présentation produit.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final PageController _controller = PageController();
  int _index = 0;

  final _slides = const [
    _OnboardingSlide(
      emoji: '📷',
      title: 'Scanne ta copie',
      body: 'Prends en photo ta dernière dictée ou ton exercice de maths. Une seule photo, et c\'est parti.',
    ),
    _OnboardingSlide(
      emoji: '🔍',
      title: 'L\'IA repère tes erreurs',
      body: 'Mimi analyse ta copie en quelques secondes et te montre exactement où tu te trompes.',
    ),
    _OnboardingSlide(
      emoji: '🎯',
      title: 'Comble ta lacune',
      body: 'Fais 3 mini-exercices ciblés. Demain, tu es prêt. Le rattrapage avant qu\'il soit trop tard.',
    ),
  ];

  void _next() {
    // Source de vérité = position réelle du PageController, pas _index
    // (sur iOS Safari, le swipe peut désynchroniser onPageChanged)
    final current = _controller.hasClients
        ? (_controller.page?.round() ?? _index)
        : _index;

    if (current < _slides.length - 1) {
      _controller.nextPage(
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    } else {
      context.go('/whatsapp-check');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.black,
      body: SafeArea(
        child: Column(
          children: [
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: () => context.go('/whatsapp-check'),
                child: const Text(
                  'Passer',
                  style: TextStyle(color: AppColors.textTertiary),
                ),
              ),
            ),
            Expanded(
              child: PageView(
                controller: _controller,
                // Swipe désactivé : navigation uniquement par le bouton, pour
                // éviter les désynchros de _index sur iOS Safari et garantir
                // que l'utilisateur passe par le CTA principal.
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (i) => setState(() => _index = i),
                children: _slides,
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  _Dots(count: _slides.length, current: _index),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _next,
                      child: Text(
                        _index < _slides.length - 1 ? 'Suivant →' : 'Commencer →',
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _OnboardingSlide extends StatelessWidget {
  const _OnboardingSlide({required this.emoji, required this.title, required this.body});

  final String emoji;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Illustration limitée à 240 px max pour éviter overflow sur petits viewports
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 240, maxHeight: 240),
            child: AspectRatio(
              aspectRatio: 1,
              child: Container(
                decoration: BoxDecoration(
                  color: AppColors.charcoal,
                  borderRadius: BorderRadius.circular(28),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                child: Center(
                  child: Text(emoji, style: const TextStyle(fontSize: 88)),
                ),
              ),
            ),
          ),
          const SizedBox(height: 28),
          Text(
            title,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            body,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _Dots extends StatelessWidget {
  const _Dots({required this.count, required this.current});
  final int count;
  final int current;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(count, (i) {
        final active = i == current;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          margin: const EdgeInsets.symmetric(horizontal: 4),
          width: active ? 24 : 8,
          height: 8,
          decoration: BoxDecoration(
            color: active ? AppColors.limeAccent : AppColors.borderSubtle,
            borderRadius: BorderRadius.circular(4),
          ),
        );
      }),
    );
  }
}
