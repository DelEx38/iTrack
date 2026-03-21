/// Configuration d'une visite (fenêtre de visite)
class VisitConfig {
  final int visitNumber;
  final String visitName;
  final int targetDay;
  final int windowBefore;
  final int windowAfter;

  const VisitConfig({
    required this.visitNumber,
    required this.visitName,
    required this.targetDay,
    this.windowBefore = 0,
    this.windowAfter = 0,
  });

  /// V1 est la visite de référence (pas de fenêtre)
  bool get isReference => visitNumber == 1;
}

/// Statut d'une visite
enum VisitStatus { pending, completed, missed }

extension VisitStatusExtension on VisitStatus {
  String get label {
    switch (this) {
      case VisitStatus.pending: return 'Pending';
      case VisitStatus.completed: return 'Completed';
      case VisitStatus.missed: return 'Missed';
    }
  }

  int get color {
    switch (this) {
      case VisitStatus.pending: return 0xFF9E9E9E;
      case VisitStatus.completed: return 0xFF4CAF50;
      case VisitStatus.missed: return 0xFFF44336;
    }
  }
}

/// Enregistrement d'une visite pour un patient
class Visit {
  final int? id;
  final int? patientId;
  final int visitNumber;
  final DateTime? visitDate;
  final VisitStatus status;
  final String? comments;
  final bool? inWindow;
  final int? daysDelta;

  Visit({
    this.id,
    this.patientId,
    required this.visitNumber,
    this.visitDate,
    this.status = VisitStatus.pending,
    this.comments,
    this.inWindow,
    this.daysDelta,
  });

  factory Visit.fromMap(Map<String, dynamic> map) {
    return Visit(
      id: map['id'] as int?,
      patientId: map['patient_id'] as int?,
      visitNumber: map['visit_number'] as int? ?? 1,
      visitDate: map['visit_date'] != null
          ? DateTime.tryParse(map['visit_date'].toString())
          : null,
      status: _statusFromString(map['status'] as String?),
      comments: map['comments'] as String?,
      inWindow: map['in_window'] == 1,
      daysDelta: map['days_delta'] as int?,
    );
  }

  static VisitStatus _statusFromString(String? value) {
    switch (value) {
      case 'Completed': return VisitStatus.completed;
      case 'Missed': return VisitStatus.missed;
      default: return VisitStatus.pending;
    }
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'patient_id': patientId,
      'visit_number': visitNumber,
      'visit_date': visitDate?.toIso8601String().split('T')[0],
      'status': status.label,
      'comments': comments,
      'in_window': inWindow == true ? 1 : 0,
      'days_delta': daysDelta,
    };
  }

  Visit copyWith({
    int? id,
    int? patientId,
    int? visitNumber,
    DateTime? visitDate,
    VisitStatus? status,
    String? comments,
    bool? inWindow,
    int? daysDelta,
  }) {
    return Visit(
      id: id ?? this.id,
      patientId: patientId ?? this.patientId,
      visitNumber: visitNumber ?? this.visitNumber,
      visitDate: visitDate ?? this.visitDate,
      status: status ?? this.status,
      comments: comments ?? this.comments,
      inWindow: inWindow ?? this.inWindow,
      daysDelta: daysDelta ?? this.daysDelta,
    );
  }
}

/// Configuration par défaut des 25 visites
final List<VisitConfig> defaultVisitConfigs = [
  const VisitConfig(visitNumber: 1, visitName: 'V1', targetDay: 0), // Référence
  const VisitConfig(visitNumber: 2, visitName: 'V2', targetDay: 7, windowBefore: 2, windowAfter: 2),
  const VisitConfig(visitNumber: 3, visitName: 'V3', targetDay: 14, windowBefore: 3, windowAfter: 3),
  const VisitConfig(visitNumber: 4, visitName: 'V4', targetDay: 28, windowBefore: 3, windowAfter: 3),
  const VisitConfig(visitNumber: 5, visitName: 'V5', targetDay: 42, windowBefore: 5, windowAfter: 5),
  const VisitConfig(visitNumber: 6, visitName: 'V6', targetDay: 56, windowBefore: 5, windowAfter: 5),
  const VisitConfig(visitNumber: 7, visitName: 'V7', targetDay: 84, windowBefore: 7, windowAfter: 7),
  const VisitConfig(visitNumber: 8, visitName: 'V8', targetDay: 112, windowBefore: 7, windowAfter: 7),
  const VisitConfig(visitNumber: 9, visitName: 'V9', targetDay: 140, windowBefore: 7, windowAfter: 7),
  const VisitConfig(visitNumber: 10, visitName: 'V10', targetDay: 168, windowBefore: 7, windowAfter: 7),
];

/// Données de démo pour les visites
final List<Visit> demoVisits = [
  // Patient 001-001 (id: 1) - V1 le 15/02/2026
  Visit(id: 1, patientId: 1, visitNumber: 1, visitDate: DateTime(2026, 2, 15), status: VisitStatus.completed, inWindow: true),
  Visit(id: 2, patientId: 1, visitNumber: 2, visitDate: DateTime(2026, 2, 22), status: VisitStatus.completed, inWindow: true, daysDelta: 0),
  Visit(id: 3, patientId: 1, visitNumber: 3, visitDate: DateTime(2026, 3, 2), status: VisitStatus.completed, inWindow: true, daysDelta: 1),
  Visit(id: 4, patientId: 1, visitNumber: 4, visitDate: DateTime(2026, 3, 18), status: VisitStatus.completed, inWindow: false, daysDelta: -3),
  Visit(id: 5, patientId: 1, visitNumber: 5, status: VisitStatus.pending),
  // Patient 001-002 (id: 2) - V1 le 20/02/2026
  Visit(id: 6, patientId: 2, visitNumber: 1, visitDate: DateTime(2026, 2, 20), status: VisitStatus.completed, inWindow: true),
  Visit(id: 7, patientId: 2, visitNumber: 2, visitDate: DateTime(2026, 2, 27), status: VisitStatus.completed, inWindow: true, daysDelta: 0),
  Visit(id: 8, patientId: 2, visitNumber: 3, visitDate: DateTime(2026, 3, 10), status: VisitStatus.completed, inWindow: false, daysDelta: 4),
  Visit(id: 9, patientId: 2, visitNumber: 4, status: VisitStatus.pending),
  // Patient 002-001 (id: 3) - screening seulement
  Visit(id: 10, patientId: 3, visitNumber: 1, status: VisitStatus.pending),
];
