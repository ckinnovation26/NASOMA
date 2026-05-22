import 'package:json_annotation/json_annotation.dart';

part 'contact_model.g.dart';

@JsonSerializable()
class ContactModel {
  final String id;
  final String? firstName;
  final String? lastName;
  final String? email;
  final String? phoneNumber;
  final String? schoolOrCompany;
  final String? role;
  final String? locale;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final String? rawText;

  ContactModel({
    required this.id,
    this.firstName,
    this.lastName,
    this.email,
    this.phoneNumber,
    this.schoolOrCompany,
    this.role,
    this.locale,
    this.notes,
    required this.createdAt,
    this.updatedAt,
    this.rawText,
  });

  factory ContactModel.fromJson(Map<String, dynamic> json) =>
      _$ContactModelFromJson(json);

  Map<String, dynamic> toJson() => _$ContactModelToJson(this);

  String? get fullName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    } else if (firstName != null) {
      return firstName;
    } else if (lastName != null) {
      return lastName;
    }
    return null;
  }

  ContactModel copyWith({
    String? id,
    String? firstName,
    String? lastName,
    String? email,
    String? phoneNumber,
    String? schoolOrCompany,
    String? role,
    String? locale,
    String? notes,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? rawText,
  }) =>
      ContactModel(
        id: id ?? this.id,
        firstName: firstName ?? this.firstName,
        lastName: lastName ?? this.lastName,
        email: email ?? this.email,
        phoneNumber: phoneNumber ?? this.phoneNumber,
        schoolOrCompany: schoolOrCompany ?? this.schoolOrCompany,
        role: role ?? this.role,
        locale: locale ?? this.locale,
        notes: notes ?? this.notes,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
        rawText: rawText ?? this.rawText,
      );
}
