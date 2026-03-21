import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/visit.dart';
import '../models/document.dart';

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
                  _VisitWindowsTab(),
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
  @override
  State<_VisitWindowsTab> createState() => _VisitWindowsTabState();
}

class _VisitWindowsTabState extends State<_VisitWindowsTab> {
  late List<VisitConfig> _configs;

  @override
  void initState() {
    super.initState();
    _configs = List.from(defaultVisitConfigs);
  }

  void _resetToDefaults() {
    setState(() {
      _configs = List.from(defaultVisitConfigs);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Reset to defaults!')),
    );
  }

  @override
  Widget build(BuildContext context) {
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
                OutlinedButton.icon(
                  onPressed: _resetToDefaults,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reset to Defaults'),
                ),
                const SizedBox(width: 12),
                FilledButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.add),
                  label: const Text('Add Visit'),
                ),
              ],
            ),
          ],
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
                      return _VisitConfigRow(config: config);
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
}

class _VisitConfigRow extends StatelessWidget {
  final VisitConfig config;

  const _VisitConfigRow({required this.config});

  @override
  Widget build(BuildContext context) {
    final isValid = config.windowBefore <= config.targetDay || config.isReference;
    final minDay = config.targetDay - config.windowBefore;
    final maxDay = config.targetDay + config.windowAfter;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: config.isReference ? Colors.blue.withOpacity(0.1) : (!isValid ? Colors.red.withOpacity(0.1) : null),
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
                  onPressed: () {},
                  tooltip: 'Edit',
                ),
                if (!config.isReference)
                  IconButton(
                    icon: const Icon(Icons.delete, size: 18, color: Colors.red),
                    onPressed: () {},
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
                            const SnackBar(content: Text('Excel export coming soon!')),
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
            color: Colors.red.withOpacity(0.1),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.warning, color: Colors.red),
                      const SizedBox(width: 8),
                      const Text('Danger Zone', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.red)),
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
