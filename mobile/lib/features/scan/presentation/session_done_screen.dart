// Fin de session — recap du score + CTA retour home.

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class SessionDoneScreen extends StatelessWidget {
  const SessionDoneScreen({super.key, required this.score, this.total = 3});

  final int score;
  final int total;

  @override
  Widget build(BuildContext context) {
    final perfect = score == total;
    final emoji = perfect ? '🎉' : (score >= 2 ? '👏' : '💪');
    final title = perfect
        ? 'Sans faute !'
        : (score >= 2 ? 'Très bien joué' : 'Bon effort');
    final sub = perfect
        ? 'Tu as compris l\'addition avec retenue.'
        : (score >= 2
            ? 'Tu progresses — la retenue est presque acquise.'
            : 'Refais la session demain pour ancrer la méthode.');

    return Scaffold(
      backgroundColor: AppColors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 32),
              Text(emoji, style: const TextStyle(fontSize: 88))
                  .animate()
                  .scale(duration: 500.ms, curve: Curves.elasticOut),
              const SizedBox(height: 16),
              Text(
                title,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                sub,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 32),

              // Score
              Container(
                padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 28),
                decoration: BoxDecoration(
                  color: AppColors.charcoal,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                child: Column(
                  children: [
                    Text(
                      '$score / $total',
                      style: const TextStyle(
                        color: AppColors.limeAccent,
                        fontSize: 48,
                        fontWeight: FontWeight.w800,
                        height: 1,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'bonnes réponses',
                      style: TextStyle(
                        color: AppColors.textTertiary,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Indicateur CT/MT/LT — placeholder
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.charcoal,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'PROCHAINE RÉVISION',
                      style: TextStyle(
                        color: AppColors.textTertiary,
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.6,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Row(
                      children: [
                        Icon(
                          Icons.calendar_today_outlined,
                          color: AppColors.limeAccent,
                          size: 18,
                        ),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Demain, Mimi te repropose 2 exercices similaires pour ancrer.',
                            style: TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 13,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const Spacer(),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => context.go('/home'),
                  child: const Text('Retour à l\'accueil'),
                ),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () => context.go('/scan'),
                child: const Text(
                  'Scanner une autre copie',
                  style: TextStyle(color: AppColors.textSecondary),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
