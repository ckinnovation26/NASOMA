// Session — 3 micro-exercices QCM pour combler la lacune détectée.

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class _Question {
  const _Question({
    required this.prompt,
    required this.choices,
    required this.correctIndex,
    required this.hint,
  });
  final String prompt;
  final List<String> choices;
  final int correctIndex;
  final String hint;
}

class SessionScreen extends StatefulWidget {
  const SessionScreen({super.key});

  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> {
  static const _questions = [
    _Question(
      prompt: 'Calcule : 27 + 15',
      choices: ['32', '42', '40', '52'],
      correctIndex: 1,
      hint: '7 + 5 = 12 → tu écris 2 et tu retiens 1.',
    ),
    _Question(
      prompt: 'Calcule : 38 + 24',
      choices: ['52', '60', '62', '72'],
      correctIndex: 2,
      hint: '8 + 4 = 12 → tu écris 2, retiens 1. Puis 3 + 2 + 1 = 6.',
    ),
    _Question(
      prompt: 'Calcule : 56 + 18',
      choices: ['64', '74', '76', '84'],
      correctIndex: 1,
      hint: '6 + 8 = 14 → tu écris 4, retiens 1. Puis 5 + 1 + 1 = 7.',
    ),
  ];

  int _index = 0;
  int? _selected;
  bool _checked = false;
  int _correctCount = 0;

  void _onSelect(int i) {
    if (_checked) return;
    setState(() {
      _selected = i;
      _checked = true;
      if (i == _questions[_index].correctIndex) _correctCount++;
    });
  }

  void _next() {
    if (_index < _questions.length - 1) {
      setState(() {
        _index++;
        _selected = null;
        _checked = false;
      });
    } else {
      context.go('/scan/done', extra: _correctCount);
    }
  }

  @override
  Widget build(BuildContext context) {
    final q = _questions[_index];
    final isCorrect = _selected == q.correctIndex;

    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.go('/home'),
        ),
        title: Text(
          'Exercice ${_index + 1} / ${_questions.length}',
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Barre de progression
              LinearProgressIndicator(
                value: (_index + (_checked ? 1 : 0)) / _questions.length,
                backgroundColor: AppColors.charcoal,
                valueColor: const AlwaysStoppedAnimation(AppColors.limeAccent),
                minHeight: 6,
                borderRadius: BorderRadius.circular(3),
              ),
              const SizedBox(height: 32),

              Text(
                'Addition avec retenue',
                style: TextStyle(
                  color: AppColors.textTertiary,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.6,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                q.prompt,
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 32),

              for (var i = 0; i < q.choices.length; i++)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: _ChoiceTile(
                    label: q.choices[i],
                    selected: _selected == i,
                    correct: _checked && i == q.correctIndex,
                    wrong: _checked && _selected == i && i != q.correctIndex,
                    onTap: () => _onSelect(i),
                  ),
                ),

              const Spacer(),

              if (_checked) ...[
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: (isCorrect ? AppColors.success : AppColors.warning)
                        .withOpacity(0.15),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                      color: (isCorrect ? AppColors.success : AppColors.warning)
                          .withOpacity(0.4),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isCorrect ? '✅' : '💡',
                        style: const TextStyle(fontSize: 22),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              isCorrect ? 'Bravo !' : 'Pas tout à fait.',
                              style: TextStyle(
                                color: isCorrect
                                    ? AppColors.success
                                    : AppColors.warning,
                                fontSize: 14,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              q.hint,
                              style: const TextStyle(
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
                ).animate().fadeIn(duration: 250.ms).slideY(begin: 0.1),
                const SizedBox(height: 14),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _next,
                    child: Text(
                      _index < _questions.length - 1
                          ? 'Question suivante →'
                          : 'Voir mes résultats →',
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

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
    Color text = AppColors.textPrimary;

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
            Text(
              label,
              style: TextStyle(
                color: text,
                fontSize: 18,
                fontWeight: FontWeight.w600,
                fontFamily: 'monospace',
              ),
            ),
            const Spacer(),
            if (correct)
              const Icon(Icons.check_circle, color: AppColors.success)
            else if (wrong)
              const Icon(Icons.cancel, color: AppColors.error),
          ],
        ),
      ),
    );
  }
}
