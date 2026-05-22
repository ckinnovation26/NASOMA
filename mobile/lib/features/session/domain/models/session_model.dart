import 'package:json_annotation/json_annotation.dart';

part 'session_model.g.dart';

@JsonSerializable()
class SessionModel {
  final String id;
  final String userId;
  final String studentId;
  final String diagnosticId;
  final DateTime createdAt;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final String status;
  final int exercisesCount;
  final int exercisesCompleted;
  final double? score;

  SessionModel({
    required this.id,
    required this.userId,
    required this.studentId,
    required this.diagnosticId,
    required this.createdAt,
    this.startedAt,
    this.completedAt,
    required this.status,
    required this.exercisesCount,
    required this.exercisesCompleted,
    this.score,
  });

  factory SessionModel.fromJson(Map<String, dynamic> json) =>
      _$SessionModelFromJson(json);

  Map<String, dynamic> toJson() => _$SessionModelToJson(this);

  SessionModel copyWith({
    String? id,
    String? userId,
    String? studentId,
    String? diagnosticId,
    DateTime? createdAt,
    DateTime? startedAt,
    DateTime? completedAt,
    String? status,
    int? exercisesCount,
    int? exercisesCompleted,
    double? score,
  }) =>
      SessionModel(
        id: id ?? this.id,
        userId: userId ?? this.userId,
        studentId: studentId ?? this.studentId,
        diagnosticId: diagnosticId ?? this.diagnosticId,
        createdAt: createdAt ?? this.createdAt,
        startedAt: startedAt ?? this.startedAt,
        completedAt: completedAt ?? this.completedAt,
        status: status ?? this.status,
        exercisesCount: exercisesCount ?? this.exercisesCount,
        exercisesCompleted: exercisesCompleted ?? this.exercisesCompleted,
        score: score ?? this.score,
      );
}
