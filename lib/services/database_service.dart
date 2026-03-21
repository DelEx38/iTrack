import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';
import 'package:path/path.dart';
import '../models/study.dart';
import '../models/site.dart';
import '../models/patient.dart';
import '../models/visit.dart';
import '../models/adverse_event.dart';
import '../models/document.dart';
import '../models/query.dart';

class DatabaseService {
  static Database? _database;
  static const String _dbName = 'clinical_study.db';
  static bool _initialized = false;

  static Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  static Future<Database> _initDatabase() async {
    if (!_initialized) {
      if (kIsWeb) {
        // Web platform: use IndexedDB via SharedWorker
        databaseFactory = databaseFactoryFfiWeb;
      } else {
        // Desktop/Mobile: use FFI
        sqfliteFfiInit();
        databaseFactory = databaseFactoryFfi;
      }
      _initialized = true;
    }

    final path = kIsWeb ? _dbName : join(await getDatabasesPath(), _dbName);

    return await openDatabase(
      path,
      version: 2,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  static Future<void> _onCreate(Database db, int version) async {
    // Studies
    await db.execute('''
      CREATE TABLE studies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_number TEXT NOT NULL,
        study_name TEXT,
        eu_ct_number TEXT,
        nct_number TEXT,
        phase TEXT,
        investigational_product TEXT,
        comparator TEXT,
        pathology TEXT,
        study_title TEXT,
        sponsor TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // Sites
    await db.execute('''
      CREATE TABLE sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_number TEXT NOT NULL UNIQUE,
        site_name TEXT,
        address TEXT,
        city TEXT,
        country TEXT,
        phone TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // Study-Sites relation
    await db.execute('''
      CREATE TABLE study_sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_id INTEGER NOT NULL,
        site_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Active',
        principal_investigator TEXT,
        activation_date DATE,
        first_patient_date DATE,
        target_patients INTEGER DEFAULT 0,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (study_id) REFERENCES studies(id) ON DELETE CASCADE,
        FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
        UNIQUE(study_id, site_id)
      )
    ''');

    // Patients
    await db.execute('''
      CREATE TABLE patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_id INTEGER,
        patient_number TEXT NOT NULL,
        initials TEXT,
        birth_date DATE,
        site_id TEXT,
        screening_date DATE,
        inclusion_date DATE,
        randomization_number TEXT,
        randomization_arm TEXT,
        status TEXT DEFAULT 'Screening',
        exit_date DATE,
        exit_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (study_id) REFERENCES studies(id),
        UNIQUE(study_id, patient_number)
      )
    ''');

    // Visit config
    await db.execute('''
      CREATE TABLE visit_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_id INTEGER NOT NULL,
        visit_number INTEGER NOT NULL,
        visit_name TEXT NOT NULL,
        target_day INTEGER DEFAULT 0,
        window_before INTEGER DEFAULT 0,
        window_after INTEGER DEFAULT 0,
        FOREIGN KEY (study_id) REFERENCES studies(id) ON DELETE CASCADE,
        UNIQUE(study_id, visit_number)
      )
    ''');

    // Visits
    await db.execute('''
      CREATE TABLE visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        visit_number INTEGER NOT NULL,
        visit_date DATE,
        status TEXT DEFAULT 'Pending',
        in_window INTEGER,
        days_delta INTEGER,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        UNIQUE(patient_id, visit_number)
      )
    ''');

    // Adverse events
    await db.execute('''
      CREATE TABLE adverse_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        onset_date DATE NOT NULL,
        end_date DATE,
        severity TEXT DEFAULT 'Mild',
        is_sae INTEGER DEFAULT 0,
        reporting_date DATE,
        outcome TEXT DEFAULT 'Ongoing',
        causality TEXT DEFAULT 'Not Related',
        action TEXT,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
      )
    ''');

    // Consent types
    await db.execute('''
      CREATE TABLE consent_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        FOREIGN KEY (study_id) REFERENCES studies(id) ON DELETE CASCADE
      )
    ''');

    // Consent versions
    await db.execute('''
      CREATE TABLE consent_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_id INTEGER NOT NULL,
        version TEXT NOT NULL,
        date DATE NOT NULL,
        is_current INTEGER DEFAULT 0,
        FOREIGN KEY (type_id) REFERENCES consent_types(id) ON DELETE CASCADE
      )
    ''');

    // Patient consents
    await db.execute('''
      CREATE TABLE patient_consents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        consent_type TEXT NOT NULL,
        version TEXT,
        signed_date DATE,
        status TEXT DEFAULT 'Missing',
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
      )
    ''');

    // Queries
    await db.execute('''
      CREATE TABLE queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        visit_name TEXT,
        field_name TEXT,
        description TEXT NOT NULL,
        category TEXT DEFAULT 'Data Entry',
        status TEXT DEFAULT 'Open',
        open_date DATE NOT NULL,
        answer_date DATE,
        close_date DATE,
        answer TEXT,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
      )
    ''');

    // Insert demo data
    await _insertDemoData(db);
  }

  static Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // Add new tables for version 2
      await db.execute('''
        CREATE TABLE IF NOT EXISTS visit_config (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          study_id INTEGER NOT NULL,
          visit_number INTEGER NOT NULL,
          visit_name TEXT NOT NULL,
          target_day INTEGER DEFAULT 0,
          window_before INTEGER DEFAULT 0,
          window_after INTEGER DEFAULT 0,
          FOREIGN KEY (study_id) REFERENCES studies(id) ON DELETE CASCADE,
          UNIQUE(study_id, visit_number)
        )
      ''');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS visits (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          patient_id INTEGER NOT NULL,
          visit_number INTEGER NOT NULL,
          visit_date DATE,
          status TEXT DEFAULT 'Pending',
          in_window INTEGER,
          days_delta INTEGER,
          comments TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
          UNIQUE(patient_id, visit_number)
        )
      ''');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS consent_types (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          study_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          code TEXT NOT NULL,
          FOREIGN KEY (study_id) REFERENCES studies(id) ON DELETE CASCADE
        )
      ''');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS consent_versions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          type_id INTEGER NOT NULL,
          version TEXT NOT NULL,
          date DATE NOT NULL,
          is_current INTEGER DEFAULT 0,
          FOREIGN KEY (type_id) REFERENCES consent_types(id) ON DELETE CASCADE
        )
      ''');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS patient_consents (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          patient_id INTEGER NOT NULL,
          consent_type TEXT NOT NULL,
          version TEXT,
          signed_date DATE,
          status TEXT DEFAULT 'Missing',
          FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        )
      ''');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS queries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          patient_id INTEGER NOT NULL,
          visit_name TEXT,
          field_name TEXT,
          description TEXT NOT NULL,
          category TEXT DEFAULT 'Data Entry',
          status TEXT DEFAULT 'Open',
          open_date DATE NOT NULL,
          answer_date DATE,
          close_date DATE,
          answer TEXT,
          comments TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        )
      ''');
    }
  }

  static Future<void> _insertDemoData(Database db) async {
    // Insert demo studies
    await db.insert('studies', {
      'study_number': 'ABC-001',
      'study_name': 'SUNRISE',
      'phase': 'III',
      'sponsor': 'Pharma Corp',
      'pathology': 'Oncology',
    });
    await db.insert('studies', {
      'study_number': 'XYZ-042',
      'study_name': 'MOONLIGHT',
      'phase': 'II',
      'sponsor': 'BioTech Inc',
      'pathology': 'Cardiology',
    });

    // Insert demo sites
    final site1Id = await db.insert('sites', {
      'site_number': '001',
      'site_name': 'CHU Paris',
      'city': 'Paris',
      'country': 'France',
    });
    final site2Id = await db.insert('sites', {
      'site_number': '002',
      'site_name': 'CHU Lyon',
      'city': 'Lyon',
      'country': 'France',
    });
    final site3Id = await db.insert('sites', {
      'site_number': '003',
      'site_name': 'CHU Marseille',
      'city': 'Marseille',
      'country': 'France',
    });

    // Link sites to study 1
    await db.insert('study_sites', {
      'study_id': 1,
      'site_id': site1Id,
      'status': 'Active',
      'principal_investigator': 'Dr. Martin',
      'target_patients': 20,
    });
    await db.insert('study_sites', {
      'study_id': 1,
      'site_id': site2Id,
      'status': 'Active',
      'principal_investigator': 'Dr. Dubois',
      'target_patients': 15,
    });
    await db.insert('study_sites', {
      'study_id': 1,
      'site_id': site3Id,
      'status': 'On Hold',
      'principal_investigator': 'Dr. Bernard',
      'target_patients': 10,
    });

    // Insert demo patients for study 1
    final patient1Id = await db.insert('patients', {
      'study_id': 1,
      'patient_number': '001-001',
      'initials': 'JD',
      'site_id': '001',
      'screening_date': '2026-02-01',
      'inclusion_date': '2026-02-15',
      'status': 'Included',
    });
    final patient2Id = await db.insert('patients', {
      'study_id': 1,
      'patient_number': '001-002',
      'initials': 'ML',
      'site_id': '001',
      'screening_date': '2026-02-05',
      'inclusion_date': '2026-02-20',
      'status': 'Included',
    });
    final patient3Id = await db.insert('patients', {
      'study_id': 1,
      'patient_number': '002-001',
      'initials': 'PB',
      'site_id': '002',
      'screening_date': '2026-02-20',
      'status': 'Screening',
    });

    // Insert default visit config for study 1
    final visitConfigs = [
      {'visit_number': 1, 'visit_name': 'V1', 'target_day': 0, 'window_before': 0, 'window_after': 0},
      {'visit_number': 2, 'visit_name': 'V2', 'target_day': 7, 'window_before': 2, 'window_after': 2},
      {'visit_number': 3, 'visit_name': 'V3', 'target_day': 14, 'window_before': 3, 'window_after': 3},
      {'visit_number': 4, 'visit_name': 'V4', 'target_day': 28, 'window_before': 3, 'window_after': 3},
      {'visit_number': 5, 'visit_name': 'V5', 'target_day': 42, 'window_before': 5, 'window_after': 5},
    ];
    for (final config in visitConfigs) {
      await db.insert('visit_config', {...config, 'study_id': 1});
    }

    // Insert demo visits for patient 1
    await db.insert('visits', {
      'patient_id': patient1Id,
      'visit_number': 1,
      'visit_date': '2026-02-15',
      'status': 'Completed',
      'in_window': 1,
    });
    await db.insert('visits', {
      'patient_id': patient1Id,
      'visit_number': 2,
      'visit_date': '2026-02-22',
      'status': 'Completed',
      'in_window': 1,
      'days_delta': 0,
    });
    await db.insert('visits', {
      'patient_id': patient1Id,
      'visit_number': 3,
      'visit_date': '2026-03-02',
      'status': 'Completed',
      'in_window': 1,
      'days_delta': 1,
    });

    // Insert demo adverse events
    await db.insert('adverse_events', {
      'patient_id': patient1Id,
      'description': 'Headache',
      'onset_date': '2026-02-20',
      'end_date': '2026-02-22',
      'severity': 'Mild',
      'outcome': 'Recovered',
      'causality': 'Possible',
    });
    await db.insert('adverse_events', {
      'patient_id': patient2Id,
      'description': 'Severe allergic reaction',
      'onset_date': '2026-03-05',
      'severity': 'Severe',
      'is_sae': 1,
      'reporting_date': '2026-03-05',
      'outcome': 'Recovered',
      'causality': 'Definite',
      'action': 'Treatment discontinued',
    });

    // Insert consent types for study 1
    final icfTypeId = await db.insert('consent_types', {
      'study_id': 1,
      'name': 'ICF Principal',
      'code': 'ICF',
    });
    final pkTypeId = await db.insert('consent_types', {
      'study_id': 1,
      'name': 'ICF PK',
      'code': 'PK',
    });
    await db.insert('consent_types', {
      'study_id': 1,
      'name': 'ICF Génétique',
      'code': 'GEN',
    });

    // Insert consent versions
    await db.insert('consent_versions', {
      'type_id': icfTypeId,
      'version': 'v1.0',
      'date': '2026-01-15',
      'is_current': 0,
    });
    await db.insert('consent_versions', {
      'type_id': icfTypeId,
      'version': 'v2.0',
      'date': '2026-02-01',
      'is_current': 1,
    });
    await db.insert('consent_versions', {
      'type_id': pkTypeId,
      'version': 'v1.0',
      'date': '2026-01-15',
      'is_current': 1,
    });

    // Insert patient consents
    await db.insert('patient_consents', {
      'patient_id': patient1Id,
      'consent_type': 'ICF Principal',
      'version': 'v1.0',
      'signed_date': '2026-02-15',
      'status': 'Update', // v2.0 disponible
    });
    await db.insert('patient_consents', {
      'patient_id': patient1Id,
      'consent_type': 'ICF PK',
      'version': 'v1.0',
      'signed_date': '2026-02-15',
      'status': 'Signed',
    });
    await db.insert('patient_consents', {
      'patient_id': patient2Id,
      'consent_type': 'ICF Principal',
      'version': 'v2.0',
      'signed_date': '2026-02-20',
      'status': 'Signed',
    });

    // Insert demo queries
    await db.insert('queries', {
      'patient_id': patient1Id,
      'visit_name': 'V2',
      'field_name': 'Weight',
      'description': 'Value out of range (120kg). Please verify.',
      'category': 'Data Entry',
      'status': 'Open',
      'open_date': '2026-03-01',
    });
    await db.insert('queries', {
      'patient_id': patient2Id,
      'visit_name': 'V1',
      'field_name': 'Informed Consent',
      'description': 'ICF version not matching protocol version.',
      'category': 'Documentation',
      'status': 'Closed',
      'open_date': '2026-02-25',
      'answer_date': '2026-02-26',
      'close_date': '2026-02-27',
      'answer': 'Re-consent obtained with correct version',
    });
  }

  // ========== STUDIES ==========

  static Future<List<Study>> getStudies() async {
    final db = await database;
    final maps = await db.query('studies', orderBy: 'study_number');

    List<Study> studies = maps.map((map) => Study.fromMap(map)).toList();

    for (var study in studies) {
      final patientResult = await db.rawQuery(
        'SELECT COUNT(*) as count FROM patients WHERE study_id = ?',
        [study.id],
      );
      study.patientCount = (patientResult.first['count'] as int?) ?? 0;

      final siteResult = await db.rawQuery(
        'SELECT COUNT(*) as count FROM study_sites WHERE study_id = ?',
        [study.id],
      );
      study.siteCount = (siteResult.first['count'] as int?) ?? 0;

      final aeResult = await db.rawQuery(
        'SELECT COUNT(*) as count FROM adverse_events ae JOIN patients p ON ae.patient_id = p.id WHERE p.study_id = ?',
        [study.id],
      );
      study.aeCount = (aeResult.first['count'] as int?) ?? 0;
    }

    return studies;
  }

  static Future<int> createStudy(Study study) async {
    final db = await database;
    return await db.insert('studies', study.toMap());
  }

  static Future<void> updateStudy(Study study) async {
    final db = await database;
    await db.update('studies', study.toMap(),
        where: 'id = ?', whereArgs: [study.id]);
  }

  static Future<void> deleteStudy(int id) async {
    final db = await database;
    await db.delete('studies', where: 'id = ?', whereArgs: [id]);
  }

  // ========== SITES ==========

  static Future<List<StudySite>> getStudySites(int studyId) async {
    final db = await database;
    final maps = await db.rawQuery('''
      SELECT ss.*, s.site_number, s.site_name, s.city, s.country,
             (SELECT COUNT(*) FROM patients p
              WHERE p.site_id = s.site_number AND p.study_id = ss.study_id) as patient_count
      FROM study_sites ss
      JOIN sites s ON ss.site_id = s.id
      WHERE ss.study_id = ?
      ORDER BY s.site_number
    ''', [studyId]);

    return maps.map((map) => StudySite.fromMap(map)).toList();
  }

  static Future<List<Site>> getSitesNotInStudy(int studyId) async {
    final db = await database;
    final maps = await db.rawQuery('''
      SELECT * FROM sites
      WHERE id NOT IN (SELECT site_id FROM study_sites WHERE study_id = ?)
      ORDER BY site_number
    ''', [studyId]);
    return maps.map((map) => Site.fromMap(map)).toList();
  }

  static Future<int> createSite(Site site) async {
    final db = await database;
    return await db.insert('sites', site.toMap());
  }

  static Future<int> addSiteToStudy(StudySite studySite) async {
    final db = await database;
    return await db.insert('study_sites', studySite.toMap());
  }

  static Future<void> updateStudySite(StudySite studySite) async {
    final db = await database;
    await db.update('study_sites', studySite.toMap(),
        where: 'id = ?', whereArgs: [studySite.id]);
  }

  static Future<void> removeSiteFromStudy(int studySiteId) async {
    final db = await database;
    await db.delete('study_sites', where: 'id = ?', whereArgs: [studySiteId]);
  }

  // ========== PATIENTS ==========

  static Future<List<Patient>> getPatients(int studyId) async {
    final db = await database;
    final maps = await db.query(
      'patients',
      where: 'study_id = ?',
      whereArgs: [studyId],
      orderBy: 'patient_number',
    );
    return maps.map((map) => Patient.fromMap(map)).toList();
  }

  static Future<int> createPatient(Patient patient) async {
    final db = await database;
    return await db.insert('patients', patient.toMap());
  }

  static Future<void> updatePatient(Patient patient) async {
    final db = await database;
    await db.update('patients', patient.toMap(),
        where: 'id = ?', whereArgs: [patient.id]);
  }

  static Future<void> deletePatient(int id) async {
    final db = await database;
    await db.delete('patients', where: 'id = ?', whereArgs: [id]);
  }

  // ========== VISITS ==========

  static Future<List<VisitConfig>> getVisitConfigs(int studyId) async {
    final db = await database;
    final maps = await db.query(
      'visit_config',
      where: 'study_id = ?',
      whereArgs: [studyId],
      orderBy: 'visit_number',
    );
    return maps.map((map) => VisitConfig(
      visitNumber: map['visit_number'] as int,
      visitName: map['visit_name'] as String,
      targetDay: map['target_day'] as int? ?? 0,
      windowBefore: map['window_before'] as int? ?? 0,
      windowAfter: map['window_after'] as int? ?? 0,
    )).toList();
  }

  static Future<List<Visit>> getPatientVisits(int patientId) async {
    final db = await database;
    final maps = await db.query(
      'visits',
      where: 'patient_id = ?',
      whereArgs: [patientId],
      orderBy: 'visit_number',
    );
    return maps.map((map) => Visit.fromMap(map)).toList();
  }

  static Future<int> createVisit(Visit visit) async {
    final db = await database;
    return await db.insert('visits', visit.toMap());
  }

  static Future<void> updateVisit(Visit visit) async {
    final db = await database;
    await db.update('visits', visit.toMap(),
        where: 'id = ?', whereArgs: [visit.id]);
  }

  static Future<void> upsertVisit(Visit visit) async {
    final db = await database;
    final existing = await db.query(
      'visits',
      where: 'patient_id = ? AND visit_number = ?',
      whereArgs: [visit.patientId, visit.visitNumber],
    );
    if (existing.isEmpty) {
      await db.insert('visits', visit.toMap());
    } else {
      await db.update('visits', visit.toMap(),
          where: 'patient_id = ? AND visit_number = ?',
          whereArgs: [visit.patientId, visit.visitNumber]);
    }
  }

  // ========== ADVERSE EVENTS ==========

  static Future<List<AdverseEvent>> getAdverseEvents(int studyId) async {
    final db = await database;
    final maps = await db.rawQuery('''
      SELECT ae.*, p.patient_number
      FROM adverse_events ae
      JOIN patients p ON ae.patient_id = p.id
      WHERE p.study_id = ?
      ORDER BY ae.onset_date DESC
    ''', [studyId]);
    return maps.map((map) => AdverseEvent.fromMap(map)).toList();
  }

  static Future<int> createAdverseEvent(AdverseEvent ae) async {
    final db = await database;
    return await db.insert('adverse_events', ae.toMap());
  }

  static Future<void> updateAdverseEvent(AdverseEvent ae) async {
    final db = await database;
    await db.update('adverse_events', ae.toMap(),
        where: 'id = ?', whereArgs: [ae.id]);
  }

  static Future<void> deleteAdverseEvent(int id) async {
    final db = await database;
    await db.delete('adverse_events', where: 'id = ?', whereArgs: [id]);
  }

  // ========== CONSENTS ==========

  static Future<List<PatientConsent>> getPatientConsents(int studyId) async {
    final db = await database;
    final maps = await db.rawQuery('''
      SELECT pc.*, p.patient_number
      FROM patient_consents pc
      JOIN patients p ON pc.patient_id = p.id
      WHERE p.study_id = ?
      ORDER BY p.patient_number, pc.consent_type
    ''', [studyId]);
    return maps.map((map) => PatientConsent.fromMap(map)).toList();
  }

  static Future<List<ConsentType>> getConsentTypes(int studyId) async {
    final db = await database;
    final maps = await db.query(
      'consent_types',
      where: 'study_id = ?',
      whereArgs: [studyId],
    );
    return maps.map((map) => ConsentType.fromMap(map)).toList();
  }

  static Future<List<ConsentVersion>> getConsentVersions(int typeId) async {
    final db = await database;
    final maps = await db.query(
      'consent_versions',
      where: 'type_id = ?',
      whereArgs: [typeId],
      orderBy: 'date DESC',
    );
    return maps.map((map) => ConsentVersion.fromMap(map)).toList();
  }

  static Future<int> createPatientConsent(PatientConsent consent) async {
    final db = await database;
    return await db.insert('patient_consents', consent.toMap());
  }

  static Future<void> updatePatientConsent(PatientConsent consent) async {
    final db = await database;
    await db.update('patient_consents', consent.toMap(),
        where: 'id = ?', whereArgs: [consent.id]);
  }

  static Future<void> deletePatientConsent(int id) async {
    final db = await database;
    await db.delete('patient_consents', where: 'id = ?', whereArgs: [id]);
  }

  // ========== QUERIES ==========

  static Future<List<Query>> getQueries(int studyId) async {
    final db = await database;
    final maps = await db.rawQuery('''
      SELECT q.*, p.patient_number
      FROM queries q
      JOIN patients p ON q.patient_id = p.id
      WHERE p.study_id = ?
      ORDER BY q.open_date DESC
    ''', [studyId]);
    return maps.map((map) => Query.fromMap(map)).toList();
  }

  static Future<int> createQuery(Query query) async {
    final db = await database;
    return await db.insert('queries', query.toMap());
  }

  static Future<void> updateQuery(Query query) async {
    final db = await database;
    await db.update('queries', query.toMap(),
        where: 'id = ?', whereArgs: [query.id]);
  }

  static Future<void> deleteQuery(int id) async {
    final db = await database;
    await db.delete('queries', where: 'id = ?', whereArgs: [id]);
  }

  // ========== UTILS ==========

  static Future<void> resetDatabase() async {
    final path = kIsWeb ? _dbName : join(await getDatabasesPath(), _dbName);
    await deleteDatabase(path);
    _database = null;
  }
}
