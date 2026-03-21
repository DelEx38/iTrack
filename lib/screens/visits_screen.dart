import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../models/visit.dart';
import '../widgets/stat_card.dart';
import '../services/database_service.dart';

class VisitsScreen extends StatefulWidget {
  final Study study;

  const VisitsScreen({super.key, required this.study});

  @override
  State<VisitsScreen> createState() => _VisitsScreenState();
}

class _VisitsScreenState extends State<VisitsScreen> {
  Patient? _selectedPatient;
  List<Patient> _patients = [];
  List<Visit> _visits = [];
  List<VisitConfig> _visitConfigs = [];
  bool _isLoading = true;

  final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final patients = await DatabaseService.getPatients(widget.study.id!);
      final configs = await DatabaseService.getVisitConfigs(widget.study.id!);
      setState(() {
        _patients = patients;
        _visitConfigs = configs.isNotEmpty ? configs : defaultVisitConfigs;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  Future<void> _loadPatientVisits() async {
    if (_selectedPatient == null) return;
    try {
      final visits = await DatabaseService.getPatientVisits(_selectedPatient!.id!);
      setState(() => _visits = visits);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading visits: $e')),
        );
      }
    }
  }

  DateTime? get _v1Date {
    final v1 = _visits.where((v) => v.visitNumber == 1 && v.visitDate != null).firstOrNull;
    return v1?.visitDate ?? _selectedPatient?.inclusionDate;
  }

  void _showVisitDialog(VisitConfig config, Visit? existingVisit) {
    showDialog(
      context: context,
      builder: (context) => _VisitDialog(
        config: config,
        visit: existingVisit,
        v1Date: _v1Date,
        patientId: _selectedPatient!.id!,
        onSave: (visit) async {
          Navigator.pop(context);
          try {
            await DatabaseService.upsertVisit(visit);
            _loadPatientVisits();
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Visit ${config.visitName} recorded!')),
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

  @override
  Widget build(BuildContext context) {
    final completedCount = _visits.where((v) => v.status == VisitStatus.completed).length;
    final inWindowCount = _visits.where((v) => v.inWindow == true).length;
    final outWindowCount = _visits.where((v) => v.inWindow == false).length;
    final pendingCount = _visits.where((v) => v.status == VisitStatus.pending).length;
    final missedCount = _visits.where((v) => v.status == VisitStatus.missed).length;

    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Visits', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              _buildLegend(),
            ],
          ),

          const SizedBox(height: 24),

          // Sélecteur patient
          Row(
            children: [
              SizedBox(
                width: 400,
                child: _isLoading
                    ? const LinearProgressIndicator()
                    : DropdownButtonFormField<Patient>(
                        value: _selectedPatient,
                        isExpanded: true,
                        decoration: InputDecoration(
                          labelText: 'Select Patient',
                          prefixIcon: const Icon(Icons.person),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                        ),
                        items: _patients.map((patient) {
                          return DropdownMenuItem(
                            value: patient,
                            child: Row(
                              children: [
                                Text(patient.patientNumber, style: const TextStyle(fontWeight: FontWeight.bold)),
                                const SizedBox(width: 8),
                                Text('(${patient.initials ?? '-'})', style: TextStyle(color: Colors.grey[400])),
                                const SizedBox(width: 8),
                                _PatientStatusBadge(status: patient.status),
                                if (patient.inclusionDate != null) ...[
                                  const SizedBox(width: 8),
                                  Text(
                                    'V1: ${_dateFormat.format(patient.inclusionDate!)}',
                                    style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                                  ),
                                ],
                              ],
                            ),
                          );
                        }).toList(),
                        onChanged: (patient) {
                          setState(() => _selectedPatient = patient);
                          _loadPatientVisits();
                        },
                      ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Stats
          if (_selectedPatient != null)
            StatsBar(
              stats: [
                StatCard(value: '${_visits.length}', label: 'Total', color: Colors.grey),
                StatCard(value: '$completedCount', label: 'Completed', color: Colors.green),
                StatCard(value: '$inWindowCount', label: 'In Window', color: Colors.blue),
                StatCard(value: '$outWindowCount', label: 'Out Window', color: Colors.orange),
                StatCard(value: '$pendingCount', label: 'Pending', color: Colors.grey),
                StatCard(value: '$missedCount', label: 'Missed', color: Colors.red),
              ],
            ),

          const SizedBox(height: 24),

          // Grille des visites
          Expanded(
            child: _selectedPatient == null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.person_search, size: 64, color: Colors.grey[600]),
                        const SizedBox(height: 16),
                        Text('Select a patient to view visits', style: TextStyle(color: Colors.grey[500])),
                      ],
                    ),
                  )
                : _buildVisitGrid(),
          ),
        ],
      ),
    );
  }

  Widget _buildLegend() {
    return Row(
      children: [
        _LegendItem(color: Colors.green, label: 'In Window'),
        const SizedBox(width: 16),
        _LegendItem(color: Colors.orange, label: 'Out Window'),
        const SizedBox(width: 16),
        _LegendItem(color: Colors.grey, label: 'Pending'),
        const SizedBox(width: 16),
        _LegendItem(color: Colors.red, label: 'Missed'),
      ],
    );
  }

  Widget _buildVisitGrid() {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.grey[850],
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            ),
            child: const Row(
              children: [
                _TableHeader('Visit', flex: 1),
                _TableHeader('Target Day', flex: 1),
                _TableHeader('Window', flex: 1),
                _TableHeader('Target Date', flex: 1),
                _TableHeader('Actual Date', flex: 1),
                _TableHeader('Window Check', flex: 1),
                _TableHeader('Status', flex: 1),
                _TableHeader('Actions', flex: 1),
              ],
            ),
          ),
          // Rows
          Expanded(
            child: ListView.separated(
              itemCount: _visitConfigs.length,
              separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
              itemBuilder: (context, index) {
                final config = _visitConfigs[index];
                final visit = _visits.where((v) => v.visitNumber == config.visitNumber).firstOrNull ??
                    Visit(visitNumber: config.visitNumber);
                return _VisitRow(
                  config: config,
                  visit: visit,
                  v1Date: _v1Date,
                  dateFormat: _dateFormat,
                  onRecord: () => _showVisitDialog(config, visit.id != null ? visit : null),
                );
              },
            ),
          ),
        ],
      ),
    );
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

class _VisitRow extends StatelessWidget {
  final VisitConfig config;
  final Visit visit;
  final DateTime? v1Date;
  final DateFormat dateFormat;
  final VoidCallback onRecord;

  const _VisitRow({
    required this.config,
    required this.visit,
    this.v1Date,
    required this.dateFormat,
    required this.onRecord,
  });

  DateTime? get targetDate {
    if (v1Date == null || config.isReference) return null;
    return v1Date!.add(Duration(days: config.targetDay));
  }

  @override
  Widget build(BuildContext context) {
    final isCompleted = visit.status == VisitStatus.completed;
    final inWindow = visit.inWindow;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: config.isReference ? Colors.blue.withValues(alpha: 0.1) : null,
      child: Row(
        children: [
          // Visit name
          Expanded(
            flex: 1,
            child: Row(
              children: [
                Text(
                  config.visitName,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                if (config.isReference) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.blue,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text('REF', style: TextStyle(fontSize: 10, color: Colors.white)),
                  ),
                ],
              ],
            ),
          ),
          // Target day
          Expanded(
            flex: 1,
            child: Text(config.isReference ? '-' : 'J${config.targetDay}'),
          ),
          // Window
          Expanded(
            flex: 1,
            child: Text(config.isReference ? '-' : '-${config.windowBefore}/+${config.windowAfter}'),
          ),
          // Target date
          Expanded(
            flex: 1,
            child: Text(
              targetDate != null ? dateFormat.format(targetDate!) : '-',
              style: TextStyle(fontSize: 12, color: Colors.grey[400]),
            ),
          ),
          // Actual date
          Expanded(
            flex: 1,
            child: Text(
              visit.visitDate != null ? dateFormat.format(visit.visitDate!) : '-',
              style: TextStyle(
                fontWeight: isCompleted ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ),
          // Window check
          Expanded(
            flex: 1,
            child: isCompleted && !config.isReference
                ? _WindowCheckBadge(inWindow: inWindow, daysDelta: visit.daysDelta)
                : const Text('-'),
          ),
          // Status
          Expanded(
            flex: 1,
            child: _VisitStatusBadge(status: visit.status),
          ),
          // Actions
          Expanded(
            flex: 1,
            child: Row(
              children: [
                IconButton(
                  icon: Icon(
                    isCompleted ? Icons.edit : Icons.add_circle,
                    size: 18,
                    color: isCompleted ? null : Colors.green,
                  ),
                  onPressed: onRecord,
                  tooltip: isCompleted ? 'Edit' : 'Record Visit',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _WindowCheckBadge extends StatelessWidget {
  final bool? inWindow;
  final int? daysDelta;

  const _WindowCheckBadge({this.inWindow, this.daysDelta});

  @override
  Widget build(BuildContext context) {
    final isOk = inWindow == true;
    final delta = daysDelta ?? 0;
    final deltaStr = delta == 0 ? '' : (delta > 0 ? ' +$delta' : ' $delta');

    return Container(
      width: 70,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isOk ? Colors.green : Colors.orange,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        isOk ? 'OK$deltaStr' : 'OUT$deltaStr',
        textAlign: TextAlign.center,
        style: const TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.bold),
      ),
    );
  }
}

class _VisitStatusBadge extends StatelessWidget {
  final VisitStatus status;

  const _VisitStatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 80,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Color(status.color),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        status.label,
        textAlign: TextAlign.center,
        style: const TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.w500),
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
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Color(status.color).withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: Color(status.color)),
      ),
      child: Text(
        status.label,
        style: TextStyle(fontSize: 10, color: Color(status.color), fontWeight: FontWeight.w500),
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2)),
        ),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 11, color: Colors.grey[400])),
      ],
    );
  }
}

class _VisitDialog extends StatefulWidget {
  final VisitConfig config;
  final Visit? visit;
  final DateTime? v1Date;
  final int patientId;
  final Function(Visit) onSave;

  const _VisitDialog({
    required this.config,
    this.visit,
    this.v1Date,
    required this.patientId,
    required this.onSave,
  });

  @override
  State<_VisitDialog> createState() => _VisitDialogState();
}

class _VisitDialogState extends State<_VisitDialog> {
  late DateTime? _visitDate;
  late VisitStatus _status;
  late TextEditingController _commentsController;
  final _dateFormat = DateFormat('yyyy-MM-dd');

  DateTime? get _targetDate {
    if (widget.v1Date == null || widget.config.isReference) return null;
    return widget.v1Date!.add(Duration(days: widget.config.targetDay));
  }

  bool get _inWindow {
    if (_visitDate == null || _targetDate == null) return true;
    final delta = _visitDate!.difference(_targetDate!).inDays;
    return delta >= -widget.config.windowBefore && delta <= widget.config.windowAfter;
  }

  int get _daysDelta {
    if (_visitDate == null || _targetDate == null) return 0;
    return _visitDate!.difference(_targetDate!).inDays;
  }

  @override
  void initState() {
    super.initState();
    _visitDate = widget.visit?.visitDate;
    _status = widget.visit?.status ?? VisitStatus.completed;
    _commentsController = TextEditingController(text: widget.visit?.comments ?? '');
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _visitDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
    );
    if (picked != null) {
      setState(() => _visitDate = picked);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Record ${widget.config.visitName}'),
      content: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Target info
            if (_targetDate != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, size: 18, color: Colors.blue),
                    const SizedBox(width: 8),
                    Text(
                      'Target: ${_dateFormat.format(_targetDate!)} (J${widget.config.targetDay})',
                      style: const TextStyle(color: Colors.blue),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            // Date picker
            InkWell(
              onTap: _selectDate,
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: 'Visit Date',
                  prefixIcon: const Icon(Icons.calendar_today),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: Text(_visitDate != null ? _dateFormat.format(_visitDate!) : 'Select date'),
              ),
            ),
            // Window check preview
            if (_visitDate != null && _targetDate != null) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    _inWindow ? Icons.check_circle : Icons.warning,
                    size: 18,
                    color: _inWindow ? Colors.green : Colors.orange,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _inWindow ? 'In window ($_daysDelta days)' : 'Out of window ($_daysDelta days)',
                    style: TextStyle(color: _inWindow ? Colors.green : Colors.orange),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 16),
            // Status
            DropdownButtonFormField<VisitStatus>(
              value: _status,
              isExpanded: true,
              decoration: InputDecoration(
                labelText: 'Status',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
              items: VisitStatus.values.map((status) {
                return DropdownMenuItem(value: status, child: Text(status.label));
              }).toList(),
              onChanged: (value) {
                if (value != null) setState(() => _status = value);
              },
            ),
            const SizedBox(height: 16),
            // Comments
            TextField(
              controller: _commentsController,
              decoration: InputDecoration(
                labelText: 'Comments',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
              maxLines: 2,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: _visitDate != null || _status == VisitStatus.missed
              ? () {
                  final visit = Visit(
                    id: widget.visit?.id,
                    patientId: widget.patientId,
                    visitNumber: widget.config.visitNumber,
                    visitDate: _visitDate,
                    status: _status,
                    comments: _commentsController.text,
                    inWindow: _inWindow,
                    daysDelta: _daysDelta,
                  );
                  widget.onSave(visit);
                }
              : null,
          child: const Text('Save'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _commentsController.dispose();
    super.dispose();
  }
}
