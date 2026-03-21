/// Statut d'une query
enum QueryStatus { open, answered, closed }

extension QueryStatusExtension on QueryStatus {
  String get label {
    switch (this) {
      case QueryStatus.open: return 'Open';
      case QueryStatus.answered: return 'Answered';
      case QueryStatus.closed: return 'Closed';
    }
  }

  int get color {
    switch (this) {
      case QueryStatus.open: return 0xFFF44336;
      case QueryStatus.answered: return 0xFFFF9800;
      case QueryStatus.closed: return 0xFF4CAF50;
    }
  }

  static QueryStatus fromString(String? value) {
    switch (value) {
      case 'Answered': return QueryStatus.answered;
      case 'Closed': return QueryStatus.closed;
      default: return QueryStatus.open;
    }
  }
}

/// Catégorie de query
enum QueryCategory { dataEntry, protocol, safety, documentation, other }

extension QueryCategoryExtension on QueryCategory {
  String get label {
    switch (this) {
      case QueryCategory.dataEntry: return 'Data Entry';
      case QueryCategory.protocol: return 'Protocol';
      case QueryCategory.safety: return 'Safety';
      case QueryCategory.documentation: return 'Documentation';
      case QueryCategory.other: return 'Other';
    }
  }

  static QueryCategory fromString(String? value) {
    switch (value) {
      case 'Protocol': return QueryCategory.protocol;
      case 'Safety': return QueryCategory.safety;
      case 'Documentation': return QueryCategory.documentation;
      case 'Other': return QueryCategory.other;
      default: return QueryCategory.dataEntry;
    }
  }
}

/// Query de data management
class Query {
  final int? id;
  final int? patientId;
  final String? patientNumber;
  final String? visitName;
  final String? fieldName;
  final String description;
  final QueryCategory category;
  final QueryStatus status;
  final DateTime openDate;
  final DateTime? answerDate;
  final DateTime? closeDate;
  final String? answer;
  final String? comments;

  Query({
    this.id,
    this.patientId,
    this.patientNumber,
    this.visitName,
    this.fieldName,
    required this.description,
    this.category = QueryCategory.dataEntry,
    this.status = QueryStatus.open,
    required this.openDate,
    this.answerDate,
    this.closeDate,
    this.answer,
    this.comments,
  });

  /// Âge de la query en jours
  int get ageInDays {
    final endDate = closeDate ?? DateTime.now();
    return endDate.difference(openDate).inDays;
  }

  /// Query en retard (> 7 jours et encore ouverte)
  bool get isOverdue => status != QueryStatus.closed && ageInDays > 7;

  factory Query.fromMap(Map<String, dynamic> map) {
    return Query(
      id: map['id'] as int?,
      patientId: map['patient_id'] as int?,
      patientNumber: map['patient_number'] as String?,
      visitName: map['visit_name'] as String?,
      fieldName: map['field_name'] as String?,
      description: map['description'] as String? ?? '',
      category: QueryCategoryExtension.fromString(map['category'] as String?),
      status: QueryStatusExtension.fromString(map['status'] as String?),
      openDate: DateTime.tryParse(map['open_date']?.toString() ?? '') ?? DateTime.now(),
      answerDate: map['answer_date'] != null
          ? DateTime.tryParse(map['answer_date'].toString())
          : null,
      closeDate: map['close_date'] != null
          ? DateTime.tryParse(map['close_date'].toString())
          : null,
      answer: map['answer'] as String?,
      comments: map['comments'] as String?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'patient_id': patientId,
      'visit_name': visitName,
      'field_name': fieldName,
      'description': description,
      'category': category.label,
      'status': status.label,
      'open_date': openDate.toIso8601String().split('T')[0],
      'answer_date': answerDate?.toIso8601String().split('T')[0],
      'close_date': closeDate?.toIso8601String().split('T')[0],
      'answer': answer,
      'comments': comments,
    };
  }
}

/// Données de démo
final List<Query> demoQueries = [
  Query(
    id: 1,
    patientId: 1,
    patientNumber: '001-001',
    visitName: 'V2',
    fieldName: 'Weight',
    description: 'Value out of range (120kg). Please verify.',
    category: QueryCategory.dataEntry,
    status: QueryStatus.open,
    openDate: DateTime(2026, 3, 1),
  ),
  Query(
    id: 2,
    patientId: 1,
    patientNumber: '001-001',
    visitName: 'V3',
    fieldName: 'AE Start Date',
    description: 'AE start date before screening date. Please correct.',
    category: QueryCategory.safety,
    status: QueryStatus.answered,
    openDate: DateTime(2026, 3, 5),
    answerDate: DateTime(2026, 3, 7),
    answer: 'Date corrected to 01-Mar-2026',
  ),
  Query(
    id: 3,
    patientId: 2,
    patientNumber: '001-002',
    visitName: 'V1',
    fieldName: 'Informed Consent',
    description: 'ICF version not matching protocol version. Please update.',
    category: QueryCategory.documentation,
    status: QueryStatus.closed,
    openDate: DateTime(2026, 2, 25),
    answerDate: DateTime(2026, 2, 26),
    closeDate: DateTime(2026, 2, 27),
    answer: 'Re-consent obtained with correct version',
  ),
  Query(
    id: 4,
    patientId: 3,
    patientNumber: '002-001',
    visitName: 'Screening',
    fieldName: 'Inclusion Criteria',
    description: 'Missing documentation for inclusion criterion #3.',
    category: QueryCategory.protocol,
    status: QueryStatus.open,
    openDate: DateTime(2026, 3, 10),
  ),
  Query(
    id: 5,
    patientId: 5,
    patientNumber: '003-001',
    visitName: 'V4',
    fieldName: 'Lab Results',
    description: 'Lab sample date missing. Please provide.',
    category: QueryCategory.dataEntry,
    status: QueryStatus.open,
    openDate: DateTime(2026, 3, 1), // > 7 jours = overdue
  ),
];
