import 'dart:typed_data';
import 'package:excel/excel.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../models/adverse_event.dart';
import '../models/document.dart';
import '../models/query.dart';
import '../models/site.dart';
import 'database_service.dart';

/// Service d'export Excel pour les données d'étude
class ExcelExportService {
  static final _dateFormat = DateFormat('dd-MMM-yy', 'en_US');

  /// Exporte toutes les données d'une étude vers un fichier Excel
  static Future<Uint8List> exportStudy(Study study) async {
    final excel = Excel.createExcel();

    // Charger les données
    final patients = await DatabaseService.getPatients(study.id!);
    final sites = await DatabaseService.getStudySites(study.id!);
    final adverseEvents = await DatabaseService.getAdverseEvents(study.id!);
    final queries = await DatabaseService.getQueries(study.id!);
    final consents = await DatabaseService.getPatientConsents(study.id!);

    // Créer les onglets
    _createSettingsSheet(excel, study);
    _createPatientsSheet(excel, patients);
    _createSitesSheet(excel, sites);
    _createAdverseEventsSheet(excel, adverseEvents);
    _createDocumentsSheet(excel, consents);
    _createQueriesSheet(excel, queries);
    _createDashboardSheet(excel, patients, adverseEvents, queries);

    // Supprimer la feuille par défaut
    excel.delete('Sheet1');

    return Uint8List.fromList(excel.encode()!);
  }

  /// Onglet Settings
  static void _createSettingsSheet(Excel excel, Study study) {
    final sheet = excel['Settings'];

    // En-têtes info étude
    _setHeader(sheet, 0, 0, 'Study Information');

    final studyInfo = [
      ['Study Number', study.studyNumber],
      ['Study Name', study.studyName ?? ''],
      ['Phase', study.phase ?? ''],
      ['Sponsor', study.sponsor ?? ''],
      ['Pathology', study.pathology ?? ''],
      ['Status', study.status],
    ];

    for (var i = 0; i < studyInfo.length; i++) {
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: i + 1)).value = TextCellValue(studyInfo[i][0]);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: i + 1)).value = TextCellValue(studyInfo[i][1]);
    }

    // Largeurs colonnes
    sheet.setColumnWidth(0, 20);
    sheet.setColumnWidth(1, 30);
  }

  /// Onglet Patients
  static void _createPatientsSheet(Excel excel, List<Patient> patients) {
    final sheet = excel['Patients'];

    // En-têtes
    final headers = [
      'Patient #', 'Initials', 'Site', 'Status', 'Screening Date',
      'Inclusion Date', 'Exit Date', 'Exit Reason'
    ];
    for (var i = 0; i < headers.length; i++) {
      _setHeader(sheet, i, 0, headers[i]);
    }

    // Données
    for (var row = 0; row < patients.length; row++) {
      final p = patients[row];
      final r = row + 1;

      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: r)).value = TextCellValue(p.patientNumber);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: r)).value = TextCellValue(p.initials ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 2, rowIndex: r)).value = TextCellValue(p.siteId ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 3, rowIndex: r)).value = TextCellValue(p.status.label);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 4, rowIndex: r)).value = TextCellValue(_formatDate(p.screeningDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 5, rowIndex: r)).value = TextCellValue(_formatDate(p.inclusionDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 6, rowIndex: r)).value = TextCellValue(_formatDate(p.exitDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 7, rowIndex: r)).value = TextCellValue(p.exitReason ?? '');
    }

    // Largeurs
    _setColumnWidths(sheet, [12, 10, 10, 12, 14, 14, 14, 25]);
  }

  /// Onglet Sites
  static void _createSitesSheet(Excel excel, List<StudySite> sites) {
    final sheet = excel['Sites'];

    final headers = [
      'Site #', 'Name', 'City', 'Country', 'PI', 'Status',
      'Activation', 'Target', 'Patients'
    ];
    for (var i = 0; i < headers.length; i++) {
      _setHeader(sheet, i, 0, headers[i]);
    }

    for (var row = 0; row < sites.length; row++) {
      final s = sites[row];
      final r = row + 1;

      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: r)).value = TextCellValue(s.siteNumber ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: r)).value = TextCellValue(s.siteName ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 2, rowIndex: r)).value = TextCellValue(s.city ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 3, rowIndex: r)).value = TextCellValue(s.country ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 4, rowIndex: r)).value = TextCellValue(s.principalInvestigator ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 5, rowIndex: r)).value = TextCellValue(s.status.label);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 6, rowIndex: r)).value = TextCellValue(_formatDate(s.activationDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 7, rowIndex: r)).value = IntCellValue(s.targetPatients);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 8, rowIndex: r)).value = IntCellValue(s.patientCount);
    }

    _setColumnWidths(sheet, [10, 20, 15, 12, 20, 12, 14, 10, 10]);
  }

  /// Onglet Adverse Events
  static void _createAdverseEventsSheet(Excel excel, List<AdverseEvent> events) {
    final sheet = excel['Adverse Events'];

    final headers = [
      'Patient #', 'Description', 'Onset Date', 'End Date', 'Severity',
      'SAE', 'Outcome', 'Causality', 'Action'
    ];
    for (var i = 0; i < headers.length; i++) {
      _setHeader(sheet, i, 0, headers[i]);
    }

    for (var row = 0; row < events.length; row++) {
      final ae = events[row];
      final r = row + 1;

      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: r)).value = TextCellValue(ae.patientNumber ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: r)).value = TextCellValue(ae.description);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 2, rowIndex: r)).value = TextCellValue(_formatDate(ae.onsetDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 3, rowIndex: r)).value = TextCellValue(_formatDate(ae.endDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 4, rowIndex: r)).value = TextCellValue(ae.severity.label);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 5, rowIndex: r)).value = TextCellValue(ae.isSAE ? 'Yes' : 'No');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 6, rowIndex: r)).value = TextCellValue(ae.outcome.label);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 7, rowIndex: r)).value = TextCellValue(ae.causality.label);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 8, rowIndex: r)).value = TextCellValue(ae.action ?? '');
    }

    _setColumnWidths(sheet, [12, 30, 14, 14, 12, 8, 15, 15, 20]);
  }

  /// Onglet Documents (Consents)
  static void _createDocumentsSheet(Excel excel, List<PatientConsent> consents) {
    final sheet = excel['Documents'];

    final headers = ['Patient #', 'Consent Type', 'Version', 'Signed Date', 'Status'];
    for (var i = 0; i < headers.length; i++) {
      _setHeader(sheet, i, 0, headers[i]);
    }

    for (var row = 0; row < consents.length; row++) {
      final c = consents[row];
      final r = row + 1;

      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: r)).value = TextCellValue(c.patientNumber ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: r)).value = TextCellValue(c.consentType);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 2, rowIndex: r)).value = TextCellValue(c.version ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 3, rowIndex: r)).value = TextCellValue(_formatDate(c.signedDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 4, rowIndex: r)).value = TextCellValue(c.status.label);
    }

    _setColumnWidths(sheet, [12, 20, 12, 14, 12]);
  }

  /// Onglet Queries
  static void _createQueriesSheet(Excel excel, List<Query> queries) {
    final sheet = excel['Queries'];

    final headers = [
      'Patient #', 'Visit', 'Field', 'Description', 'Category',
      'Status', 'Open Date', 'Answer Date', 'Close Date', 'Answer'
    ];
    for (var i = 0; i < headers.length; i++) {
      _setHeader(sheet, i, 0, headers[i]);
    }

    for (var row = 0; row < queries.length; row++) {
      final q = queries[row];
      final r = row + 1;

      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: r)).value = TextCellValue(q.patientNumber ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: r)).value = TextCellValue(q.visitName ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 2, rowIndex: r)).value = TextCellValue(q.fieldName ?? '');
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 3, rowIndex: r)).value = TextCellValue(q.description);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 4, rowIndex: r)).value = TextCellValue(q.category.label);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 5, rowIndex: r)).value = TextCellValue(q.status.label);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 6, rowIndex: r)).value = TextCellValue(_formatDate(q.openDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 7, rowIndex: r)).value = TextCellValue(_formatDate(q.answerDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 8, rowIndex: r)).value = TextCellValue(_formatDate(q.closeDate));
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 9, rowIndex: r)).value = TextCellValue(q.answer ?? '');
    }

    _setColumnWidths(sheet, [12, 10, 15, 30, 15, 12, 14, 14, 14, 30]);
  }

  /// Onglet Dashboard
  static void _createDashboardSheet(
    Excel excel,
    List<Patient> patients,
    List<AdverseEvent> events,
    List<Query> queries,
  ) {
    final sheet = excel['Dashboard'];

    // Section Recruitment
    _setHeader(sheet, 0, 0, 'RECRUITMENT');

    final screeningCount = patients.where((p) => p.status == PatientStatus.screening).length;
    final includedCount = patients.where((p) => p.status == PatientStatus.included).length;
    final completedCount = patients.where((p) => p.status == PatientStatus.completed).length;
    final withdrawnCount = patients.where((p) => p.status == PatientStatus.withdrawn).length;

    final recruitmentData = [
      ['Total Patients', patients.length],
      ['Screening', screeningCount],
      ['Included', includedCount],
      ['Completed', completedCount],
      ['Withdrawn', withdrawnCount],
    ];

    for (var i = 0; i < recruitmentData.length; i++) {
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: i + 1)).value = TextCellValue(recruitmentData[i][0] as String);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: i + 1)).value = IntCellValue(recruitmentData[i][1] as int);
    }

    // Section Safety
    _setHeader(sheet, 0, 7, 'SAFETY');

    final totalAE = events.length;
    final saeCount = events.where((ae) => ae.isSAE).length;
    final ongoingAE = events.where((ae) => ae.outcome == AEOutcome.ongoing).length;

    final safetyData = [
      ['Total AE', totalAE],
      ['Total SAE', saeCount],
      ['Ongoing AE', ongoingAE],
    ];

    for (var i = 0; i < safetyData.length; i++) {
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: i + 8)).value = TextCellValue(safetyData[i][0] as String);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: i + 8)).value = IntCellValue(safetyData[i][1] as int);
    }

    // Section Data Management
    _setHeader(sheet, 0, 12, 'DATA MANAGEMENT');

    final openQueries = queries.where((q) => q.status == QueryStatus.open).length;
    final closedQueries = queries.where((q) => q.status == QueryStatus.closed).length;

    final dmData = [
      ['Total Queries', queries.length],
      ['Open', openQueries],
      ['Closed', closedQueries],
    ];

    for (var i = 0; i < dmData.length; i++) {
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: i + 13)).value = TextCellValue(dmData[i][0] as String);
      sheet.cell(CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: i + 13)).value = IntCellValue(dmData[i][1] as int);
    }

    _setColumnWidths(sheet, [25, 12]);
  }

  // === Helpers ===

  static void _setHeader(Sheet sheet, int col, int row, String value) {
    final cell = sheet.cell(CellIndex.indexByColumnRow(columnIndex: col, rowIndex: row));
    cell.value = TextCellValue(value);
    cell.cellStyle = CellStyle(
      bold: true,
      backgroundColorHex: ExcelColor.fromHexString('#4472C4'),
      fontColorHex: ExcelColor.fromHexString('#FFFFFF'),
    );
  }

  static void _setColumnWidths(Sheet sheet, List<double> widths) {
    for (var i = 0; i < widths.length; i++) {
      sheet.setColumnWidth(i, widths[i]);
    }
  }

  static String _formatDate(DateTime? date) {
    if (date == null) return '';
    return _dateFormat.format(date);
  }
}
