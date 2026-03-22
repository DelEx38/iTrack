import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:file_picker/file_picker.dart';
import '../models/study.dart';
import '../models/visit.dart';
import '../models/document.dart';
import '../services/soa_parser_service.dart';
import '../services/database_service.dart';

class SettingsScreen extends StatefulWidget {
  final Study study;

  const SettingsScreen({super.key, required this.study});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Settings', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                Row(
                  children: [
                    OutlinedButton.icon(
                      onPressed: _exportConfig,
                      icon: const Icon(Icons.download),
                      label: const Text('Export'),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton.icon(
                      onPressed: _importConfig,
                      icon: const Icon(Icons.upload),
                      label: const Text('Import'),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Tabs
            const TabBar(
              tabs: [
                Tab(text: 'Visit Windows'),
                Tab(text: 'Consent Types'),
                Tab(text: 'General'),
              ],
            ),

            const SizedBox(height: 16),

            // Tab content
            Expanded(
              child: TabBarView(
                children: [
                  _VisitWindowsTab(studyId: widget.study.id!),
                  _ConsentTypesTab(),
                  _GeneralTab(study: widget.study),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _exportConfig() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Configuration exported!')),
    );
  }

  void _importConfig() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Configuration imported!')),
    );
  }
}

class _VisitWindowsTab extends StatefulWidget {
  final int studyId;

  const _VisitWindowsTab({required this.studyId});

  @override
  State<_VisitWindowsTab> createState() => _VisitWindowsTabState();
}

class _VisitWindowsTabState extends State<_VisitWindowsTab> {
  List<VisitConfig> _configs = [];
  bool _isLoading = true;
  bool _isImporting = false;

  @override
  void initState() {
    super.initState();
    _loadConfigs();
  }

  Future<void> _loadConfigs() async {
    setState(() => _isLoading = true);
    try {
      final configs = await DatabaseService.getVisitConfigs(widget.studyId);
      setState(() {
        _configs = configs.isNotEmpty ? configs : List.from(defaultVisitConfigs);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _configs = List.from(defaultVisitConfigs);
        _isLoading = false;
      });
    }
  }

  void _resetToDefaults() {
    setState(() {
      _configs = List.from(defaultVisitConfigs);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Reset to defaults!')),
    );
  }

  Future<void> _importFromSoA() async {
    setState(() => _isImporting = true);

    try {
      // Ouvrir le file picker
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['docx', 'doc'],
        withData: true,
      );

      if (result == null || result.files.isEmpty) {
        setState(() => _isImporting = false);
        return;
      }

      final file = result.files.first;
      if (file.bytes == null) {
        throw Exception('Could not read file');
      }

      // Parser le fichier
      final parseResult = await SoaParserService.parseDocx(file.bytes!);

      setState(() => _isImporting = false);

      if (!parseResult.success) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${parseResult.error}')),
          );
        }
        return;
      }

      // Afficher le dialog de preview
      if (mounted) {
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => _SoaPreviewDialog(
            visits: parseResult.visits,
            procedures: parseResult.procedures,
            fileName: file.name,
          ),
        );

        if (confirmed == true) {
          setState(() {
            _configs = parseResult.visits;
          });

          // Sauvegarder en base
          await DatabaseService.saveVisitConfigs(widget.studyId, _configs);

          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Imported ${_configs.length} visits from ${file.name}')),
            );
          }
        }
      }
    } catch (e) {
      setState(() => _isImporting = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Import error: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      children: [
        // Actions
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${_configs.length} visits configured',
              style: TextStyle(color: Colors.grey[400]),
            ),
            Row(
              children: [
                // Import from SoA button
                FilledButton.icon(
                  onPressed: _isImporting ? null : _importFromSoA,
                  icon: _isImporting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.upload_file),
                  label: Text(_isImporting ? 'Importing...' : 'Import from SoA'),
                  style: FilledButton.styleFrom(backgroundColor: Colors.green[700]),
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  onPressed: _resetToDefaults,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reset to Defaults'),
                ),
                const SizedBox(width: 12),
                FilledButton.icon(
                  onPressed: _showAddVisitDialog,
                  icon: const Icon(Icons.add),
                  label: const Text('Add Visit'),
                ),
              ],
            ),
          ],
        ),

        const SizedBox(height: 16),

        // Info card
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.blue.withAlpha(30),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue.withAlpha(100)),
          ),
          child: Row(
            children: [
              const Icon(Icons.info_outline, color: Colors.blue, size: 20),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Import your Schedule of Assessments (.docx) to automatically configure visit windows.',
                  style: TextStyle(color: Colors.blue[300], fontSize: 13),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Table
        Expanded(
          child: Container(
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
                      _TableHeader('Visit', flex: 1),
                      _TableHeader('Target Day', flex: 1),
                      _TableHeader('Window Before', flex: 1),
                      _TableHeader('Window After', flex: 1),
                      _TableHeader('Window Range', flex: 2),
                      _TableHeader('Actions', flex: 1),
                    ],
                  ),
                ),
                Expanded(
                  child: ListView.separated(
                    itemCount: _configs.length,
                    separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                    itemBuilder: (context, index) {
                      final config = _configs[index];
                      return _VisitConfigRow(
                        config: config,
                        onEdit: () => _showEditVisitDialog(index),
                        onDelete: () => _deleteVisit(index),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _showAddVisitDialog() {
    final nextNumber = _configs.isEmpty ? 1 : _configs.map((c) => c.visitNumber).reduce((a, b) => a > b ? a : b) + 1;
    showDialog(
      context: context,
      builder: (context) => _VisitConfigDialog(
        initialConfig: VisitConfig(
          visitNumber: nextNumber,
          visitName: 'V$nextNumber',
          targetDay: 0,
        ),
        onSave: (config) {
          setState(() {
            _configs.add(config);
            _configs.sort((a, b) => a.visitNumber.compareTo(b.visitNumber));
          });
          Navigator.pop(context);
        },
      ),
    );
  }

  void _showEditVisitDialog(int index) {
    showDialog(
      context: context,
      builder: (context) => _VisitConfigDialog(
        initialConfig: _configs[index],
        onSave: (config) {
          setState(() {
            _configs[index] = config;
          });
          Navigator.pop(context);
        },
      ),
    );
  }

  void _deleteVisit(int index) {
    if (_configs[index].isReference) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cannot delete reference visit')),
      );
      return;
    }
    setState(() {
      _configs.removeAt(index);
    });
  }
}

class _SoaPreviewDialog extends StatelessWidget {
  final List<VisitConfig> visits;
  final List<String> procedures;
  final String fileName;

  const _SoaPreviewDialog({
    required this.visits,
    required this.procedures,
    required this.fileName,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          const Icon(Icons.check_circle, color: Colors.green),
          const SizedBox(width: 12),
          Expanded(child: Text('Import from $fileName')),
        ],
      ),
      content: SizedBox(
        width: 600,
        height: 400,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${visits.length} visits detected:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[700]!),
                ),
                child: ListView.separated(
                  itemCount: visits.length,
                  separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                  itemBuilder: (context, index) {
                    final v = visits[index];
                    return ListTile(
                      dense: true,
                      leading: CircleAvatar(
                        radius: 14,
                        backgroundColor: v.isReference ? Colors.blue : Colors.grey[700],
                        child: Text(
                          '${v.visitNumber}',
                          style: const TextStyle(fontSize: 12, color: Colors.white),
                        ),
                      ),
                      title: Row(
                        children: [
                          Text(v.visitName, style: const TextStyle(fontWeight: FontWeight.bold)),
                          if (v.isReference) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.blue,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Text('REF', style: TextStyle(fontSize: 9, color: Colors.white)),
                            ),
                          ],
                        ],
                      ),
                      subtitle: Text(
                        v.isReference
                            ? 'Day 0 (Reference)'
                            : 'Day ${v.targetDay} (±${v.windowBefore}/${v.windowAfter})',
                        style: TextStyle(color: Colors.grey[400], fontSize: 12),
                      ),
                      trailing: Text(
                        v.isReference ? '-' : 'J${v.targetDay - v.windowBefore} - J${v.targetDay + v.windowAfter}',
                        style: TextStyle(color: Colors.grey[500], fontSize: 12),
                      ),
                    );
                  },
                ),
              ),
            ),
            if (procedures.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(
                '${procedures.length} procedures detected (preview):',
                style: TextStyle(color: Colors.grey[400], fontSize: 12),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: procedures.take(10).map((p) {
                  return Chip(
                    label: Text(p, style: const TextStyle(fontSize: 11)),
                    padding: EdgeInsets.zero,
                    visualDensity: VisualDensity.compact,
                  );
                }).toList(),
              ),
              if (procedures.length > 10)
                Text(
                  '... and ${procedures.length - 10} more',
                  style: TextStyle(color: Colors.grey[500], fontSize: 11),
                ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Cancel'),
        ),
        FilledButton.icon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.check),
          label: const Text('Import'),
        ),
      ],
    );
  }
}

class _VisitConfigDialog extends StatefulWidget {
  final VisitConfig initialConfig;
  final Function(VisitConfig) onSave;

  const _VisitConfigDialog({required this.initialConfig, required this.onSave});

  @override
  State<_VisitConfigDialog> createState() => _VisitConfigDialogState();
}

class _VisitConfigDialogState extends State<_VisitConfigDialog> {
  late TextEditingController _nameController;
  late TextEditingController _dayController;
  late TextEditingController _windowBeforeController;
  late TextEditingController _windowAfterController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.initialConfig.visitName);
    _dayController = TextEditingController(text: widget.initialConfig.targetDay.toString());
    _windowBeforeController = TextEditingController(text: widget.initialConfig.windowBefore.toString());
    _windowAfterController = TextEditingController(text: widget.initialConfig.windowAfter.toString());
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.initialConfig.visitNumber == 0 ? 'Add Visit' : 'Edit ${widget.initialConfig.visitName}'),
      content: SizedBox(
        width: 350,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Visit Name'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _dayController,
              decoration: const InputDecoration(labelText: 'Target Day'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _windowBeforeController,
                    decoration: const InputDecoration(labelText: 'Window Before (-)'),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _windowAfterController,
                    decoration: const InputDecoration(labelText: 'Window After (+)'),
                    keyboardType: TextInputType.number,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () {
            final config = VisitConfig(
              visitNumber: widget.initialConfig.visitNumber,
              visitName: _nameController.text,
              targetDay: int.tryParse(_dayController.text) ?? 0,
              windowBefore: int.tryParse(_windowBeforeController.text) ?? 0,
              windowAfter: int.tryParse(_windowAfterController.text) ?? 0,
            );
            widget.onSave(config);
          },
          child: const Text('Save'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _dayController.dispose();
    _windowBeforeController.dispose();
    _windowAfterController.dispose();
    super.dispose();
  }
}

class _VisitConfigRow extends StatelessWidget {
  final VisitConfig config;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _VisitConfigRow({
    required this.config,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final isValid = config.windowBefore <= config.targetDay || config.isReference;
    final minDay = config.targetDay - config.windowBefore;
    final maxDay = config.targetDay + config.windowAfter;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: config.isReference ? Colors.blue.withAlpha(25) : (!isValid ? Colors.red.withAlpha(25) : null),
      child: Row(
        children: [
          Expanded(
            flex: 1,
            child: Row(
              children: [
                Text(config.visitName, style: const TextStyle(fontWeight: FontWeight.bold)),
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
          Expanded(
            flex: 1,
            child: Text(config.isReference ? '-' : 'J${config.targetDay}'),
          ),
          Expanded(
            flex: 1,
            child: Text(config.isReference ? '-' : '-${config.windowBefore}'),
          ),
          Expanded(
            flex: 1,
            child: Text(config.isReference ? '-' : '+${config.windowAfter}'),
          ),
          Expanded(
            flex: 2,
            child: config.isReference
                ? const Text('-')
                : Text(
                    'J$minDay - J$maxDay',
                    style: TextStyle(color: Colors.grey[400]),
                  ),
          ),
          Expanded(
            flex: 1,
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.edit, size: 18),
                  onPressed: onEdit,
                  tooltip: 'Edit',
                ),
                if (!config.isReference)
                  IconButton(
                    icon: const Icon(Icons.delete, size: 18, color: Colors.red),
                    onPressed: onDelete,
                    tooltip: 'Delete',
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ConsentTypesTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Types
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Consent Types', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.add),
                    onPressed: () {},
                    tooltip: 'Add Type',
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey[800]!),
                  ),
                  child: ListView.separated(
                    itemCount: defaultConsentTypes.length,
                    separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                    itemBuilder: (context, index) {
                      final type = defaultConsentTypes[index];
                      return ListTile(
                        leading: const Icon(Icons.description),
                        title: Text(type.name),
                        subtitle: Text('Code: ${type.code}'),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete, size: 18, color: Colors.red),
                          onPressed: () {},
                        ),
                      );
                    },
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(width: 24),

        // Versions
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Versions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.add),
                    onPressed: () {},
                    tooltip: 'Add Version',
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey[800]!),
                  ),
                  child: ListView.separated(
                    itemCount: defaultConsentVersions.length,
                    separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                    itemBuilder: (context, index) {
                      final version = defaultConsentVersions[index];
                      final typeName = defaultConsentTypes
                          .firstWhere((t) => t.id == version.typeId, orElse: () => const ConsentType(name: '?', code: '?'))
                          .name;
                      return ListTile(
                        leading: Icon(
                          version.isCurrent ? Icons.star : Icons.history,
                          color: version.isCurrent ? Colors.amber : Colors.grey,
                        ),
                        title: Text('$typeName - ${version.version}'),
                        subtitle: Text('Date: ${DateFormat('yyyy-MM-dd').format(version.date)}'),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (version.isCurrent)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.green,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: const Text('Current', style: TextStyle(fontSize: 10, color: Colors.white)),
                              ),
                            IconButton(
                              icon: const Icon(Icons.delete, size: 18, color: Colors.red),
                              onPressed: () {},
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _GeneralTab extends StatelessWidget {
  final Study study;

  const _GeneralTab({required this.study});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Study info card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Study Information', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  _InfoRow(label: 'Study Number', value: study.number),
                  _InfoRow(label: 'Study Name', value: study.name),
                  _InfoRow(label: 'Phase', value: study.phase ?? '-'),
                  _InfoRow(label: 'Sponsor', value: study.sponsor ?? '-'),
                  _InfoRow(label: 'Pathology', value: study.pathology ?? '-'),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Export options
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Export Options', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      FilledButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Use Export Excel button in Dashboard')),
                          );
                        },
                        icon: const Icon(Icons.table_chart),
                        label: const Text('Export to Excel'),
                      ),
                      OutlinedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.picture_as_pdf),
                        label: const Text('Export to PDF'),
                      ),
                      OutlinedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.code),
                        label: const Text('Export to JSON'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Danger zone
          Card(
            color: Colors.red.withAlpha(25),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.warning, color: Colors.red),
                      SizedBox(width: 8),
                      Text('Danger Zone', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.red)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  OutlinedButton.icon(
                    onPressed: () {},
                    style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                    icon: const Icon(Icons.delete_forever),
                    label: const Text('Delete Study'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 150,
            child: Text(label, style: TextStyle(color: Colors.grey[400])),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
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
