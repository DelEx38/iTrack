/// Sévérité d'un événement indésirable
enum AESeverity { mild, moderate, severe }

extension AESeverityExtension on AESeverity {
  String get label {
    switch (this) {
      case AESeverity.mild: return 'Mild';
      case AESeverity.moderate: return 'Moderate';
      case AESeverity.severe: return 'Severe';
    }
  }

  int get color {
    switch (this) {
      case AESeverity.mild: return 0xFF4CAF50;
      case AESeverity.moderate: return 0xFFFF9800;
      case AESeverity.severe: return 0xFFF44336;
    }
  }

  static AESeverity fromString(String? value) {
    switch (value) {
      case 'Moderate': return AESeverity.moderate;
      case 'Severe': return AESeverity.severe;
      default: return AESeverity.mild;
    }
  }
}

/// Outcome d'un événement indésirable
enum AEOutcome { ongoing, recovered, recoveredWithSequelae, notRecovered, fatal, unknown }

extension AEOutcomeExtension on AEOutcome {
  String get label {
    switch (this) {
      case AEOutcome.ongoing: return 'Ongoing';
      case AEOutcome.recovered: return 'Recovered';
      case AEOutcome.recoveredWithSequelae: return 'Recovered w/ Sequelae';
      case AEOutcome.notRecovered: return 'Not Recovered';
      case AEOutcome.fatal: return 'Fatal';
      case AEOutcome.unknown: return 'Unknown';
    }
  }

  int get color {
    switch (this) {
      case AEOutcome.ongoing: return 0xFF2196F3;
      case AEOutcome.recovered: return 0xFF4CAF50;
      case AEOutcome.recoveredWithSequelae: return 0xFF8BC34A;
      case AEOutcome.notRecovered: return 0xFFFF9800;
      case AEOutcome.fatal: return 0xFFF44336;
      case AEOutcome.unknown: return 0xFF9E9E9E;
    }
  }

  static AEOutcome fromString(String? value) {
    switch (value) {
      case 'Recovered': return AEOutcome.recovered;
      case 'Recovered w/ Sequelae': return AEOutcome.recoveredWithSequelae;
      case 'Not Recovered': return AEOutcome.notRecovered;
      case 'Fatal': return AEOutcome.fatal;
      case 'Unknown': return AEOutcome.unknown;
      default: return AEOutcome.ongoing;
    }
  }
}

/// Causalité
enum AECausality { notRelated, unlikely, possible, probable, definite }

extension AECausalityExtension on AECausality {
  String get label {
    switch (this) {
      case AECausality.notRelated: return 'Not Related';
      case AECausality.unlikely: return 'Unlikely';
      case AECausality.possible: return 'Possible';
      case AECausality.probable: return 'Probable';
      case AECausality.definite: return 'Definite';
    }
  }

  static AECausality fromString(String? value) {
    switch (value) {
      case 'Unlikely': return AECausality.unlikely;
      case 'Possible': return AECausality.possible;
      case 'Probable': return AECausality.probable;
      case 'Definite': return AECausality.definite;
      default: return AECausality.notRelated;
    }
  }
}

/// Événement indésirable
class AdverseEvent {
  final int? id;
  final int? patientId;
  final String? patientNumber;
  final String description;
  final DateTime onsetDate;
  final DateTime? endDate;
  final AESeverity severity;
  final bool isSAE;
  final DateTime? reportingDate;
  final AEOutcome outcome;
  final AECausality causality;
  final String? action;
  final String? comments;
  final DateTime? createdAt;

  AdverseEvent({
    this.id,
    this.patientId,
    this.patientNumber,
    required this.description,
    required this.onsetDate,
    this.endDate,
    this.severity = AESeverity.mild,
    this.isSAE = false,
    this.reportingDate,
    this.outcome = AEOutcome.ongoing,
    this.causality = AECausality.notRelated,
    this.action,
    this.comments,
    this.createdAt,
  });

  /// Délai de déclaration SAE (< 24h = ok, sinon retard)
  int? get saeDelayHours {
    if (!isSAE || reportingDate == null) return null;
    return reportingDate!.difference(onsetDate).inHours;
  }

  bool get saeOnTime => saeDelayHours != null && saeDelayHours! <= 24;

  factory AdverseEvent.fromMap(Map<String, dynamic> map) {
    return AdverseEvent(
      id: map['id'] as int?,
      patientId: map['patient_id'] as int?,
      patientNumber: map['patient_number'] as String?,
      description: map['description'] as String? ?? '',
      onsetDate: DateTime.tryParse(map['onset_date']?.toString() ?? '') ?? DateTime.now(),
      endDate: map['end_date'] != null ? DateTime.tryParse(map['end_date'].toString()) : null,
      severity: AESeverityExtension.fromString(map['severity'] as String?),
      isSAE: map['is_sae'] == 1 || map['is_sae'] == true,
      reportingDate: map['reporting_date'] != null
          ? DateTime.tryParse(map['reporting_date'].toString())
          : null,
      outcome: AEOutcomeExtension.fromString(map['outcome'] as String?),
      causality: AECausalityExtension.fromString(map['causality'] as String?),
      action: map['action'] as String?,
      comments: map['comments'] as String?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'patient_id': patientId,
      'description': description,
      'onset_date': onsetDate.toIso8601String().split('T')[0],
      'end_date': endDate?.toIso8601String().split('T')[0],
      'severity': severity.label,
      'is_sae': isSAE ? 1 : 0,
      'reporting_date': reportingDate?.toIso8601String().split('T')[0],
      'outcome': outcome.label,
      'causality': causality.label,
      'action': action,
      'comments': comments,
    };
  }
}

/// Données de démo
final List<AdverseEvent> demoAdverseEvents = [
  AdverseEvent(
    id: 1,
    patientId: 1,
    patientNumber: '001-001',
    description: 'Headache',
    onsetDate: DateTime(2026, 2, 20),
    endDate: DateTime(2026, 2, 22),
    severity: AESeverity.mild,
    outcome: AEOutcome.recovered,
    causality: AECausality.possible,
  ),
  AdverseEvent(
    id: 2,
    patientId: 1,
    patientNumber: '001-001',
    description: 'Nausea',
    onsetDate: DateTime(2026, 3, 1),
    severity: AESeverity.moderate,
    outcome: AEOutcome.ongoing,
    causality: AECausality.probable,
  ),
  AdverseEvent(
    id: 3,
    patientId: 2,
    patientNumber: '001-002',
    description: 'Severe allergic reaction',
    onsetDate: DateTime(2026, 3, 5),
    endDate: DateTime(2026, 3, 7),
    severity: AESeverity.severe,
    isSAE: true,
    reportingDate: DateTime(2026, 3, 5),
    outcome: AEOutcome.recovered,
    causality: AECausality.definite,
    action: 'Treatment discontinued',
  ),
  AdverseEvent(
    id: 4,
    patientId: 5,
    patientNumber: '003-001',
    description: 'Fatigue',
    onsetDate: DateTime(2026, 3, 10),
    severity: AESeverity.mild,
    outcome: AEOutcome.ongoing,
    causality: AECausality.unlikely,
  ),
  AdverseEvent(
    id: 5,
    patientId: 6,
    patientNumber: '002-002',
    description: 'Hospitalization - cardiac event',
    onsetDate: DateTime(2026, 3, 8),
    severity: AESeverity.severe,
    isSAE: true,
    reportingDate: DateTime(2026, 3, 10), // Retard > 24h
    outcome: AEOutcome.notRecovered,
    causality: AECausality.possible,
    action: 'Patient withdrawn',
  ),
];
