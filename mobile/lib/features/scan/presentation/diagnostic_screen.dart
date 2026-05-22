// Diagnostic IA — anime les 3 étages OCR/Vision/Gemini puis route vers le résultat.

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class DiagnosticScreen extends StatefulWidget {
  const DiagnosticScreen({super.key});

  @override
  State<DiagnosticScreen> createState() => _DiagnosticScreenState();
}

class _DiagnosticScreenState extends State<DiagnosticScreen> {
  static const _steps = [
    _Step(
      emoji: '📱',
      title: 'ML Kit OCR',
      sub: 'Lecture sur ton téléphone — gratuit, instant',
      durationMs: 1300,
    ),
    _Step(
      emoji: '☁️',
      title: 'Cloud Vision',
      sub: 'Renfort serveur pour les caractères difficiles',
      durationMs: 1500,
    ),
    _Step(
      emoji: '🤖',
      title: 'Gemini Flash',
      sub: 'Diagnostic du concept en lacune',
      durationMs: 1700,
    ),
  ];

  int _currentStep = 0;
  bool _done = false;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _scheduleNext();
  }

  void _scheduleNext() {
    if (_currentStep >= _steps.length) {
      setState(() => _done = true);
      Timer(const Duration(milliseconds: 700), () {
        if (mounted) context.go('/scan/result');
      });
      return;
    }
    _timer = Timer(
      Duration(milliseconds: _steps[_currentStep].durationMs),
      () {
        if (!mounted) return;
        setState(() => _currentStep++);
        _scheduleNext();
      },
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 12),
              Text(
                'Mimi analyse ta copie…',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Trois étages d\'IA, du moins cher au plus puissant.',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 32),

              for (var i = 0; i < _steps.length; i++) ...[
                _StepRow(
                  step: _steps[i],
                  state: i < _currentStep
                      ? _StepState.done
                      : (i == _currentStep ? _StepState.active : _StepState.pending),
                ),
                if (i < _steps.length - 1) const SizedBox(height: 14),
              ],

              const Spacer(),

              if (_done)
                Center(
                  child: Column(
                    children: [
                      const Icon(
                        Icons.check_circle,
                        color: AppColors.limeAccent,
                        size: 54,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Diagnostic terminé',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ],
                  ).animate().fadeIn(duration: 400.ms).scale(),
                ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

enum _StepState { pending, active, done }

class _Step {
  const _Step({
    required this.emoji,
    required this.title,
    required this.sub,
    required this.durationMs,
  });
  final String emoji;
  final String title;
  final String sub;
  final int durationMs;
}

class _StepRow extends StatelessWidget {
  const _StepRow({required this.step, required this.state});
  final _Step step;
  final _StepState state;

  @override
  Widget build(BuildContext context) {
    Color border;
    Widget trailing;
    switch (state) {
      case _StepState.pending:
        border = AppColors.borderSubtle;
        trailing = const Icon(
          Icons.circle_outlined,
          color: AppColors.textTertiary,
          size: 22,
        );
        break;
      case _StepState.active:
        border = AppColors.limeAccent;
        trailing = const SizedBox(
          width: 22,
          height: 22,
          child: CircularProgressIndicator(
            strokeWidth: 2.5,
            color: AppColors.limeAccent,
          ),
        );
        break;
      case _StepState.done:
        border = AppColors.limeAccent.withOpacity(0.4);
        trailing = const Icon(
          Icons.check_circle,
          color: AppColors.limeAccent,
          size: 22,
        );
        break;
    }

    final dim = state == _StepState.pending;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.charcoal,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: border),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AppColors.black,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Center(
              child: Text(step.emoji, style: const TextStyle(fontSize: 22)),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  step.title,
                  style: TextStyle(
                    color: dim ? AppColors.textTertiary : AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  step.sub,
                  style: TextStyle(
                    color: dim ? AppColors.textTertiary : AppColors.textSecondary,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          trailing,
        ],
      ),
    );
  }
}
