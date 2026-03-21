/// Credentials du staff
enum StaffCredential { pr, dr, m, ms }

extension StaffCredentialExtension on StaffCredential {
  String get label {
    switch (this) {
      case StaffCredential.pr: return 'Pr.';
      case StaffCredential.dr: return 'Dr.';
      case StaffCredential.m: return 'M.';
      case StaffCredential.ms: return 'Ms.';
    }
  }

  static StaffCredential fromString(String? value) {
    switch (value) {
      case 'Pr.': return StaffCredential.pr;
      case 'Dr.': return StaffCredential.dr;
      case 'Ms.': return StaffCredential.ms;
      default: return StaffCredential.m;
    }
  }
}

/// Role du staff
enum StaffRole { pi, si, sc, ph, phs, lab, rad, oth }

extension StaffRoleExtension on StaffRole {
  String get label {
    switch (this) {
      case StaffRole.pi: return 'PI';
      case StaffRole.si: return 'SI';
      case StaffRole.sc: return 'SC';
      case StaffRole.ph: return 'PH';
      case StaffRole.phs: return 'PHS';
      case StaffRole.lab: return 'LAB';
      case StaffRole.rad: return 'RAD';
      case StaffRole.oth: return 'OTH';
    }
  }

  String get fullLabel {
    switch (this) {
      case StaffRole.pi: return 'Principal Investigator';
      case StaffRole.si: return 'Sub-Investigator';
      case StaffRole.sc: return 'Study Coordinator';
      case StaffRole.ph: return 'Pharmacist';
      case StaffRole.phs: return 'Pharmacy Staff';
      case StaffRole.lab: return 'Laboratory';
      case StaffRole.rad: return 'Radiology';
      case StaffRole.oth: return 'Other';
    }
  }

  int get color {
    switch (this) {
      case StaffRole.pi: return 0xFF9C27B0;
      case StaffRole.si: return 0xFF673AB7;
      case StaffRole.sc: return 0xFF2196F3;
      case StaffRole.ph: return 0xFF4CAF50;
      case StaffRole.phs: return 0xFF8BC34A;
      case StaffRole.lab: return 0xFFFF9800;
      case StaffRole.rad: return 0xFFFF5722;
      case StaffRole.oth: return 0xFF9E9E9E;
    }
  }

  static StaffRole fromString(String? value) {
    switch (value) {
      case 'PI': return StaffRole.pi;
      case 'SI': return StaffRole.si;
      case 'SC': return StaffRole.sc;
      case 'PH': return StaffRole.ph;
      case 'PHS': return StaffRole.phs;
      case 'LAB': return StaffRole.lab;
      case 'RAD': return StaffRole.rad;
      default: return StaffRole.oth;
    }
  }
}

/// Modele de membre du staff
class StaffMember {
  final int? id;
  final int studySiteId;
  final String firstName;
  final String lastName;
  final StaffCredential credential;
  final StaffRole role;
  final DateTime? startDate;
  final DateTime? endDate;

  StaffMember({
    this.id,
    required this.studySiteId,
    required this.firstName,
    required this.lastName,
    this.credential = StaffCredential.m,
    this.role = StaffRole.oth,
    this.startDate,
    this.endDate,
  });

  String get fullName => '${credential.label} $firstName $lastName';

  bool get isActive => endDate == null || endDate!.isAfter(DateTime.now());

  factory StaffMember.fromMap(Map<String, dynamic> map) {
    return StaffMember(
      id: map['id'] as int?,
      studySiteId: map['study_site_id'] as int,
      firstName: map['first_name'] as String? ?? '',
      lastName: map['last_name'] as String? ?? '',
      credential: StaffCredentialExtension.fromString(map['credential'] as String?),
      role: StaffRoleExtension.fromString(map['role'] as String?),
      startDate: map['start_date'] != null
          ? DateTime.tryParse(map['start_date'].toString())
          : null,
      endDate: map['end_date'] != null
          ? DateTime.tryParse(map['end_date'].toString())
          : null,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'study_site_id': studySiteId,
      'first_name': firstName,
      'last_name': lastName,
      'credential': credential.label,
      'role': role.label,
      'start_date': startDate?.toIso8601String().split('T')[0],
      'end_date': endDate?.toIso8601String().split('T')[0],
    };
  }
}

/// Donnees de demo
final Map<int, List<StaffMember>> demoStaffBySite = {
  1: [
    StaffMember(
      id: 1,
      studySiteId: 1,
      firstName: 'Jean',
      lastName: 'Martin',
      credential: StaffCredential.dr,
      role: StaffRole.pi,
      startDate: DateTime(2026, 1, 15),
    ),
    StaffMember(
      id: 2,
      studySiteId: 1,
      firstName: 'Marie',
      lastName: 'Dupont',
      credential: StaffCredential.dr,
      role: StaffRole.si,
      startDate: DateTime(2026, 1, 20),
    ),
    StaffMember(
      id: 3,
      studySiteId: 1,
      firstName: 'Sophie',
      lastName: 'Bernard',
      credential: StaffCredential.ms,
      role: StaffRole.sc,
      startDate: DateTime(2026, 1, 15),
    ),
  ],
  2: [
    StaffMember(
      id: 4,
      studySiteId: 2,
      firstName: 'Pierre',
      lastName: 'Dubois',
      credential: StaffCredential.pr,
      role: StaffRole.pi,
      startDate: DateTime(2026, 2, 1),
    ),
    StaffMember(
      id: 5,
      studySiteId: 2,
      firstName: 'Claire',
      lastName: 'Moreau',
      credential: StaffCredential.ms,
      role: StaffRole.sc,
      startDate: DateTime(2026, 2, 1),
    ),
  ],
  3: [
    StaffMember(
      id: 6,
      studySiteId: 3,
      firstName: 'Luc',
      lastName: 'Bernard',
      credential: StaffCredential.dr,
      role: StaffRole.pi,
      startDate: DateTime(2026, 1, 20),
    ),
  ],
  4: [
    StaffMember(
      id: 7,
      studySiteId: 4,
      firstName: 'Anne',
      lastName: 'Petit',
      credential: StaffCredential.dr,
      role: StaffRole.pi,
      startDate: DateTime(2026, 3, 1),
    ),
    StaffMember(
      id: 8,
      studySiteId: 4,
      firstName: 'Marc',
      lastName: 'Leroy',
      credential: StaffCredential.m,
      role: StaffRole.ph,
      startDate: DateTime(2026, 3, 1),
    ),
  ],
};
