/// Statut d'un site
enum SiteStatus { active, onHold, closed }

extension SiteStatusExtension on SiteStatus {
  String get label {
    switch (this) {
      case SiteStatus.active: return 'Active';
      case SiteStatus.onHold: return 'On Hold';
      case SiteStatus.closed: return 'Closed';
    }
  }

  String get value {
    switch (this) {
      case SiteStatus.active: return 'Active';
      case SiteStatus.onHold: return 'On Hold';
      case SiteStatus.closed: return 'Closed';
    }
  }

  int get color {
    switch (this) {
      case SiteStatus.active: return 0xFF4CAF50;
      case SiteStatus.onHold: return 0xFFFF9800;
      case SiteStatus.closed: return 0xFFF44336;
    }
  }

  static SiteStatus fromString(String? value) {
    switch (value) {
      case 'On Hold': return SiteStatus.onHold;
      case 'Closed': return SiteStatus.closed;
      default: return SiteStatus.active;
    }
  }
}

/// Modèle de site (informations générales)
class Site {
  final int? id;
  final String siteNumber;
  final String? siteName;
  final String? address;
  final String? city;
  final String? country;
  final String? phone;
  final String? email;
  final DateTime? createdAt;

  Site({
    this.id,
    required this.siteNumber,
    this.siteName,
    this.address,
    this.city,
    this.country,
    this.phone,
    this.email,
    this.createdAt,
  });

  factory Site.fromMap(Map<String, dynamic> map) {
    return Site(
      id: map['id'] as int?,
      siteNumber: map['site_number'] as String? ?? '',
      siteName: map['site_name'] as String?,
      address: map['address'] as String?,
      city: map['city'] as String?,
      country: map['country'] as String?,
      phone: map['phone'] as String?,
      email: map['email'] as String?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'site_number': siteNumber,
      'site_name': siteName,
      'address': address,
      'city': city,
      'country': country,
      'phone': phone,
      'email': email,
    };
  }
}

/// Liaison étude-site (informations spécifiques à l'étude)
class StudySite {
  final int? id;
  final int studyId;
  final int siteId;
  final SiteStatus status;
  final String? principalInvestigator;
  final DateTime? activationDate;
  final DateTime? firstPatientDate;
  final int targetPatients;
  final String? comments;

  // Données jointes depuis Site
  final String? siteNumber;
  final String? siteName;
  final String? city;
  final String? country;
  int patientCount;

  StudySite({
    this.id,
    required this.studyId,
    required this.siteId,
    this.status = SiteStatus.active,
    this.principalInvestigator,
    this.activationDate,
    this.firstPatientDate,
    this.targetPatients = 0,
    this.comments,
    this.siteNumber,
    this.siteName,
    this.city,
    this.country,
    this.patientCount = 0,
  });

  double get recruitmentProgress {
    if (targetPatients == 0) return 0;
    return patientCount / targetPatients;
  }

  int get progressColor {
    if (recruitmentProgress >= 1.0) return 0xFF4CAF50;
    if (recruitmentProgress >= 0.5) return 0xFFFF9800;
    return 0xFF9E9E9E;
  }

  factory StudySite.fromMap(Map<String, dynamic> map) {
    return StudySite(
      id: map['id'] as int?,
      studyId: map['study_id'] as int,
      siteId: map['site_id'] as int,
      status: SiteStatusExtension.fromString(map['status'] as String?),
      principalInvestigator: map['principal_investigator'] as String?,
      activationDate: map['activation_date'] != null
          ? DateTime.tryParse(map['activation_date'].toString())
          : null,
      firstPatientDate: map['first_patient_date'] != null
          ? DateTime.tryParse(map['first_patient_date'].toString())
          : null,
      targetPatients: map['target_patients'] as int? ?? 0,
      comments: map['comments'] as String?,
      siteNumber: map['site_number'] as String?,
      siteName: map['site_name'] as String?,
      city: map['city'] as String?,
      country: map['country'] as String?,
      patientCount: map['patient_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'study_id': studyId,
      'site_id': siteId,
      'status': status.value,
      'principal_investigator': principalInvestigator,
      'activation_date': activationDate?.toIso8601String().split('T')[0],
      'first_patient_date': firstPatientDate?.toIso8601String().split('T')[0],
      'target_patients': targetPatients,
      'comments': comments,
    };
  }
}
