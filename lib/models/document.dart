/// Type de consentement
class ConsentType {
  final int? id;
  final String name;
  final String code;

  const ConsentType({this.id, required this.name, required this.code});

  factory ConsentType.fromMap(Map<String, dynamic> map) {
    return ConsentType(
      id: map['id'] as int?,
      name: map['name'] as String? ?? '',
      code: map['code'] as String? ?? '',
    );
  }
}

/// Version d'un type de consentement
class ConsentVersion {
  final int? id;
  final int? typeId;
  final String version;
  final DateTime date;
  final bool isCurrent;

  const ConsentVersion({
    this.id,
    this.typeId,
    required this.version,
    required this.date,
    this.isCurrent = false,
  });

  factory ConsentVersion.fromMap(Map<String, dynamic> map) {
    return ConsentVersion(
      id: map['id'] as int?,
      typeId: map['type_id'] as int?,
      version: map['version'] as String? ?? '',
      date: DateTime.tryParse(map['date']?.toString() ?? '') ?? DateTime.now(),
      isCurrent: map['is_current'] == 1 || map['is_current'] == true,
    );
  }
}

/// Statut d'un consentement patient
enum ConsentStatus { signed, missing, needsUpdate }

extension ConsentStatusExtension on ConsentStatus {
  String get label {
    switch (this) {
      case ConsentStatus.signed: return 'Signed';
      case ConsentStatus.missing: return 'Missing';
      case ConsentStatus.needsUpdate: return 'Update';
    }
  }

  int get color {
    switch (this) {
      case ConsentStatus.signed: return 0xFF4CAF50;
      case ConsentStatus.missing: return 0xFFF44336;
      case ConsentStatus.needsUpdate: return 0xFFFF9800;
    }
  }

  static ConsentStatus fromString(String? value) {
    switch (value) {
      case 'Signed': return ConsentStatus.signed;
      case 'Update': return ConsentStatus.needsUpdate;
      default: return ConsentStatus.missing;
    }
  }
}

/// Consentement d'un patient
class PatientConsent {
  final int? id;
  final int? patientId;
  final String? patientNumber;
  final String consentType;
  final String? version;
  final DateTime? signedDate;
  final ConsentStatus status;

  PatientConsent({
    this.id,
    this.patientId,
    this.patientNumber,
    required this.consentType,
    this.version,
    this.signedDate,
    this.status = ConsentStatus.missing,
  });

  /// Libellé complet (Type + Version + Date)
  String get fullLabel {
    if (version == null || signedDate == null) return consentType;
    final dateStr = '${signedDate!.day.toString().padLeft(2, '0')}-${_monthName(signedDate!.month)}-${signedDate!.year.toString().substring(2)}';
    return '$consentType $version ($dateStr)';
  }

  static String _monthName(int month) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[month - 1];
  }

  factory PatientConsent.fromMap(Map<String, dynamic> map) {
    return PatientConsent(
      id: map['id'] as int?,
      patientId: map['patient_id'] as int?,
      patientNumber: map['patient_number'] as String?,
      consentType: map['consent_type'] as String? ?? '',
      version: map['version'] as String?,
      signedDate: map['signed_date'] != null
          ? DateTime.tryParse(map['signed_date'].toString())
          : null,
      status: ConsentStatusExtension.fromString(map['status'] as String?),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'patient_id': patientId,
      'consent_type': consentType,
      'version': version,
      'signed_date': signedDate?.toIso8601String().split('T')[0],
      'status': status.label,
    };
  }
}

/// Types de consentements par défaut
final List<ConsentType> defaultConsentTypes = [
  const ConsentType(id: 1, name: 'ICF Principal', code: 'ICF'),
  const ConsentType(id: 2, name: 'ICF PK', code: 'PK'),
  const ConsentType(id: 3, name: 'ICF Génétique', code: 'GEN'),
];

/// Versions par défaut
final List<ConsentVersion> defaultConsentVersions = [
  ConsentVersion(id: 1, typeId: 1, version: 'v1.0', date: DateTime(2026, 1, 15), isCurrent: false),
  ConsentVersion(id: 2, typeId: 1, version: 'v2.0', date: DateTime(2026, 2, 1), isCurrent: true),
  ConsentVersion(id: 3, typeId: 2, version: 'v1.0', date: DateTime(2026, 1, 15), isCurrent: true),
  ConsentVersion(id: 4, typeId: 3, version: 'v1.0', date: DateTime(2026, 1, 15), isCurrent: true),
];

/// Données de démo
final List<PatientConsent> demoConsents = [
  // Patient 001-001 - tous signés, ICF Principal v1.0 (ancienne version)
  PatientConsent(
    id: 1,
    patientId: 1,
    patientNumber: '001-001',
    consentType: 'ICF Principal',
    version: 'v1.0',
    signedDate: DateTime(2026, 2, 15),
    status: ConsentStatus.needsUpdate, // v2.0 disponible
  ),
  PatientConsent(
    id: 2,
    patientId: 1,
    patientNumber: '001-001',
    consentType: 'ICF PK',
    version: 'v1.0',
    signedDate: DateTime(2026, 2, 15),
    status: ConsentStatus.signed,
  ),
  PatientConsent(
    id: 3,
    patientId: 1,
    patientNumber: '001-001',
    consentType: 'ICF Génétique',
    version: 'v1.0',
    signedDate: DateTime(2026, 2, 15),
    status: ConsentStatus.signed,
  ),
  // Patient 001-002 - ICF Principal signé v2.0, PK manquant
  PatientConsent(
    id: 4,
    patientId: 2,
    patientNumber: '001-002',
    consentType: 'ICF Principal',
    version: 'v2.0',
    signedDate: DateTime(2026, 2, 20),
    status: ConsentStatus.signed,
  ),
  PatientConsent(
    id: 5,
    patientId: 2,
    patientNumber: '001-002',
    consentType: 'ICF PK',
    status: ConsentStatus.missing,
  ),
  PatientConsent(
    id: 6,
    patientId: 2,
    patientNumber: '001-002',
    consentType: 'ICF Génétique',
    version: 'v1.0',
    signedDate: DateTime(2026, 2, 20),
    status: ConsentStatus.signed,
  ),
  // Patient 002-001 - en screening, rien de signé
  PatientConsent(
    id: 7,
    patientId: 3,
    patientNumber: '002-001',
    consentType: 'ICF Principal',
    status: ConsentStatus.missing,
  ),
];
