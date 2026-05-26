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

  factory ExerciseModel.fromJson(Map<String, dynamic> json) => ExerciseModel(
        id: json['id'] as String,
        sessionId: json['sessionId'] as String,
        conceptCode: json['conceptCode'] as String,
        type: json['type'] as String,
        question: json['question'] as String,
        options: (json['options'] as List<dynamic>?)
            ?.map((e) => e as String)
            .toList(),
        correctAnswer: json['correctAnswer'] as String,
        userAnswer: json['userAnswer'] as String?,
        isCorrect: json['isCorrect'] as bool?,
        timeSpentSeconds: (json['timeSpentSeconds'] as num?)?.toInt(),
        createdAt: DateTime.parse(json['createdAt'] as String),
        submittedAt: json['submittedAt'] == null
            ? null
            : DateTime.parse(json['submittedAt'] as String),
      );

  Map<String, dynamic> toJson() => <String, dynamic>{
        'id': id,
        'sessionId': sessionId,
        'conceptCode': conceptCode,
        'type': type,
        'question': question,
        'options': options,
        'correctAnswer': correctAnswer,
        'userAnswer': userAnswer,
        'isCorrect': isCorrect,
        'timeSpentSeconds': timeSpentSeconds,
        'createdAt': createdAt.toIso8601String(),
        'submittedAt': submittedAt?.toIso8601String(),
      };

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
