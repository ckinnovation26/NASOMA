import 'package:json_annotation/json_annotation.dart';

part 'exercise_model.g.dart';

@JsonSerializable()
class ExerciseModel {
  final String id;
  final String sessionId;
  final String conceptCode;
  final String type;
  final String question;
  final List<String>? options;
  final String correctAnswer;
  final String? userAnswer;
  final bool? isCorrect;
  final int? timeSpentSeconds;
  final DateTime createdAt;
  final DateTime? submittedAt;

  ExerciseModel({
    required this.id,
    required this.sessionId,
    required this.conceptCode,
    required this.type,
    required this.question,
    this.options,
    required this.correctAnswer,
    this.userAnswer,
    this.isCorrect,
    this.timeSpentSeconds,
    required this.createdAt,
    this.submittedAt,
  });

  factory ExerciseModel.fromJson(Map<String, dynamic> json) =>
      _$ExerciseModelFromJson(json);

  Map<String, dynamic> toJson() => _$ExerciseModelToJson(this);

  ExerciseModel copyWith({
    String? id,
    String? sessionId,
    String? conceptCode,
    String? type,
    String? question,
    List<String>? options,
    String? correctAnswer,
    String? userAnswer,
    bool? isCorrect,
    int? timeSpentSeconds,
    DateTime? createdAt,
    DateTime? submittedAt,
  }) =>
      ExerciseModel(
        id: id ?? this.id,
        sessionId: sessionId ?? this.sessionId,
        conceptCode: conceptCode ?? this.conceptCode,
        type: type ?? this.type,
        question: question ?? this.question,
        options: options ?? this.options,
        correctAnswer: correctAnswer ?? this.correctAnswer,
        userAnswer: userAnswer ?? this.userAnswer,
        isCorrect: isCorrect ?? this.isCorrect,
        timeSpentSeconds: timeSpentSeconds ?? this.timeSpentSeconds,
        createdAt: createdAt ?? this.createdAt,
        submittedAt: submittedAt ?? this.submittedAt,
      );
}
