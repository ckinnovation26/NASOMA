import 'package:json_annotation/json_annotation.dart';

part 'scan_model.g.dart';

@JsonSerializable()
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

  factory ScanModel.fromJson(Map<String, dynamic> json) =>
      _$ScanModelFromJson(json);

  Map<String, dynamic> toJson() => _$ScanModelToJson(this);

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
