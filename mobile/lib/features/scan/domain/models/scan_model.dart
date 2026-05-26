class ScanModel {
  final String id;
  final String sessionId;
  final String base64Image;
  final DateTime createdAt;
  final String? extractedText;
  final String? ocrConfidence;
  final String? uploadStatus;
  final String? errorMessage;

  ScanModel({
    required this.id,
    required this.sessionId,
    required this.base64Image,
    required this.createdAt,
    this.extractedText,
    this.ocrConfidence,
    this.uploadStatus,
    this.errorMessage,
  });

  factory ScanModel.fromJson(Map<String, dynamic> json) => ScanModel(
        id: json['id'] as String,
        sessionId: json['sessionId'] as String,
        base64Image: json['base64Image'] as String,
        createdAt: DateTime.parse(json['createdAt'] as String),
        extractedText: json['extractedText'] as String?,
        ocrConfidence: json['ocrConfidence'] as String?,
        uploadStatus: json['uploadStatus'] as String?,
        errorMessage: json['errorMessage'] as String?,
      );

  Map<String, dynamic> toJson() => <String, dynamic>{
        'id': id,
        'sessionId': sessionId,
        'base64Image': base64Image,
        'createdAt': createdAt.toIso8601String(),
        'extractedText': extractedText,
        'ocrConfidence': ocrConfidence,
        'uploadStatus': uploadStatus,
        'errorMessage': errorMessage,
      };

  ScanModel copyWith({
    String? id,
    String? sessionId,
    String? base64Image,
    DateTime? createdAt,
    String? extractedText,
    String? ocrConfidence,
    String? uploadStatus,
    String? errorMessage,
  }) =>
      ScanModel(
        id: id ?? this.id,
        sessionId: sessionId ?? this.sessionId,
        base64Image: base64Image ?? this.base64Image,
        createdAt: createdAt ?? this.createdAt,
        extractedText: extractedText ?? this.extractedText,
        ocrConfidence: ocrConfidence ?? this.ocrConfidence,
        uploadStatus: uploadStatus ?? this.uploadStatus,
        errorMessage: errorMessage ?? this.errorMessage,
      );
}
