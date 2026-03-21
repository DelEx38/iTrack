import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../models/document.dart';
import '../widgets/stat_card.dart';
import '../services/database_service.dart';

class DocumentsScreen extends StatefulWidget {
  final Study study;

  const DocumentsScreen({super.key, required this.study});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  final TextEditingController _searchController = TextEditingController();
  String? _typeFilter;
  List<PatientConsent> _consents = [];
  List<PatientConsent> _filteredConsents = [];
  List<Patient> _patients = [];
  List<ConsentType> _consentTypes = [];
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
      final consents = await DatabaseService.getPatientConsents(widget.study.id!);
      final patients = await DatabaseService.getPatients(widget.study.id!);
      final types = await DatabaseService.getConsentTypes(widget.study.id!);
      setState(() {
        _consents = consents;
        _filteredConsents = consents;
        _patients = patients;
        _consentTypes = types;
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

  List<String> get _availableTypes {
    return _consents.map((c) => c.consentType).toSet().toList()..sort();
  }

  void _applyFilters() {
    setState(() {
      _filteredConsents = _consents.where((consent) {
        final query = _searchController.text.toLowerCase();
        final matchesSearch = query.isEmpty ||
            (consent.patientNumber?.toLowerCase().contains(query) ?? false) ||
            consent.consentType.toLowerCase().contains(query);

        final matchesType = _typeFilter == null || consent.consentType == _typeFilter;

        return matchesSearch && matchesType;
      }).toList();
    });
  }

  void _showConsentDialog([PatientConsent? consent]) {
    showDialog(
      context: context,
      builder: (context) => _ConsentDialog(
        consent: consent,
        patients: _patients,
        consentTypes: _consentTypes,
        onSave: (updatedConsent) async {
          Navigator.pop(context);
          try {
            if (consent == null) {
              await DatabaseService.createPatientConsent(updatedConsent);
            } else {
              await DatabaseService.updatePatientConsent(updatedConsent);
            }
            _loadData();
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(consent == null ? 'Consent added!' : 'Consent updated!')),
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

  Future<void> _deleteConsent(PatientConsent consent) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Consent'),
        content: Text('Delete consent "${consent.consentType}" for ${consent.patientNumber}?'),
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
      await DatabaseService.deletePatientConsent(consent.id!);
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalCount = _filteredConsents.length;
    final signedCount = _filteredConsents.where((c) => c.status == ConsentStatus.signed).length;
    final missingCount = _filteredConsents.where((c) => c.status == ConsentStatus.missing).length;
    final updateCount = _filteredConsents.where((c) => c.status == ConsentStatus.needsUpdate).length;

    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Documents', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              Row(
                children: [
                  _buildLegend(),
                  const SizedBox(width: 24),
                  FilledButton.icon(
                    onPressed: _patients.isEmpty ? null : () => _showConsentDialog(),
                    icon: const Icon(Icons.add),
                    label: const Text('Add Consent'),
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
              StatCard(value: '$signedCount', label: 'Signed', color: Colors.green),
              StatCard(value: '$missingCount', label: 'Missing', color: Colors.red),
              StatCard(value: '$updateCount', label: 'Update', color: Colors.orange),
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
                    hintText: 'Search patient...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 180,
                child: DropdownButtonFormField<String?>(
                  value: _typeFilter,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: 'Type',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('All')),
                    ..._availableTypes.map((type) {
                      return DropdownMenuItem(value: type, child: Text(type));
                    }),
                  ],
                  onChanged: (value) {
                    _typeFilter = value;
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
                              _TableHeader('Type', flex: 1),
                              _TableHeader('Version', flex: 1),
                              _TableHeader('Signed Date', flex: 1),
                              _TableHeader('Status', flex: 1),
                              _TableHeader('Full Label', flex: 2),
                              _TableHeader('Actions', flex: 1),
                            ],
                          ),
                        ),
                        Expanded(
                          child: _filteredConsents.isEmpty
                              ? Center(child: Text('No consents', style: TextStyle(color: Colors.grey[500])))
                              : ListView.separated(
                                  itemCount: _filteredConsents.length,
                                  separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                                  itemBuilder: (context, index) {
                                    final consent = _filteredConsents[index];
                                    return _ConsentRow(
                                      consent: consent,
                                      dateFormat: _dateFormat,
                                      onEdit: () => _showConsentDialog(consent),
                                      onDelete: () => _deleteConsent(consent),
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
        _LegendItem(color: Colors.green, label: 'Signed'),
        const SizedBox(width: 12),
        _LegendItem(color: Colors.red, label: 'Missing'),
        const SizedBox(width: 12),
        _LegendItem(color: Colors.orange, label: 'New version'),
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

class _ConsentRow extends StatelessWidget {
  final PatientConsent consent;
  final DateFormat dateFormat;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _ConsentRow({
    required this.consent,
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
            child: Text(consent.patientNumber ?? '-', style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
          Expanded(
            flex: 1,
            child: Text(consent.consentType),
          ),
          Expanded(
            flex: 1,
            child: Text(consent.version ?? '-'),
          ),
          Expanded(
            flex: 1,
            child: Text(
              consent.signedDate != null ? dateFormat.format(consent.signedDate!) : '-',
              style: const TextStyle(fontSize: 12),
            ),
          ),
          Expanded(
            flex: 1,
            child: _ConsentStatusBadge(status: consent.status),
          ),
          Expanded(
            flex: 2,
            child: Text(
              consent.fullLabel,
              style: TextStyle(fontSize: 12, color: Colors.grey[400]),
              overflow: TextOverflow.ellipsis,
            ),
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

class _ConsentStatusBadge extends StatelessWidget {
  final ConsentStatus status;

  const _ConsentStatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        width: 70,
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

class _ConsentDialog extends StatefulWidget {
  final PatientConsent? consent;
  final List<Patient> patients;
  final List<ConsentType> consentTypes;
  final Function(PatientConsent) onSave;

  const _ConsentDialog({
    this.consent,
    required this.patients,
    required this.consentTypes,
    required this.onSave,
  });

  @override
  State<_ConsentDialog> createState() => _ConsentDialogState();
}

class _ConsentDialogState extends State<_ConsentDialog> {
  Patient? _selectedPatient;
  String? _selectedType;
  String? _selectedVersion;
  DateTime? _signedDate;

  final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    if (widget.consent != null) {
      _selectedPatient = widget.patients.where((p) => p.id == widget.consent!.patientId).firstOrNull;
      _selectedType = widget.consent!.consentType;
      _selectedVersion = widget.consent!.version;
      _signedDate = widget.consent!.signedDate;
    } else if (widget.consentTypes.isNotEmpty) {
      _selectedType = widget.consentTypes.first.name;
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _signedDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() => _signedDate = picked);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.consent != null;
    return AlertDialog(
      title: Text(isEdit ? 'Edit Consent' : 'Add Consent'),
      content: SizedBox(
        width: 400,
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
            DropdownButtonFormField<String>(
              value: _selectedType,
              isExpanded: true,
              decoration: const InputDecoration(labelText: 'Consent Type *'),
              items: widget.consentTypes.map((type) {
                return DropdownMenuItem(value: type.name, child: Text(type.name));
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _selectedType = value;
                    _selectedVersion = null;
                  });
                }
              },
            ),
            const SizedBox(height: 16),
            TextField(
              decoration: const InputDecoration(labelText: 'Version'),
              controller: TextEditingController(text: _selectedVersion),
              onChanged: (value) => _selectedVersion = value,
            ),
            const SizedBox(height: 16),
            InkWell(
              onTap: _selectDate,
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: 'Signed Date',
                  prefixIcon: const Icon(Icons.calendar_today),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: Text(_signedDate != null ? _dateFormat.format(_signedDate!) : 'Select date'),
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: (_selectedType != null && (isEdit || _selectedPatient != null))
              ? () {
                  final consent = PatientConsent(
                    id: widget.consent?.id,
                    patientId: _selectedPatient?.id ?? widget.consent?.patientId,
                    patientNumber: _selectedPatient?.patientNumber ?? widget.consent?.patientNumber,
                    consentType: _selectedType!,
                    version: _selectedVersion,
                    signedDate: _signedDate,
                    status: _signedDate != null ? ConsentStatus.signed : ConsentStatus.missing,
                  );
                  widget.onSave(consent);
                }
              : null,
          child: const Text('Save'),
        ),
      ],
    );
  }
}
