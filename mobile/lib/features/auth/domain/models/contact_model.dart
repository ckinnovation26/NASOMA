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

  factory ContactModel.fromJson(Map<String, dynamic> json) => ContactModel(
        id: json['id'] as String,
        firstName: json['firstName'] as String?,
        lastName: json['lastName'] as String?,
        email: json['email'] as String?,
        phoneNumber: json['phoneNumber'] as String?,
        schoolOrCompany: json['schoolOrCompany'] as String?,
        role: json['role'] as String?,
        locale: json['locale'] as String?,
        notes: json['notes'] as String?,
        createdAt: DateTime.parse(json['createdAt'] as String),
        updatedAt: json['updatedAt'] == null
            ? null
            : DateTime.parse(json['updatedAt'] as String),
        rawText: json['rawText'] as String?,
      );

  Map<String, dynamic> toJson() => <String, dynamic>{
        'id': id,
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'phoneNumber': phoneNumber,
        'schoolOrCompany': schoolOrCompany,
        'role': role,
        'locale': locale,
        'notes': notes,
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt?.toIso8601String(),
        'rawText': rawText,
      };

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
