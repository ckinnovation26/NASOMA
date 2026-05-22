// Résultat du scan — montre la lacune détectée + CTA pour démarrer la session.

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class ScanResultScreen extends StatelessWidget {
  const ScanResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/home'),
        ),
        title: const Text(
          'Diagnostic',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Bandeau confiance
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: AppColors.limeAccent.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.limeAccent.withOpacity(0.4)),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.bolt, color: AppColors.limeAccent, size: 16),
                    SizedBox(width: 6),
                    Text(
                      'Diagnostic en 4,5 sec — confiance 87 %',
                      style: TextStyle(
                        color: AppColors.limeAccent,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              Text(
                'Ce que Mimi a vu',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: AppColors.textTertiary,
                      letterSpacing: 0.6,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 8),

              // "Aperçu" de la copie scannée (placeholder graphique)
              Container(
                height: 180,
                decoration: BoxDecoration(
                  color: AppColors.charcoal,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                child: const Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Exercice 4 — Calcule.',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                      SizedBox(height: 14),
                      _CalcLine('27 + 15 = ', '32', isWrong: true),
                      SizedBox(height: 6),
                      _CalcLine('38 + 24 = ', '52', isWrong: true),
                      SizedBox(height: 6),
                      _CalcLine('45 + 32 = ', '77', isWrong: false),
                      SizedBox(height: 6),
                      _CalcLine('56 + 18 = ', '64', isWrong: true),
                    ],
                  ),
                ),
              ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.05),
              const SizedBox(height: 24),

              Text(
                'LACUNE DÉTECTÉE',
                style: TextStyle(
                  color: AppColors.textTertiary,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.6,
                ),
              ),
              const SizedBox(height: 10),

              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.charcoal,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: AppColors.warning.withOpacity(0.5),
                  ),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppColors.warning.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Center(
                        child: Text('📐', style: TextStyle(fontSize: 24)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Addition avec retenue',
                            style: TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Maths · CM2 · 3 erreurs sur 4',
                            style: TextStyle(
                              color: AppColors.textSecondary,
                              fontSize: 13,
                            ),
                          ),
                          SizedBox(height: 12),
                          Text(
                            'Tu oublies la retenue quand le résultat des unités dépasse 9.',
                            style: TextStyle(
                              color: AppColors.textSecondary,
                              fontSize: 13,
                              height: 1.4,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ).animate(delay: 200.ms).fadeIn(duration: 400.ms).slideY(begin: 0.05),
              const SizedBox(height: 24),

              // CTA principal
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => context.go('/scan/session'),
                  child: const Text('Faire mes 3 exercices ciblés →'),
                ),
              ),
              const SizedBox(height: 12),
              Center(
                child: TextButton(
                  onPressed: () => context.go('/home'),
                  child: const Text(
                    'Plus tard',
                    style: TextStyle(color: AppColors.textTertiary),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CalcLine extends StatelessWidget {
  const _CalcLine(this.calc, this.answer, {required this.isWrong});
  final String calc;
  final String answer;
  final bool isWrong;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          calc,
          style: const TextStyle(
            color: AppColors.textPrimary,
            fontSize: 15,
            fontFamily: 'monospace',
            fontWeight: FontWeight.w500,
          ),
        ),
        Text(
          answer,
          style: TextStyle(
            color: isWrong ? AppColors.error : AppColors.success,
            fontSize: 15,
            fontFamily: 'monospace',
            fontWeight: FontWeight.w700,
            decoration: isWrong ? TextDecoration.lineThrough : TextDecoration.none,
          ),
        ),
        const SizedBox(width: 8),
        Icon(
          isWrong ? Icons.close : Icons.check,
          color: isWrong ? AppColors.error : AppColors.success,
          size: 18,
        ),
      ],
    );
  }
}
