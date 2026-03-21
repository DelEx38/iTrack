import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../widgets/stat_card.dart';
import '../services/database_service.dart';

class PatientsScreen extends StatefulWidget {
  final Study study;

  const PatientsScreen({super.key, required this.study});

  @override
  State<PatientsScreen> createState() => _PatientsScreenState();
}

class _PatientsScreenState extends State<PatientsScreen> {
  final TextEditingController _searchController = TextEditingController();
  PatientStatus? _statusFilter;
  String? _siteFilter;
  List<Patient> _patients = [];
  List<Patient> _filteredPatients = [];
  bool _isLoading = true;

  final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    _loadPatients();
  }

  Future<void> _loadPatients() async {
    setState(() => _isLoading = true);
    try {
      final patients = await DatabaseService.getPatients(widget.study.id!);
      setState(() {
        _patients = patients;
        _filteredPatients = patients;
        _isLoading = false;
      });
      _applyFilters();
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading patients: $e')),
        );
      }
    }
  }

  List<String> get _availableSites {
    return _patients
        .map((p) => p.siteId)
        .whereType<String>()
        .toSet()
        .toList()
      ..sort();
  }

  void _applyFilters() {
    setState(() {
      _filteredPatients = _patients.where((patient) {
        final query = _searchController.text.toLowerCase();
        final matchesSearch = query.isEmpty ||
            patient.patientNumber.toLowerCase().contains(query) ||
            (patient.initials?.toLowerCase().contains(query) ?? false) ||
            (patient.siteId?.toLowerCase().contains(query) ?? false);

        final matchesStatus = _statusFilter == null || patient.status == _statusFilter;
        final matchesSite = _siteFilter == null || patient.siteId == _siteFilter;

        return matchesSearch && matchesStatus && matchesSite;
      }).toList();
    });
  }

  void _showPatientDialog([Patient? patient]) {
    showDialog(
      context: context,
      builder: (context) => _PatientDialog(
        patient: patient,
        studyId: widget.study.id!,
        onSave: (updatedPatient) async {
          Navigator.pop(context);
          try {
            if (patient == null) {
              await DatabaseService.createPatient(updatedPatient);
            } else {
              await DatabaseService.updatePatient(updatedPatient);
            }
            _loadPatients();
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(patient == null ? 'Patient added!' : 'Patient updated!')),
              );
            }
          } catch (e) {
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Error: $e')),
              );
            }
          }
        },
      ),
    );
  }

  Future<void> _deletePatient(Patient patient) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Patient'),
        content: Text('Are you sure you want to delete ${patient.patientNumber}?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await DatabaseService.deletePatient(patient.id!);
      _loadPatients();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Patient ${patient.patientNumber} deleted')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalPatients = _filteredPatients.length;
    final screeningCount = _filteredPatients.where((p) => p.status == PatientStatus.screening).length;
    final includedCount = _filteredPatients.where((p) => p.status == PatientStatus.included).length;
    final completedCount = _filteredPatients.where((p) => p.status == PatientStatus.completed).length;

    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Patients',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              FilledButton.icon(
                onPressed: () => _showPatientDialog(),
                icon: const Icon(Icons.add),
                label: const Text('Add Patient'),
              ),
            ],
          ),

          const SizedBox(height: 24),

          StatsBar(
            stats: [
              StatCard(value: '$totalPatients', label: 'Total', color: Colors.grey),
              StatCard(value: '$screeningCount', label: 'Screening', color: Colors.blue),
              StatCard(value: '$includedCount', label: 'Included', color: Colors.green),
              StatCard(value: '$completedCount', label: 'Completed', color: Colors.purple),
            ],
          ),

          const SizedBox(height: 24),

          // Filtres
          Row(
            children: [
              SizedBox(
                width: 250,
                child: TextField(
                  controller: _searchController,
                  onChanged: (_) => _applyFilters(),
                  decoration: InputDecoration(
                    hintText: 'Search patients...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 170,
                child: DropdownButtonFormField<PatientStatus?>(
                  value: _statusFilter,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: 'Status',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('All')),
                    ...PatientStatus.values.map((status) {
                      return DropdownMenuItem(value: status, child: Text(status.label));
                    }),
                  ],
                  onChanged: (value) {
                    _statusFilter = value;
                    _applyFilters();
                  },
                ),
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 120,
                child: DropdownButtonFormField<String?>(
                  value: _siteFilter,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: 'Site',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('All')),
                    ..._availableSites.map((site) {
                      return DropdownMenuItem(value: site, child: Text(site));
                    }),
                  ],
                  onChanged: (value) {
                    _siteFilter = value;
                    _applyFilters();
                  },
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Tableau
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey[800]!),
                    ),
                    child: Column(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: Colors.grey[850],
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                          ),
                          child: const Row(
                            children: [
                              _TableHeader('Patient #', flex: 1),
                              _TableHeader('Initials', flex: 1),
                              _TableHeader('Site', flex: 1),
                              _TableHeader('Status', flex: 1),
                              _TableHeader('Screening', flex: 1),
                              _TableHeader('Inclusion', flex: 1),
                              _TableHeader('Exit', flex: 1),
                              _TableHeader('Exit Reason', flex: 2),
                              _TableHeader('Actions', flex: 1),
                            ],
                          ),
                        ),
                        Expanded(
                          child: _filteredPatients.isEmpty
                              ? Center(
                                  child: Text('No patients found', style: TextStyle(color: Colors.grey[500])),
                                )
                              : ListView.separated(
                                  itemCount: _filteredPatients.length,
                                  separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                                  itemBuilder: (context, index) {
                                    final patient = _filteredPatients[index];
                                    return _PatientRow(
                                      patient: patient,
                                      dateFormat: _dateFormat,
                                      onEdit: () => _showPatientDialog(patient),
                                      onDelete: () => _deletePatient(patient),
                                    );
                                  },
                                ),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
}

class _TableHeader extends StatelessWidget {
  final String text;
  final int flex;

  const _TableHeader(this.text, {this.flex = 1});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      flex: flex,
      child: Text(text, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
    );
  }
}

class _PatientRow extends StatelessWidget {
  final Patient patient;
  final DateFormat dateFormat;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _PatientRow({
    required this.patient,
    required this.dateFormat,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Expanded(
            flex: 1,
            child: Text(patient.patientNumber, style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
          Expanded(
            flex: 1,
            child: Text(patient.initials ?? '-'),
          ),
          Expanded(
            flex: 1,
            child: Text(patient.siteId ?? '-'),
          ),
          Expanded(
            flex: 1,
            child: Align(
              alignment: Alignment.centerLeft,
              child: _PatientStatusBadge(status: patient.status),
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              patient.screeningDate != null ? dateFormat.format(patient.screeningDate!) : '-',
              style: const TextStyle(fontSize: 12),
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              patient.inclusionDate != null ? dateFormat.format(patient.inclusionDate!) : '-',
              style: const TextStyle(fontSize: 12),
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              patient.exitDate != null ? dateFormat.format(patient.exitDate!) : '-',
              style: const TextStyle(fontSize: 12),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(
              patient.exitReason ?? '-',
              style: const TextStyle(fontSize: 12),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Expanded(
            flex: 1,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(icon: const Icon(Icons.edit, size: 18), onPressed: onEdit, tooltip: 'Edit'),
                IconButton(icon: const Icon(Icons.delete, size: 18, color: Colors.red), onPressed: onDelete, tooltip: 'Delete'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PatientStatusBadge extends StatelessWidget {
  final PatientStatus status;

  const _PatientStatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 95,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: Color(status.color),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        status.label,
        textAlign: TextAlign.center,
        style: const TextStyle(
          fontSize: 11,
          color: Colors.white,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

class _PatientDialog extends StatefulWidget {
  final Patient? patient;
  final int studyId;
  final Function(Patient) onSave;

  const _PatientDialog({this.patient, required this.studyId, required this.onSave});

  @override
  State<_PatientDialog> createState() => _PatientDialogState();
}

class _PatientDialogState extends State<_PatientDialog> {
  late TextEditingController _numberController;
  late TextEditingController _initialsController;
  late TextEditingController _siteController;
  late PatientStatus _status;
  DateTime? _screeningDate;
  DateTime? _inclusionDate;

  final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    _numberController = TextEditingController(text: widget.patient?.patientNumber ?? '');
    _initialsController = TextEditingController(text: widget.patient?.initials ?? '');
    _siteController = TextEditingController(text: widget.patient?.siteId ?? '');
    _status = widget.patient?.status ?? PatientStatus.screening;
    _screeningDate = widget.patient?.screeningDate;
    _inclusionDate = widget.patient?.inclusionDate;
  }

  Future<void> _selectDate(bool isScreening) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: (isScreening ? _screeningDate : _inclusionDate) ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
    );
    if (picked != null) {
      setState(() {
        if (isScreening) {
          _screeningDate = picked;
        } else {
          _inclusionDate = picked;
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.patient != null;
    return AlertDialog(
      title: Text(isEdit ? 'Edit Patient ${widget.patient!.patientNumber}' : 'New Patient'),
      content: SizedBox(
        width: 450,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _numberController,
                    decoration: const InputDecoration(labelText: 'Patient Number *'),
                    enabled: !isEdit,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _initialsController,
                    decoration: const InputDecoration(labelText: 'Initials'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _siteController,
                    decoration: const InputDecoration(labelText: 'Site'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownButtonFormField<PatientStatus>(
                    value: _status,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Status'),
                    items: PatientStatus.values.map((status) {
                      return DropdownMenuItem(value: status, child: Text(status.label));
                    }).toList(),
                    onChanged: (value) {
                      if (value != null) setState(() => _status = value);
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: () => _selectDate(true),
                    child: InputDecorator(
                      decoration: const InputDecoration(labelText: 'Screening Date'),
                      child: Text(_screeningDate != null ? _dateFormat.format(_screeningDate!) : '-'),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: InkWell(
                    onTap: () => _selectDate(false),
                    child: InputDecorator(
                      decoration: const InputDecoration(labelText: 'Inclusion Date'),
                      child: Text(_inclusionDate != null ? _dateFormat.format(_inclusionDate!) : '-'),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: _numberController.text.isNotEmpty
              ? () {
                  final patient = Patient(
                    id: widget.patient?.id,
                    studyId: widget.studyId,
                    patientNumber: _numberController.text,
                    initials: _initialsController.text.isEmpty ? null : _initialsController.text,
                    siteId: _siteController.text.isEmpty ? null : _siteController.text,
                    status: _status,
                    screeningDate: _screeningDate,
                    inclusionDate: _inclusionDate,
                  );
                  widget.onSave(patient);
                }
              : null,
          child: const Text('Save'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _numberController.dispose();
    _initialsController.dispose();
    _siteController.dispose();
    super.dispose();
  }
}
