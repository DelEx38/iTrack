/// Statut d'un patient
enum PatientStatus { screening, included, completed, withdrawn, screenFailure }

extension PatientStatusExtension on PatientStatus {
  String get label {
    switch (this) {
      case PatientStatus.screening: return 'Screening';
      case PatientStatus.included: return 'Included';
      case PatientStatus.completed: return 'Completed';
      case PatientStatus.withdrawn: return 'Withdrawn';
      case PatientStatus.screenFailure: return 'Screen Failure';
    }
  }

  int get color {
    switch (this) {
      case PatientStatus.screening: return 0xFF2196F3;
      case PatientStatus.included: return 0xFF4CAF50;
      case PatientStatus.completed: return 0xFF9C27B0;
      case PatientStatus.withdrawn: return 0xFFF44336;
      case PatientStatus.screenFailure: return 0xFF9E9E9E;
    }
  }

  static PatientStatus fromString(String? value) {
    switch (value) {
      case 'Included': return PatientStatus.included;
      case 'Completed': return PatientStatus.completed;
      case 'Withdrawn': return PatientStatus.withdrawn;
      case 'Screen Failure': return PatientStatus.screenFailure;
      default: return PatientStatus.screening;
    }
  }
}

/// Modèle de patient
class Patient {
  final int? id;
  final int? studyId;
  final String patientNumber;
  final String? initials;
  final DateTime? birthDate;
  final String? siteId;
  final DateTime? screeningDate;
  final DateTime? inclusionDate;
  final String? randomizationNumber;
  final String? randomizationArm;
  final PatientStatus status;
  final DateTime? exitDate;
  final String? exitReason;
  final DateTime? createdAt;

  Patient({
    this.id,
    this.studyId,
    required this.patientNumber,
    this.initials,
    this.birthDate,
    this.siteId,
    this.screeningDate,
    this.inclusionDate,
    this.randomizationNumber,
    this.randomizationArm,
    this.status = PatientStatus.screening,
    this.exitDate,
    this.exitReason,
    this.createdAt,
  });

  factory Patient.fromMap(Map<String, dynamic> map) {
    return Patient(
      id: map['id'] as int?,
      studyId: map['study_id'] as int?,
      patientNumber: map['patient_number'] as String? ?? '',
      initials: map['initials'] as String?,
      birthDate: map['birth_date'] != null
          ? DateTime.tryParse(map['birth_date'].toString())
          : null,
      siteId: map['site_id'] as String?,
      screeningDate: map['screening_date'] != null
          ? DateTime.tryParse(map['screening_date'].toString())
          : null,
      inclusionDate: map['inclusion_date'] != null
          ? DateTime.tryParse(map['inclusion_date'].toString())
          : null,
      randomizationNumber: map['randomization_number'] as String?,
      randomizationArm: map['randomization_arm'] as String?,
      status: PatientStatusExtension.fromString(map['status'] as String?),
      exitDate: map['exit_date'] != null
          ? DateTime.tryParse(map['exit_date'].toString())
          : null,
      exitReason: map['exit_reason'] as String?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'study_id': studyId,
      'patient_number': patientNumber,
      'initials': initials,
      'birth_date': birthDate?.toIso8601String().split('T')[0],
      'site_id': siteId,
      'screening_date': screeningDate?.toIso8601String().split('T')[0],
      'inclusion_date': inclusionDate?.toIso8601String().split('T')[0],
      'randomization_number': randomizationNumber,
      'randomization_arm': randomizationArm,
      'status': status.label,
      'exit_date': exitDate?.toIso8601String().split('T')[0],
      'exit_reason': exitReason,
    };
  }

  Patient copyWith({
    int? id,
    int? studyId,
    String? patientNumber,
    String? initials,
    DateTime? birthDate,
    String? siteId,
    DateTime? screeningDate,
    DateTime? inclusionDate,
    PatientStatus? status,
  }) {
    return Patient(
      id: id ?? this.id,
      studyId: studyId ?? this.studyId,
      patientNumber: patientNumber ?? this.patientNumber,
      initials: initials ?? this.initials,
      birthDate: birthDate ?? this.birthDate,
      siteId: siteId ?? this.siteId,
      screeningDate: screeningDate ?? this.screeningDate,
      inclusionDate: inclusionDate ?? this.inclusionDate,
      status: status ?? this.status,
    );
  }
}

/// Donnees de demo
final List<Patient> demoPatients = [
  Patient(
    id: 1,
    studyId: 1,
    patientNumber: '001-001',
    initials: 'JD',
    siteId: '001',
    screeningDate: DateTime(2026, 2, 1),
    inclusionDate: DateTime(2026, 2, 15),
    status: PatientStatus.included,
  ),
  Patient(
    id: 2,
    studyId: 1,
    patientNumber: '001-002',
    initials: 'ML',
    siteId: '001',
    screeningDate: DateTime(2026, 2, 5),
    inclusionDate: DateTime(2026, 2, 20),
    status: PatientStatus.included,
  ),
  Patient(
    id: 3,
    studyId: 1,
    patientNumber: '002-001',
    initials: 'PB',
    siteId: '002',
    screeningDate: DateTime(2026, 2, 20),
    status: PatientStatus.screening,
  ),
  Patient(
    id: 4,
    studyId: 1,
    patientNumber: '001-003',
    initials: 'AC',
    siteId: '001',
    screeningDate: DateTime(2026, 1, 15),
    status: PatientStatus.screenFailure,
  ),
  Patient(
    id: 5,
    studyId: 1,
    patientNumber: '003-001',
    initials: 'RD',
    siteId: '003',
    screeningDate: DateTime(2026, 2, 10),
    inclusionDate: DateTime(2026, 2, 25),
    exitDate: DateTime(2026, 3, 15),
    status: PatientStatus.completed,
  ),
  Patient(
    id: 6,
    studyId: 1,
    patientNumber: '002-002',
    initials: 'SG',
    siteId: '002',
    screeningDate: DateTime(2026, 2, 22),
    inclusionDate: DateTime(2026, 3, 1),
    exitDate: DateTime(2026, 3, 10),
    exitReason: 'Consent withdrawn',
    status: PatientStatus.withdrawn,
  ),
];
