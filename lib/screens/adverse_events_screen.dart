import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../models/adverse_event.dart';
import '../widgets/stat_card.dart';
import '../services/database_service.dart';

class AdverseEventsScreen extends StatefulWidget {
  final Study study;

  const AdverseEventsScreen({super.key, required this.study});

  @override
  State<AdverseEventsScreen> createState() => _AdverseEventsScreenState();
}

class _AdverseEventsScreenState extends State<AdverseEventsScreen> {
  final TextEditingController _searchController = TextEditingController();
  AEOutcome? _outcomeFilter;
  List<AdverseEvent> _events = [];
  List<AdverseEvent> _filteredEvents = [];
  List<Patient> _patients = [];
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
      final events = await DatabaseService.getAdverseEvents(widget.study.id!);
      final patients = await DatabaseService.getPatients(widget.study.id!);
      setState(() {
        _events = events;
        _filteredEvents = events;
        _patients = patients;
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

  void _applyFilters() {
    setState(() {
      _filteredEvents = _events.where((ae) {
        final query = _searchController.text.toLowerCase();
        final matchesSearch = query.isEmpty ||
            (ae.patientNumber?.toLowerCase().contains(query) ?? false) ||
            ae.description.toLowerCase().contains(query);

        final matchesOutcome = _outcomeFilter == null || ae.outcome == _outcomeFilter;

        return matchesSearch && matchesOutcome;
      }).toList();
    });
  }

  void _showAEDialog([AdverseEvent? ae]) {
    showDialog(
      context: context,
      builder: (context) => _AdverseEventDialog(
        adverseEvent: ae,
        patients: _patients,
        onSave: (updatedAE) async {
          Navigator.pop(context);
          try {
            if (ae == null) {
              await DatabaseService.createAdverseEvent(updatedAE);
            } else {
              await DatabaseService.updateAdverseEvent(updatedAE);
            }
            _loadData();
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(ae == null ? 'AE reported!' : 'AE updated!')),
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

  Future<void> _deleteAE(AdverseEvent ae) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Adverse Event'),
        content: Text('Are you sure you want to delete "${ae.description}"?'),
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
      await DatabaseService.deleteAdverseEvent(ae.id!);
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalCount = _filteredEvents.length;
    final saeCount = _filteredEvents.where((ae) => ae.isSAE).length;
    final ongoingCount = _filteredEvents.where((ae) => ae.outcome == AEOutcome.ongoing).length;
    final recoveredCount = _filteredEvents.where((ae) => ae.outcome == AEOutcome.recovered).length;
    final fatalCount = _filteredEvents.where((ae) => ae.outcome == AEOutcome.fatal).length;

    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Adverse Events', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              Row(
                children: [
                  _buildLegend(),
                  const SizedBox(width: 24),
                  FilledButton.icon(
                    onPressed: _patients.isEmpty ? null : () => _showAEDialog(),
                    icon: const Icon(Icons.add),
                    label: const Text('Report AE'),
                  ),
                ],
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Stats
          StatsBar(
            stats: [
              StatCard(value: '$totalCount', label: 'Total', color: Colors.grey),
              StatCard(value: '$saeCount', label: 'SAE', color: Colors.red),
              StatCard(value: '$ongoingCount', label: 'Ongoing', color: Colors.blue),
              StatCard(value: '$recoveredCount', label: 'Recovered', color: Colors.green),
              StatCard(value: '$fatalCount', label: 'Fatal', color: Colors.red[900]!),
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
                    hintText: 'Search patient or description...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 200,
                child: DropdownButtonFormField<AEOutcome?>(
                  value: _outcomeFilter,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: 'Outcome',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('All')),
                    ...AEOutcome.values.map((outcome) {
                      return DropdownMenuItem(value: outcome, child: Text(outcome.label));
                    }),
                  ],
                  onChanged: (value) {
                    _outcomeFilter = value;
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
                              _TableHeader('Patient', flex: 1),
                              _TableHeader('Description', flex: 2),
                              _TableHeader('Onset', flex: 1),
                              _TableHeader('Severity', flex: 1),
                              _TableHeader('SAE', flex: 1),
                              _TableHeader('Outcome', flex: 1),
                              _TableHeader('Causality', flex: 1),
                              _TableHeader('Actions', flex: 1),
                            ],
                          ),
                        ),
                        Expanded(
                          child: _filteredEvents.isEmpty
                              ? Center(child: Text('No adverse events', style: TextStyle(color: Colors.grey[500])))
                              : ListView.separated(
                                  itemCount: _filteredEvents.length,
                                  separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                                  itemBuilder: (context, index) {
                                    final ae = _filteredEvents[index];
                                    return _AERow(
                                      ae: ae,
                                      dateFormat: _dateFormat,
                                      onEdit: () => _showAEDialog(ae),
                                      onDelete: () => _deleteAE(ae),
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

  Widget _buildLegend() {
    return Row(
      children: [
        _LegendItem(color: Colors.green, label: 'Mild'),
        const SizedBox(width: 12),
        _LegendItem(color: Colors.orange, label: 'Moderate'),
        const SizedBox(width: 12),
        _LegendItem(color: Colors.red, label: 'Severe'),
      ],
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

class _AERow extends StatelessWidget {
  final AdverseEvent ae;
  final DateFormat dateFormat;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _AERow({
    required this.ae,
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
            child: Text(ae.patientNumber ?? '-', style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
          Expanded(
            flex: 2,
            child: Text(ae.description, overflow: TextOverflow.ellipsis),
          ),
          Expanded(
            flex: 1,
            child: Text(dateFormat.format(ae.onsetDate), style: const TextStyle(fontSize: 12)),
          ),
          Expanded(
            flex: 1,
            child: _SeverityBadge(severity: ae.severity),
          ),
          Expanded(
            flex: 1,
            child: ae.isSAE
                ? Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text('SAE', style: TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.bold)),
                      ),
                      const SizedBox(width: 4),
                      _SAEDelayIndicator(ae: ae),
                    ],
                  )
                : const Text('-'),
          ),
          Expanded(
            flex: 1,
            child: _OutcomeBadge(outcome: ae.outcome),
          ),
          Expanded(
            flex: 1,
            child: Text(ae.causality.label, style: const TextStyle(fontSize: 12)),
          ),
          Expanded(
            flex: 1,
            child: Row(
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

class _SeverityBadge extends StatelessWidget {
  final AESeverity severity;

  const _SeverityBadge({required this.severity});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        width: 70,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Color(severity.color),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          severity.label,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.w500),
        ),
      ),
    );
  }
}

class _OutcomeBadge extends StatelessWidget {
  final AEOutcome outcome;

  const _OutcomeBadge({required this.outcome});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        width: 85,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Color(outcome.color),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          outcome.label,
          textAlign: TextAlign.center,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.w500),
        ),
      ),
    );
  }
}

class _SAEDelayIndicator extends StatelessWidget {
  final AdverseEvent ae;

  const _SAEDelayIndicator({required this.ae});

  @override
  Widget build(BuildContext context) {
    final hours = ae.saeDelayHours;
    if (hours == null) return const SizedBox.shrink();

    final onTime = hours <= 24;
    final text = onTime ? '<24h' : '+${(hours / 24).ceil()}d';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
      decoration: BoxDecoration(
        color: onTime ? Colors.green : Colors.red,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: const TextStyle(fontSize: 9, color: Colors.white, fontWeight: FontWeight.bold),
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

class _AdverseEventDialog extends StatefulWidget {
  final AdverseEvent? adverseEvent;
  final List<Patient> patients;
  final Function(AdverseEvent) onSave;

  const _AdverseEventDialog({this.adverseEvent, required this.patients, required this.onSave});

  @override
  State<_AdverseEventDialog> createState() => _AdverseEventDialogState();
}

class _AdverseEventDialogState extends State<_AdverseEventDialog> {
  late TextEditingController _descriptionController;
  late DateTime _onsetDate;
  late AESeverity _severity;
  late bool _isSAE;
  late AEOutcome _outcome;
  late AECausality _causality;
  Patient? _selectedPatient;

  final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    _descriptionController = TextEditingController(text: widget.adverseEvent?.description ?? '');
    _onsetDate = widget.adverseEvent?.onsetDate ?? DateTime.now();
    _severity = widget.adverseEvent?.severity ?? AESeverity.mild;
    _isSAE = widget.adverseEvent?.isSAE ?? false;
    _outcome = widget.adverseEvent?.outcome ?? AEOutcome.ongoing;
    _causality = widget.adverseEvent?.causality ?? AECausality.notRelated;

    if (widget.adverseEvent != null) {
      _selectedPatient = widget.patients.where((p) => p.id == widget.adverseEvent!.patientId).firstOrNull;
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _onsetDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() => _onsetDate = picked);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.adverseEvent != null;
    return AlertDialog(
      title: Text(isEdit ? 'Edit Adverse Event' : 'Report Adverse Event'),
      content: SizedBox(
        width: 500,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (!isEdit)
                DropdownButtonFormField<Patient>(
                  value: _selectedPatient,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Patient *'),
                  items: widget.patients.map((p) {
                    return DropdownMenuItem(value: p, child: Text('${p.patientNumber} (${p.initials ?? "-"})'));
                  }).toList(),
                  onChanged: (value) => setState(() => _selectedPatient = value),
                ),
              if (!isEdit) const SizedBox(height: 16),
              TextField(
                controller: _descriptionController,
                decoration: const InputDecoration(labelText: 'Description *'),
                maxLines: 2,
              ),
              const SizedBox(height: 16),
              InkWell(
                onTap: _selectDate,
                child: InputDecorator(
                  decoration: InputDecoration(
                    labelText: 'Onset Date',
                    prefixIcon: const Icon(Icons.calendar_today),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  child: Text(_dateFormat.format(_onsetDate)),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<AESeverity>(
                      value: _severity,
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Severity'),
                      items: AESeverity.values.map((s) {
                        return DropdownMenuItem(value: s, child: Text(s.label));
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) setState(() => _severity = value);
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: DropdownButtonFormField<AEOutcome>(
                      value: _outcome,
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Outcome'),
                      items: AEOutcome.values.map((o) {
                        return DropdownMenuItem(value: o, child: Text(o.label));
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) setState(() => _outcome = value);
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<AECausality>(
                      value: _causality,
                      isExpanded: true,
                      decoration: const InputDecoration(labelText: 'Causality'),
                      items: AECausality.values.map((c) {
                        return DropdownMenuItem(value: c, child: Text(c.label));
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) setState(() => _causality = value);
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: SwitchListTile(
                      title: const Text('SAE'),
                      subtitle: const Text('Serious'),
                      value: _isSAE,
                      onChanged: (value) => setState(() => _isSAE = value),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: (_descriptionController.text.isNotEmpty && (isEdit || _selectedPatient != null))
              ? () {
                  final ae = AdverseEvent(
                    id: widget.adverseEvent?.id,
                    patientId: _selectedPatient?.id ?? widget.adverseEvent?.patientId,
                    patientNumber: _selectedPatient?.patientNumber ?? widget.adverseEvent?.patientNumber,
                    description: _descriptionController.text,
                    onsetDate: _onsetDate,
                    severity: _severity,
                    isSAE: _isSAE,
                    reportingDate: _isSAE ? DateTime.now() : null,
                    outcome: _outcome,
                    causality: _causality,
                  );
                  widget.onSave(ae);
                }
              : null,
          child: const Text('Save'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }
}
