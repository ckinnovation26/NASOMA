import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../scan/data/providers/scan_provider.dart';
import '../../session/data/models/exercise_model.dart';
import '../../session/data/providers/session_provider.dart';

class SessionScreen extends ConsumerStatefulWidget {
  const SessionScreen({super.key});

  @override
  ConsumerState<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends ConsumerState<SessionScreen> {
  String? _sessionId;
  String? _selectedAnswer;
  bool _answered = false;
  bool? _lastAnswerCorrect;
  final _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _initSession());
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _initSession() async {
    final scan = ref.read(scanProvider.notifier).currentScan;
    _sessionId = scan?.sessionId;

    if (_sessionId == null || _sessionId!.isEmpty) {
      ref.read(sessionProvider.notifier).setError('Session introuvable.');
      return;
    }
    await ref.read(sessionProvider.notifier).loadSession(_sessionId!);
  }

  Future<void> _submitAnswer() async {
    final ex = ref.read(sessionProvider.notifier).currentExercise;
    if (ex == null || _sessionId == null) return;

    final answer = ex.type == 'mcq' ? (_selectedAnswer ?? '') : _textController.text.trim();
    if (answer.isEmpty) return;

    final isCorrect = await ref.read(sessionProvider.notifier).submitAnswer(_sessionId!, answer);
    setState(() {
      _answered = true;
      _lastAnswerCorrect = isCorrect;
    });
  }

  Future<void> _next() async {
    if (_sessionId == null) return;

    final notifier = ref.read(sessionProvider.notifier);
    final isLast = notifier.currentExerciseIndex >= notifier.totalExercises - 1;

    await notifier.moveToNext(_sessionId!);

    if (isLast) return; // moveToNext gère la transition completed

    setState(() {
      _answered = false;
      _lastAnswerCorrect = null;
      _selectedAnswer = null;
      _textController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final sessionState = ref.watch(sessionProvider);
    final notifier = ref.read(sessionProvider.notifier);

    ref.listen<SessionState>(sessionProvider, (_, next) {
      if (next == SessionState.completed && mounted) {
        context.go('/scan/done', extra: notifier.correctCount);
      }
    });

    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: AppColors.textSecondary),
          onPressed: () {
            ref.read(sessionProvider.notifier).reset();
            context.go('/home');
          },
        ),
        title: sessionState == SessionState.active
            ? Text(
                'Exercice ${notifier.currentExerciseIndex + 1} / ${notifier.totalExercises}',
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
              )
            : null,
      ),
      body: SafeArea(
        child: switch (sessionState) {
          SessionState.idle || SessionState.loading => const _LoadingView(),
          SessionState.error => _ErrorView(
              message: notifier.errorMessage ?? 'Erreur inconnue',
              onRetry: _initSession,
            ),
          SessionState.active || SessionState.submitting => _ExerciseView(
              exercise: notifier.currentExercise!,
              totalExercises: notifier.totalExercises,
              currentIndex: notifier.currentExerciseIndex,
              selectedAnswer: _selectedAnswer,
              textController: _textController,
              answered: _answered,
              isCorrect: _lastAnswerCorrect,
              onSelectMcq: (answer) {
                if (!_answered) setState(() => _selectedAnswer = answer);
              },
              onSubmit: _answered ? _next : _submitAnswer,
              isSubmitting: sessionState == SessionState.submitting,
            ),
          SessionState.completed => const _LoadingView(),
        },
      ),
    );
  }
}

// ══════════════════════════════════════════════
//  Vue exercice
// ══════════════════════════════════════════════

class _ExerciseView extends StatelessWidget {
  const _ExerciseView({
    required this.exercise,
    required this.totalExercises,
    required this.currentIndex,
    required this.selectedAnswer,
    required this.textController,
    required this.answered,
    required this.isCorrect,
    required this.onSelectMcq,
    required this.onSubmit,
    required this.isSubmitting,
  });

  final ExerciseModel exercise;
  final int totalExercises;
  final int currentIndex;
  final String? selectedAnswer;
  final TextEditingController textController;
  final bool answered;
  final bool? isCorrect;
  final ValueChanged<String> onSelectMcq;
  final VoidCallback onSubmit;
  final bool isSubmitting;

  @override
  Widget build(BuildContext context) {
    final isLast = currentIndex >= totalExercises - 1;

    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Barre de progression
          ClipRRect(
            borderRadius: BorderRadius.circular(3),
            child: LinearProgressIndicator(
              value: (currentIndex + (answered ? 1 : 0)) / totalExercises,
              backgroundColor: AppColors.charcoal,
              valueColor: const AlwaysStoppedAnimation(AppColors.limeAccent),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 28),

          // Label concept
          Text(
            exercise.conceptCode.replaceAll('_', ' '),
            style: TextStyle(
              color: AppColors.textTertiary,
              fontSize: 11,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 10),

          // Question
          Text(
            exercise.question,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  height: 1.35,
                ),
          ),
          const SizedBox(height: 28),

          // Zone de réponse selon le type
          if (exercise.type == 'mcq' && exercise.options != null)
            _McqChoices(
              options: exercise.options!,
              correctAnswer: exercise.correctAnswer,
              selectedAnswer: selectedAnswer,
              answered: answered,
              onSelect: onSelectMcq,
            )
          else
            _TextInput(
              controller: textController,
              answered: answered,
              isFillBlank: exercise.type == 'fill_blank',
            ),

          const Spacer(),

          // Feedback après réponse
          if (answered && isCorrect != null) ...[
            _FeedbackBanner(
              isCorrect: isCorrect!,
              explanation: exercise.correctAnswer,
            ).animate().fadeIn(duration: 250.ms).slideY(begin: 0.1),
            const SizedBox(height: 14),
          ],

          // Bouton soumettre / suivant
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: isSubmitting ? null : onSubmit,
              child: isSubmitting
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: AppColors.black,
                      ),
                    )
                  : Text(
                      answered
                          ? (isLast ? 'Voir mes résultats →' : 'Exercice suivant →')
                          : 'Vérifier ma réponse',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

class _McqChoices extends StatelessWidget {
  const _McqChoices({
    required this.options,
    required this.correctAnswer,
    required this.selectedAnswer,
    required this.answered,
    required this.onSelect,
  });

  final List<String> options;
  final String correctAnswer;
  final String? selectedAnswer;
  final bool answered;
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (final option in options)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: _ChoiceTile(
              label: option,
              selected: selectedAnswer == option,
              correct: answered && option == correctAnswer,
              wrong: answered && selectedAnswer == option && option != correctAnswer,
              onTap: () => onSelect(option),
            ),
          ),
      ],
    );
  }
}

class _TextInput extends StatelessWidget {
  const _TextInput({
    required this.controller,
    required this.answered,
    required this.isFillBlank,
  });

  final TextEditingController controller;
  final bool answered;
  final bool isFillBlank;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      enabled: !answered,
      autofocus: true,
      textCapitalization: TextCapitalization.none,
      inputFormatters: isFillBlank
          ? [FilteringTextInputFormatter.deny(RegExp(r'\n'))]
          : null,
      maxLines: isFillBlank ? 1 : 3,
      style: const TextStyle(
        color: AppColors.textPrimary,
        fontSize: 18,
        fontWeight: FontWeight.w500,
      ),
      decoration: InputDecoration(
        hintText: isFillBlank ? 'Complète la phrase…' : 'Écris ta réponse…',
      ),
    );
  }
}

class _FeedbackBanner extends StatelessWidget {
  const _FeedbackBanner({required this.isCorrect, required this.explanation});
  final bool isCorrect;
  final String explanation;

  @override
  Widget build(BuildContext context) {
    final color = isCorrect ? AppColors.success : AppColors.warning;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withOpacity(0.35)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(isCorrect ? '✅' : '💡', style: const TextStyle(fontSize: 22)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isCorrect ? 'Bravo !' : 'Pas tout à fait.',
                  style: TextStyle(
                    color: color,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (!isCorrect) ...[
                  const SizedBox(height: 4),
                  Text(
                    'Bonne réponse : $explanation',
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ══════════════════════════════════════════════
//  Vues auxiliaires
// ══════════════════════════════════════════════

class _LoadingView extends StatelessWidget {
  const _LoadingView();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: CircularProgressIndicator(color: AppColors.limeAccent, strokeWidth: 2.5),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, color: AppColors.error, size: 48),
            const SizedBox(height: 16),
            Text(
              message,
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.textSecondary, fontSize: 14, height: 1.5),
            ),
            const SizedBox(height: 28),
            ElevatedButton(onPressed: onRetry, child: const Text('Réessayer')),
          ],
        ),
      ),
    );
  }
}

// ══════════════════════════════════════════════
//  Tuile de choix MCQ (réutilisée depuis session)
// ══════════════════════════════════════════════

class _ChoiceTile extends StatelessWidget {
  const _ChoiceTile({
    required this.label,
    required this.selected,
    required this.correct,
    required this.wrong,
    required this.onTap,
  });
  final String label;
  final bool selected;
  final bool correct;
  final bool wrong;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    Color border = AppColors.borderSubtle;
    Color bg = AppColors.charcoal;

    if (correct) {
      border = AppColors.success;
      bg = AppColors.success.withOpacity(0.12);
    } else if (wrong) {
      border = AppColors.error;
      bg = AppColors.error.withOpacity(0.12);
    } else if (selected) {
      border = AppColors.limeAccent;
    }

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: border, width: 1.5),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                label,
                style: const TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            if (correct)
              const Icon(Icons.check_circle, color: AppColors.success, size: 20)
            else if (wrong)
              const Icon(Icons.cancel, color: AppColors.error, size: 20),
          ],
        ),
      ),
    );
  }
}
