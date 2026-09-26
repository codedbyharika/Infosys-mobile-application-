class UserModel {
  final String id;
  final String email;
  final String name;
  final String healthProfile;
  final DateTime? lastLogin;
  final bool isGuest;

  const UserModel({
    required this.id,
    required this.email,
    required this.name,
    this.healthProfile = 'General User',
    this.lastLogin,
    this.isGuest = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'health_profile': healthProfile,
      'last_login': lastLogin?.toIso8601String(),
      'is_guest': isGuest,
    };
  }

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id']?.toString() ?? 'usr_1',
      email: json['email']?.toString() ?? '',
      name: json['name']?.toString() ?? 'AirSense User',
      healthProfile: json['health_profile']?.toString() ?? 'General User',
      lastLogin: json['last_login'] != null
          ? DateTime.tryParse(json['last_login'].toString())
          : null,
      isGuest: json['is_guest'] == true,
    );
  }

  String get initials {
    final parts = name.trim().split(' ');
    if (parts.length >= 2 && parts[0].isNotEmpty && parts[1].isNotEmpty) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    } else if (name.isNotEmpty) {
      return name.substring(0, name.length >= 2 ? 2 : 1).toUpperCase();
    }
    return 'EA';
  }
}
