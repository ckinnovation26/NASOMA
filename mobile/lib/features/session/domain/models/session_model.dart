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

  factory SessionModel.fromJson(Map<String, dynamic> json) => SessionModel(
        id: json['id'] as String,
        userId: json['userId'] as String,
        studentId: json['studentId'] as String,
        diagnosticId: json['diagnosticId'] as String,
        createdAt: DateTime.parse(json['createdAt'] as String),
        startedAt: json['startedAt'] == null
            ? null
            : DateTime.parse(json['startedAt'] as String),
        completedAt: json['completedAt'] == null
            ? null
            : DateTime.parse(json['completedAt'] as String),
        status: json['status'] as String,
        exercisesCount: (json['exercisesCount'] as num).toInt(),
        exercisesCompleted: (json['exercisesCompleted'] as num).toInt(),
        score: (json['score'] as num?)?.toDouble(),
      );

  Map<String, dynamic> toJson() => <String, dynamic>{
        'id': id,
        'userId': userId,
        'studentId': studentId,
        'diagnosticId': diagnosticId,
        'createdAt': createdAt.toIso8601String(),
        'startedAt': startedAt?.toIso8601String(),
        'completedAt': completedAt?.toIso8601String(),
        'status': status,
        'exercisesCount': exercisesCount,
        'exercisesCompleted': exercisesCompleted,
        'score': score,
      };

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
