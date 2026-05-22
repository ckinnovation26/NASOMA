import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/session_model.dart';
import '../models/exercise_model.dart';

enum SessionState {
  idle,
  loading,
  active,
  submitting,
  completed,
  error,
}

class SessionNotifier extends StateNotifier<SessionState> {
  SessionNotifier() : super(SessionState.idle);

  SessionModel? _currentSession;
  List<ExerciseModel> _exercises = [];
  int _currentExerciseIndex = 0;
  String? _errorMessage;

  SessionModel? get currentSession => _currentSession;
  List<ExerciseModel> get exercises => _exercises;
  ExerciseModel? get currentExercise =>
      _currentExerciseIndex < _exercises.length
          ? _exercises[_currentExerciseIndex]
          : null;
  int get currentExerciseIndex => _currentExerciseIndex;
  int get totalExercises => _exercises.length;
  String? get errorMessage => _errorMessage;

  bool get isActive => state == SessionState.active;
  bool get isCompleted => state == SessionState.completed;

  Future<void> loadSession(SessionModel session) async {
    state = SessionState.loading;
    _currentSession = session;
    _errorMessage = null;
    _currentExerciseIndex = 0;
    // fetch exercises depuis repository se fera via un autre provider (voir M7)
  }

  void setExercises(List<ExerciseModel> exercises) {
    _exercises = exercises;
    if (_exercises.isNotEmpty) {
      state = SessionState.active;
    }
  }

  Future<void> submitAnswer(String answer) async {
    if (currentExercise == null) {
      _errorMessage = 'Pas d\'exercice à soumettre';
      state = SessionState.error;
      return;
    }

    state = SessionState.submitting;
    final exerciseIndex = _currentExerciseIndex;
    final updatedExercise = currentExercise!.copyWith(userAnswer: answer);
    _exercises[exerciseIndex] = updatedExercise;
    // submission au backend se fera via un autre provider (voir M7)
  }

  void moveToNextExercise() {
    if (_currentExerciseIndex < _exercises.length - 1) {
      _currentExerciseIndex++;
      state = SessionState.active;
    } else {
      completeSession();
    }
  }

  void completeSession() {
    _currentSession = _currentSession?.copyWith(
      status: 'completed',
      completedAt: DateTime.now(),
      exercisesCompleted: _exercises.length,
    );
    state = SessionState.completed;
  }

  void setError(String message) {
    _errorMessage = message;
    state = SessionState.error;
  }

  void reset() {
    _currentSession = null;
    _exercises = [];
    _currentExerciseIndex = 0;
    _errorMessage = null;
    state = SessionState.idle;
  }
}

final sessionProvider =
    StateNotifierProvider<SessionNotifier, SessionState>((ref) {
  return SessionNotifier();
});
