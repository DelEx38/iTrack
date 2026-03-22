import 'dart:typed_data';
import 'package:archive/archive.dart';
import 'package:xml/xml.dart';
import '../models/visit.dart';

/// Résultat du parsing d'un Schedule of Assessments
class SoaParseResult {
  final List<VisitConfig> visits;
  final List<String> procedures;
  final Map<String, List<bool>> procedureMatrix; // procedure -> [hasV1, hasV2, ...]
  final String? error;

  SoaParseResult({
    this.visits = const [],
    this.procedures = const [],
    this.procedureMatrix = const {},
    this.error,
  });

  bool get success => error == null && visits.isNotEmpty;
}

/// Service pour parser un Schedule of Assessments depuis Word (.docx)
class SoaParserService {
  /// Parse un fichier .docx et extrait les configurations de visites
  static Future<SoaParseResult> parseDocx(Uint8List bytes) async {
    try {
      // Dézipper le .docx
      final archive = ZipDecoder().decodeBytes(bytes);

      // Trouver document.xml (contenu principal)
      final documentFile = archive.files.firstWhere(
        (f) => f.name == 'word/document.xml',
        orElse: () => throw Exception('Invalid .docx file: document.xml not found'),
      );

      final xmlContent = String.fromCharCodes(documentFile.content as List<int>);
      final document = XmlDocument.parse(xmlContent);

      // Extraire tous les tableaux
      final tables = _extractTables(document);

      if (tables.isEmpty) {
        return SoaParseResult(error: 'No tables found in document');
      }

      // Chercher le tableau SoA (celui avec "Day" ou "Window" ou des noms de visites V1, V2...)
      for (final table in tables) {
        final result = _parseSoaTable(table);
        if (result.success) {
          return result;
        }
      }

      return SoaParseResult(error: 'No Schedule of Assessments table found');
    } catch (e) {
      return SoaParseResult(error: 'Parse error: $e');
    }
  }

  /// Extrait tous les tableaux du document XML
  static List<List<List<String>>> _extractTables(XmlDocument document) {
    final tables = <List<List<String>>>[];
    final nsW = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main';

    // Trouver tous les éléments <w:tbl>
    final tblElements = document.findAllElements('tbl', namespace: nsW);

    for (final tbl in tblElements) {
      final rows = <List<String>>[];

      // Parcourir les lignes <w:tr>
      for (final tr in tbl.findAllElements('tr', namespace: nsW)) {
        final cells = <String>[];

        // Parcourir les cellules <w:tc>
        for (final tc in tr.findAllElements('tc', namespace: nsW)) {
          // Extraire le texte de toutes les balises <w:t>
          final textElements = tc.findAllElements('t', namespace: nsW);
          final cellText = textElements.map((t) => t.innerText).join(' ').trim();
          cells.add(cellText);
        }

        if (cells.isNotEmpty) {
          rows.add(cells);
        }
      }

      if (rows.isNotEmpty) {
        tables.add(rows);
      }
    }

    return tables;
  }

  /// Tente de parser un tableau comme SoA
  static SoaParseResult _parseSoaTable(List<List<String>> table) {
    if (table.length < 2) {
      return SoaParseResult(error: 'Table too small');
    }

    // Chercher la ligne d'en-tête avec les visites (V1, V2, Visit 1, etc.)
    int headerRow = -1;
    int dayRow = -1;
    int windowRow = -1;

    for (var i = 0; i < table.length && i < 10; i++) {
      final row = table[i];
      final rowText = row.join(' ').toLowerCase();

      // Détecter ligne des visites
      if (_isVisitHeader(row)) {
        headerRow = i;
      }

      // Détecter ligne Day
      if (rowText.contains('day') || rowText.contains('jour') ||
          row.any((c) => RegExp(r'^[dj]\s*-?\d+').hasMatch(c.toLowerCase()))) {
        if (row.any((c) => RegExp(r'\d+').hasMatch(c))) {
          dayRow = i;
        }
      }

      // Détecter ligne Window
      if (rowText.contains('window') || rowText.contains('fenêtre') || rowText.contains('±') ||
          row.any((c) => c.contains('±') || RegExp(r'[+-]\s*\d+').hasMatch(c))) {
        windowRow = i;
      }
    }

    // Si pas de header explicite, utiliser la première ligne
    if (headerRow == -1) headerRow = 0;

    // Si pas de ligne Day trouvée, chercher dans header
    if (dayRow == -1) {
      // Peut-être que les jours sont dans l'en-tête (ex: "V1 D0", "V2 D7±2")
      final headerWithDays = _parseVisitsFromHeader(table[headerRow]);
      if (headerWithDays.isNotEmpty) {
        return SoaParseResult(
          visits: headerWithDays,
          procedures: _extractProcedures(table, headerRow + 1),
          procedureMatrix: _buildProcedureMatrix(table, headerRow),
        );
      }
      return SoaParseResult(error: 'Could not find Day row');
    }

    // Extraire les visites
    final visits = _parseVisits(
      table[headerRow],
      table[dayRow],
      windowRow >= 0 ? table[windowRow] : null,
    );

    if (visits.isEmpty) {
      return SoaParseResult(error: 'Could not parse visits');
    }

    // Extraire les procédures (lignes après Day/Window)
    final procedureStartRow = (windowRow >= 0 ? windowRow : dayRow) + 1;
    final procedures = _extractProcedures(table, procedureStartRow);

    return SoaParseResult(
      visits: visits,
      procedures: procedures,
      procedureMatrix: _buildProcedureMatrix(table, headerRow),
    );
  }

  /// Vérifie si une ligne contient des noms de visites
  static bool _isVisitHeader(List<String> row) {
    int visitCount = 0;
    for (final cell in row) {
      final lower = cell.toLowerCase().trim();
      if (RegExp(r'^v\d+').hasMatch(lower) ||
          RegExp(r'^visit\s*\d+').hasMatch(lower) ||
          RegExp(r'^visite\s*\d+').hasMatch(lower) ||
          lower == 'screening' ||
          lower == 'baseline' ||
          lower.contains('inclusion') ||
          lower.contains('randomization') ||
          lower.contains('end of') ||
          lower.contains('follow')) {
        visitCount++;
      }
    }
    return visitCount >= 2;
  }

  /// Parse les visites depuis header + day + window rows
  static List<VisitConfig> _parseVisits(
    List<String> headerRow,
    List<String> dayRow,
    List<String>? windowRow,
  ) {
    final visits = <VisitConfig>[];

    // Trouver la première colonne de visite (skip la colonne "Assessment" ou vide)
    int startCol = 0;
    for (var i = 0; i < headerRow.length; i++) {
      if (_isVisitName(headerRow[i])) {
        startCol = i;
        break;
      }
    }

    int visitNumber = 1;
    for (var i = startCol; i < headerRow.length; i++) {
      final visitName = headerRow[i].trim();
      if (visitName.isEmpty) continue;

      // Parser le jour
      int targetDay = 0;
      if (i < dayRow.length) {
        targetDay = _parseDay(dayRow[i]);
      }

      // Parser la fenêtre
      int windowBefore = 0;
      int windowAfter = 0;
      if (windowRow != null && i < windowRow.length) {
        final window = _parseWindow(windowRow[i]);
        windowBefore = window['before'] ?? 0;
        windowAfter = window['after'] ?? 0;
      }

      visits.add(VisitConfig(
        visitNumber: visitNumber,
        visitName: _cleanVisitName(visitName),
        targetDay: targetDay,
        windowBefore: windowBefore,
        windowAfter: windowAfter,
      ));

      visitNumber++;
    }

    return visits;
  }

  /// Parse les visites depuis un header qui contient tout (ex: "V1 D0", "V2 D7±2")
  static List<VisitConfig> _parseVisitsFromHeader(List<String> headerRow) {
    final visits = <VisitConfig>[];
    int visitNumber = 1;

    for (final cell in headerRow) {
      if (cell.isEmpty) continue;

      // Pattern: "V1 D0", "V2 D7±2", "V3 (Day 14 ±3)"
      final dayMatch = RegExp(r'[dj]\s*(-?\d+)', caseSensitive: false).firstMatch(cell);
      if (dayMatch != null) {
        final targetDay = int.tryParse(dayMatch.group(1) ?? '0') ?? 0;
        final window = _parseWindow(cell);

        visits.add(VisitConfig(
          visitNumber: visitNumber,
          visitName: _cleanVisitName(cell.split(RegExp(r'[dj]\s*-?\d+', caseSensitive: false))[0]),
          targetDay: targetDay,
          windowBefore: window['before'] ?? 0,
          windowAfter: window['after'] ?? 0,
        ));

        visitNumber++;
      }
    }

    return visits;
  }

  static bool _isVisitName(String text) {
    final lower = text.toLowerCase().trim();
    return RegExp(r'^v\d+').hasMatch(lower) ||
        RegExp(r'^visit\s*\d+').hasMatch(lower) ||
        lower == 'screening' ||
        lower == 'baseline' ||
        lower.contains('inclusion');
  }

  static String _cleanVisitName(String name) {
    return name
        .replaceAll(RegExp(r'\s+'), ' ')
        .replaceAll(RegExp(r'[dj]\s*-?\d+.*', caseSensitive: false), '')
        .trim();
  }

  static int _parseDay(String text) {
    // Patterns: "0", "7", "D7", "Day 14", "-28", "D-1"
    final match = RegExp(r'(-?\d+)').firstMatch(text);
    if (match != null) {
      return int.tryParse(match.group(1) ?? '0') ?? 0;
    }
    return 0;
  }

  static Map<String, int> _parseWindow(String text) {
    int before = 0;
    int after = 0;

    // Pattern: "±3", "+/- 3", "± 3 days"
    final pmMatch = RegExp(r'[±]\s*(\d+)').firstMatch(text);
    if (pmMatch != null) {
      final val = int.tryParse(pmMatch.group(1) ?? '0') ?? 0;
      before = val;
      after = val;
      return {'before': before, 'after': after};
    }

    // Pattern: "-3/+5", "-3 to +5"
    final rangeMatch = RegExp(r'(-\d+)\s*[/to]+\s*\+?(\d+)').firstMatch(text);
    if (rangeMatch != null) {
      before = (int.tryParse(rangeMatch.group(1) ?? '0') ?? 0).abs();
      after = int.tryParse(rangeMatch.group(2) ?? '0') ?? 0;
      return {'before': before, 'after': after};
    }

    // Pattern: "+/- 2 days"
    final daysMatch = RegExp(r'\+\s*/\s*-\s*(\d+)').firstMatch(text);
    if (daysMatch != null) {
      final val = int.tryParse(daysMatch.group(1) ?? '0') ?? 0;
      before = val;
      after = val;
      return {'before': before, 'after': after};
    }

    return {'before': before, 'after': after};
  }

  static List<String> _extractProcedures(List<List<String>> table, int startRow) {
    final procedures = <String>[];
    for (var i = startRow; i < table.length; i++) {
      if (table[i].isNotEmpty) {
        final proc = table[i][0].trim();
        if (proc.isNotEmpty && !proc.toLowerCase().contains('note')) {
          procedures.add(proc);
        }
      }
    }
    return procedures;
  }

  static Map<String, List<bool>> _buildProcedureMatrix(List<List<String>> table, int headerRow) {
    // TODO: Implémenter si besoin d'afficher la matrice des procédures
    return {};
  }
}
