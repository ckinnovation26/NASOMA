import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/api/api_client.dart';
import '../models/exercise_model.dart';
import '../models/session_model.dart';
import '../repositories/session_repository_impl.dart';

enum SessionState { idle, loading, active, submitting, completed, error }

final sessionRepositoryProvider = Provider<SessionRepository>((ref) {
  return SessionRepositoryImpl(dio: ref.read(apiClientProvider));
});

class SessionNotifier extends StateNotifier<SessionState> {
  SessionNotifier(this._repo) : super(SessionState.idle);

  final SessionRepository _repo;

  SessionModel? _currentSession;
  List<ExerciseModel> _exercises = [];
  int _currentExerciseIndex = 0;
  String? _errorMessage;
  int _correctCount = 0;

  SessionModel? get currentSession => _currentSession;
  List<ExerciseModel> get exercises => List.unmodifiable(_exercises);
  ExerciseModel? get currentExercise =>
      _currentExerciseIndex < _exercises.length ? _exercises[_currentExerciseIndex] : null;
  int get currentExerciseIndex => _currentExerciseIndex;
  int get totalExercises => _exercises.length;
  int get correctCount => _correctCount;
  String? get errorMessage => _errorMessage;
  bool get isActive => state == SessionState.active;
  bool get isCompleted => state == SessionState.completed;

  Future<void> loadSession(String sessionId) async {
    state = SessionState.loading;
    _errorMessage = null;
    _currentExerciseIndex = 0;
    _correctCount = 0;

    try {
      final exercises = await _repo.fetchExercises(sessionId);
      _exercises = exercises;
      if (_exercises.isEmpty) {
        _errorMessage = 'Aucun exercice disponible pour cette session.';
        state = SessionState.error;
      } else {
        state = SessionState.active;
      }
    } catch (e) {
      _errorMessage = e.toString();
      state = SessionState.error;
    }
  }

  void setExercises(List<ExerciseModel> exercises) {
    _exercises = exercises;
    _currentExerciseIndex = 0;
    _correctCount = 0;
    state = exercises.isEmpty ? SessionState.error : SessionState.active;
  }

  Future<bool> submitAnswer(String sessionId, String answer) async {
    final ex = currentExercise;
    if (ex == null) return false;

    state = SessionState.submitting;

    final isCorrect = answer.trim().toLowerCase() ==
        ex.correctAnswer.trim().toLowerCase();

    // Mise à jour locale optimiste
    _exercises[_currentExerciseIndex] = ex.copyWith(
      userAnswer: answer,
      isCorrect: isCorrect,
    );
    if (isCorrect) _correctCount++;

    // Envoi au backend (best-effort : on ne bloque pas si échoue)
    try {
      await _repo.submitAnswer(sessionId, ex.id, answer);
    } catch (_) {
      // Erreur réseau non bloquante : BKT se mettra à jour au prochain sync
    }

    state = SessionState.active;
    return isCorrect;
  }

  Future<void> moveToNext(String sessionId) async {
    if (_currentExerciseIndex < _exercises.length - 1) {
      _currentExerciseIndex++;
      state = SessionState.active;
    } else {
      await _completeSession(sessionId);
    }
  }

  Future<void> _completeSession(String sessionId) async {
    try {
      final completed = await _repo.completeSession(sessionId);
      _currentSession = completed;
    } catch (_) {
      // Erreur réseau : on marque quand même localement
    }
    state = SessionState.completed;
  }

  void completeSession() => state = SessionState.completed;

  void setError(String message) {
    _errorMessage = message;
    state = SessionState.error;
  }

  void reset() {
    _currentSession = null;
    _exercises = [];
    _currentExerciseIndex = 0;
    _correctCount = 0;
    _errorMessage = null;
    state = SessionState.idle;
  }
}

final sessionProvider = StateNotifierProvider<SessionNotifier, SessionState>((ref) {
  return SessionNotifier(ref.read(sessionRepositoryProvider));
});
