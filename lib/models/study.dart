/// Modèle d'étude clinique
class Study {
  final int? id;
  final String studyNumber;
  final String? studyName;
  final String? euCtNumber;
  final String? nctNumber;
  final String? phase;
  final String? investigationalProduct;
  final String? comparator;
  final String? pathology;
  final String? studyTitle;
  final String? sponsor;
  final String status;
  final DateTime? createdAt;

  // Stats (calculées)
  int patientCount;
  int siteCount;
  int aeCount;

  Study({
    this.id,
    required this.studyNumber,
    this.studyName,
    this.euCtNumber,
    this.nctNumber,
    this.phase,
    this.investigationalProduct,
    this.comparator,
    this.pathology,
    this.studyTitle,
    this.sponsor,
    this.status = 'Active',
    this.createdAt,
    this.patientCount = 0,
    this.siteCount = 0,
    this.aeCount = 0,
  });

  /// Couleur selon la phase
  static const Map<String, int> phaseColors = {
    'I': 0xFF2196F3,
    'II': 0xFF4CAF50,
    'III': 0xFFFF9800,
    'IV': 0xFFF44336,
  };

  int get phaseColor => phaseColors[phase] ?? 0xFF9E9E9E;

  // Alias pour compatibilité
  String get number => studyNumber;
  String get name => studyName ?? studyNumber;

  factory Study.fromMap(Map<String, dynamic> map) {
    return Study(
      id: map['id'] as int?,
      studyNumber: map['study_number'] as String? ?? '',
      studyName: map['study_name'] as String?,
      euCtNumber: map['eu_ct_number'] as String?,
      nctNumber: map['nct_number'] as String?,
      phase: map['phase'] as String?,
      investigationalProduct: map['investigational_product'] as String?,
      comparator: map['comparator'] as String?,
      pathology: map['pathology'] as String?,
      studyTitle: map['study_title'] as String?,
      sponsor: map['sponsor'] as String?,
      status: map['status'] as String? ?? 'Active',
    );
  }

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'study_number': studyNumber,
      'study_name': studyName,
      'eu_ct_number': euCtNumber,
      'nct_number': nctNumber,
      'phase': phase,
      'investigational_product': investigationalProduct,
      'comparator': comparator,
      'pathology': pathology,
      'study_title': studyTitle,
      'sponsor': sponsor,
      'status': status,
    };
  }

  Study copyWith({
    int? id,
    String? studyNumber,
    String? studyName,
    String? phase,
    String? pathology,
    String? sponsor,
    String? status,
  }) {
    return Study(
      id: id ?? this.id,
      studyNumber: studyNumber ?? this.studyNumber,
      studyName: studyName ?? this.studyName,
      phase: phase ?? this.phase,
      pathology: pathology ?? this.pathology,
      sponsor: sponsor ?? this.sponsor,
      status: status ?? this.status,
      patientCount: patientCount,
      siteCount: siteCount,
      aeCount: aeCount,
    );
  }
}

/// Données de démo
final List<Study> demoStudies = [
  Study(
    id: 1,
    studyNumber: 'ABC-001',
    studyName: 'SUNRISE',
    phase: 'III',
    sponsor: 'Pharma Corp',
    pathology: 'Oncology',
    patientCount: 45,
    siteCount: 8,
  ),
  Study(
    id: 2,
    studyNumber: 'XYZ-042',
    studyName: 'MOONLIGHT',
    phase: 'II',
    sponsor: 'BioTech Inc',
    pathology: 'Cardiology',
    patientCount: 23,
    siteCount: 5,
  ),
  Study(
    id: 3,
    studyNumber: 'DEF-103',
    studyName: 'STELLAR',
    phase: 'I',
    sponsor: 'MedResearch',
    pathology: 'Neurology',
    patientCount: 12,
    siteCount: 3,
  ),
];
