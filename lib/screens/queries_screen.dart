import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../models/query.dart';
import '../widgets/stat_card.dart';
import '../services/database_service.dart';

class QueriesScreen extends StatefulWidget {
  final Study study;

  const QueriesScreen({super.key, required this.study});

  @override
  State<QueriesScreen> createState() => _QueriesScreenState();
}

class _QueriesScreenState extends State<QueriesScreen> {
  final TextEditingController _searchController = TextEditingController();
  QueryStatus? _statusFilter;
  String? _ageFilter;
  List<Query> _queries = [];
  List<Query> _filteredQueries = [];
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
      final queries = await DatabaseService.getQueries(widget.study.id!);
      final patients = await DatabaseService.getPatients(widget.study.id!);
      setState(() {
        _queries = queries;
        _filteredQueries = queries;
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
      _filteredQueries = _queries.where((query) {
        final searchQuery = _searchController.text.toLowerCase();
        final matchesSearch = searchQuery.isEmpty ||
            (query.patientNumber?.toLowerCase().contains(searchQuery) ?? false) ||
            query.description.toLowerCase().contains(searchQuery) ||
            (query.fieldName?.toLowerCase().contains(searchQuery) ?? false);

        final matchesStatus = _statusFilter == null || query.status == _statusFilter;

        bool matchesAge = true;
        if (_ageFilter == '>7') {
          matchesAge = query.ageInDays > 7;
        } else if (_ageFilter == '>30') {
          matchesAge = query.ageInDays > 30;
        }

        return matchesSearch && matchesStatus && matchesAge;
      }).toList();
    });
  }

  void _showQueryDialog([Query? query]) {
    showDialog(
      context: context,
      builder: (context) => _QueryDialog(
        query: query,
        patients: _patients,
        onSave: (updatedQuery) async {
          Navigator.pop(context);
          try {
            if (query == null) {
              await DatabaseService.createQuery(updatedQuery);
            } else {
              await DatabaseService.updateQuery(updatedQuery);
            }
            _loadData();
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(query == null ? 'Query created!' : 'Query updated!')),
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

  Future<void> _quickAnswer(Query query) async {
    final controller = TextEditingController();
    final answer = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Answer Query #${query.id}'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(labelText: 'Answer'),
          maxLines: 3,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(context, controller.text),
            child: const Text('Answer'),
          ),
        ],
      ),
    );

    if (answer != null && answer.isNotEmpty) {
      final updated = Query(
        id: query.id,
        patientId: query.patientId,
        patientNumber: query.patientNumber,
        visitName: query.visitName,
        fieldName: query.fieldName,
        description: query.description,
        category: query.category,
        status: QueryStatus.answered,
        openDate: query.openDate,
        answerDate: DateTime.now(),
        answer: answer,
      );
      await DatabaseService.updateQuery(updated);
      _loadData();
    }
  }

  Future<void> _quickClose(Query query) async {
    final updated = Query(
      id: query.id,
      patientId: query.patientId,
      patientNumber: query.patientNumber,
      visitName: query.visitName,
      fieldName: query.fieldName,
      description: query.description,
      category: query.category,
      status: QueryStatus.closed,
      openDate: query.openDate,
      answerDate: query.answerDate,
      closeDate: DateTime.now(),
      answer: query.answer,
    );
    await DatabaseService.updateQuery(updated);
    _loadData();
  }

  Future<void> _deleteQuery(Query query) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Query'),
        content: Text('Are you sure you want to delete query #${query.id}?'),
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
      await DatabaseService.deleteQuery(query.id!);
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalCount = _filteredQueries.length;
    final openCount = _filteredQueries.where((q) => q.status == QueryStatus.open).length;
    final answeredCount = _filteredQueries.where((q) => q.status == QueryStatus.answered).length;
    final closedCount = _filteredQueries.where((q) => q.status == QueryStatus.closed).length;
    final overdueCount = _filteredQueries.where((q) => q.isOverdue).length;

    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Queries', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              Row(
                children: [
                  _buildLegend(),
                  const SizedBox(width: 24),
                  FilledButton.icon(
                    onPressed: _patients.isEmpty ? null : () => _showQueryDialog(),
                    icon: const Icon(Icons.add),
                    label: const Text('New Query'),
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
              StatCard(value: '$openCount', label: 'Open', color: Colors.red),
              StatCard(value: '$answeredCount', label: 'Answered', color: Colors.orange),
              StatCard(value: '$closedCount', label: 'Closed', color: Colors.green),
              StatCard(value: '$overdueCount', label: 'Overdue', color: Colors.red[900]!),
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
                width: 150,
                child: DropdownButtonFormField<QueryStatus?>(
                  value: _statusFilter,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: 'Status',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('All')),
                    ...QueryStatus.values.map((status) {
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
                width: 150,
                child: DropdownButtonFormField<String?>(
                  value: _ageFilter,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: 'Age',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  items: const [
                    DropdownMenuItem(value: null, child: Text('All')),
                    DropdownMenuItem(value: '>7', child: Text('> 7 days')),
                    DropdownMenuItem(value: '>30', child: Text('> 30 days')),
                  ],
                  onChanged: (value) {
                    _ageFilter = value;
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
                              _TableHeader('Visit', flex: 1),
                              _TableHeader('Field', flex: 1),
                              _TableHeader('Description', flex: 2),
                              _TableHeader('Category', flex: 1),
                              _TableHeader('Age', flex: 1),
                              _TableHeader('Status', flex: 1),
                              _TableHeader('Actions', flex: 1),
                            ],
                          ),
                        ),
                        Expanded(
                          child: _filteredQueries.isEmpty
                              ? Center(child: Text('No queries', style: TextStyle(color: Colors.grey[500])))
                              : ListView.separated(
                                  itemCount: _filteredQueries.length,
                                  separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                                  itemBuilder: (context, index) {
                                    final query = _filteredQueries[index];
                                    return _QueryRow(
                                      query: query,
                                      dateFormat: _dateFormat,
                                      onEdit: () => _showQueryDialog(query),
                                      onAnswer: () => _quickAnswer(query),
                                      onClose: () => _quickClose(query),
                                      onDelete: () => _deleteQuery(query),
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
        _LegendItem(color: Colors.red, label: 'Open'),
        const SizedBox(width: 12),
        _LegendItem(color: Colors.orange, label: 'Answered'),
        const SizedBox(width: 12),
        _LegendItem(color: Colors.green, label: 'Closed'),
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

class _QueryRow extends StatelessWidget {
  final Query query;
  final DateFormat dateFormat;
  final VoidCallback onEdit;
  final VoidCallback onAnswer;
  final VoidCallback onClose;
  final VoidCallback onDelete;

  const _QueryRow({
    required this.query,
    required this.dateFormat,
    required this.onEdit,
    required this.onAnswer,
    required this.onClose,
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
            child: Text(query.patientNumber ?? '-', style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
          Expanded(
            flex: 1,
            child: Text(query.visitName ?? '-'),
          ),
          Expanded(
            flex: 1,
            child: Text(query.fieldName ?? '-', style: const TextStyle(fontSize: 12)),
          ),
          Expanded(
            flex: 2,
            child: Text(query.description, overflow: TextOverflow.ellipsis),
          ),
          Expanded(
            flex: 1,
            child: Text(query.category.label, style: const TextStyle(fontSize: 12)),
          ),
          Expanded(
            flex: 1,
            child: _AgeIndicator(ageInDays: query.ageInDays, isOverdue: query.isOverdue),
          ),
          Expanded(
            flex: 1,
            child: _QueryStatusBadge(status: query.status),
          ),
          Expanded(
            flex: 1,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (query.status == QueryStatus.open)
                  IconButton(
                    icon: const Icon(Icons.reply, size: 18, color: Colors.orange),
                    onPressed: onAnswer,
                    tooltip: 'Answer',
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 32),
                  ),
                if (query.status == QueryStatus.answered)
                  IconButton(
                    icon: const Icon(Icons.check, size: 18, color: Colors.green),
                    onPressed: onClose,
                    tooltip: 'Close',
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 32),
                  ),
                IconButton(
                  icon: const Icon(Icons.edit, size: 18),
                  onPressed: onEdit,
                  tooltip: 'Edit',
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(minWidth: 32),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, size: 18, color: Colors.red),
                  onPressed: onDelete,
                  tooltip: 'Delete',
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(minWidth: 32),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AgeIndicator extends StatelessWidget {
  final int ageInDays;
  final bool isOverdue;

  const _AgeIndicator({required this.ageInDays, required this.isOverdue});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          '$ageInDays d',
          style: TextStyle(
            fontWeight: isOverdue ? FontWeight.bold : FontWeight.normal,
            color: isOverdue ? Colors.red : null,
          ),
        ),
        if (isOverdue) ...[
          const SizedBox(width: 4),
          const Icon(Icons.warning, size: 14, color: Colors.red),
        ],
      ],
    );
  }
}

class _QueryStatusBadge extends StatelessWidget {
  final QueryStatus status;

  const _QueryStatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        width: 75,
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

class _QueryDialog extends StatefulWidget {
  final Query? query;
  final List<Patient> patients;
  final Function(Query) onSave;

  const _QueryDialog({this.query, required this.patients, required this.onSave});

  @override
  State<_QueryDialog> createState() => _QueryDialogState();
}

class _QueryDialogState extends State<_QueryDialog> {
  late TextEditingController _descriptionController;
  late TextEditingController _fieldController;
  late TextEditingController _visitController;
  late QueryCategory _category;
  late QueryStatus _status;
  Patient? _selectedPatient;

  @override
  void initState() {
    super.initState();
    _descriptionController = TextEditingController(text: widget.query?.description ?? '');
    _fieldController = TextEditingController(text: widget.query?.fieldName ?? '');
    _visitController = TextEditingController(text: widget.query?.visitName ?? '');
    _category = widget.query?.category ?? QueryCategory.dataEntry;
    _status = widget.query?.status ?? QueryStatus.open;

    if (widget.query != null) {
      _selectedPatient = widget.patients.where((p) => p.id == widget.query!.patientId).firstOrNull;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.query != null;
    return AlertDialog(
      title: Text(isEdit ? 'Edit Query' : 'New Query'),
      content: SizedBox(
        width: 450,
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
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _visitController,
                    decoration: const InputDecoration(labelText: 'Visit'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _fieldController,
                    decoration: const InputDecoration(labelText: 'Field'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'Description *'),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<QueryCategory>(
                    value: _category,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Category'),
                    items: QueryCategory.values.map((c) {
                      return DropdownMenuItem(value: c, child: Text(c.label));
                    }).toList(),
                    onChanged: (value) {
                      if (value != null) setState(() => _category = value);
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: DropdownButtonFormField<QueryStatus>(
                    value: _status,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Status'),
                    items: QueryStatus.values.map((s) {
                      return DropdownMenuItem(value: s, child: Text(s.label));
                    }).toList(),
                    onChanged: (value) {
                      if (value != null) setState(() => _status = value);
                    },
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
          onPressed: (_descriptionController.text.isNotEmpty && (isEdit || _selectedPatient != null))
              ? () {
                  final query = Query(
                    id: widget.query?.id,
                    patientId: _selectedPatient?.id ?? widget.query?.patientId,
                    patientNumber: _selectedPatient?.patientNumber ?? widget.query?.patientNumber,
                    visitName: _visitController.text.isEmpty ? null : _visitController.text,
                    fieldName: _fieldController.text.isEmpty ? null : _fieldController.text,
                    description: _descriptionController.text,
                    category: _category,
                    status: _status,
                    openDate: widget.query?.openDate ?? DateTime.now(),
                  );
                  widget.onSave(query);
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
    _fieldController.dispose();
    _visitController.dispose();
    super.dispose();
  }
}
