import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/study.dart';
import '../models/site.dart';
import '../widgets/stat_card.dart';
import '../widgets/status_badge.dart';
import 'site_detail_screen.dart';

/// Données de démo pour les sites
final List<StudySite> demoSites = [
  StudySite(
    id: 1,
    studyId: 1,
    siteId: 1,
    siteNumber: '001',
    siteName: 'CHU Paris',
    principalInvestigator: 'Dr. Martin',
    status: SiteStatus.active,
    activationDate: DateTime(2026, 1, 15),
    firstPatientDate: DateTime(2026, 2, 1),
    targetPatients: 10,
    patientCount: 8,
  ),
  StudySite(
    id: 2,
    studyId: 1,
    siteId: 2,
    siteNumber: '002',
    siteName: 'Hôpital Lyon',
    principalInvestigator: 'Dr. Dubois',
    status: SiteStatus.active,
    activationDate: DateTime(2026, 2, 1),
    firstPatientDate: DateTime(2026, 2, 20),
    targetPatients: 8,
    patientCount: 5,
  ),
  StudySite(
    id: 3,
    studyId: 1,
    siteId: 3,
    siteNumber: '003',
    siteName: 'CHU Marseille',
    principalInvestigator: 'Dr. Bernard',
    status: SiteStatus.onHold,
    activationDate: DateTime(2026, 1, 20),
    targetPatients: 12,
    patientCount: 3,
  ),
  StudySite(
    id: 4,
    studyId: 1,
    siteId: 4,
    siteNumber: '004',
    siteName: 'Clinique Bordeaux',
    principalInvestigator: 'Dr. Petit',
    status: SiteStatus.active,
    activationDate: DateTime(2026, 3, 1),
    targetPatients: 6,
    patientCount: 0,
  ),
];

class SitesScreen extends StatefulWidget {
  final Study study;

  const SitesScreen({super.key, required this.study});

  @override
  State<SitesScreen> createState() => _SitesScreenState();
}

class _SitesScreenState extends State<SitesScreen> {
  final TextEditingController _searchController = TextEditingController();
  SiteStatus? _statusFilter;
  List<StudySite> _filteredSites = demoSites;

  final _dateFormat = DateFormat('yyyy-MM-dd');

  void _applyFilters() {
    setState(() {
      _filteredSites = demoSites.where((site) {
        final query = _searchController.text.toLowerCase();
        final matchesSearch = query.isEmpty ||
            (site.siteNumber?.toLowerCase().contains(query) ?? false) ||
            (site.siteName?.toLowerCase().contains(query) ?? false) ||
            (site.principalInvestigator?.toLowerCase().contains(query) ?? false);

        final matchesStatus = _statusFilter == null || site.status == _statusFilter;

        return matchesSearch && matchesStatus;
      }).toList();
    });
  }

  void _showEditDialog(StudySite site) {
    showDialog(
      context: context,
      builder: (context) => _SiteEditDialog(site: site),
    );
  }

  @override
  Widget build(BuildContext context) {
    final totalSites = _filteredSites.length;
    final activeSites = _filteredSites.where((s) => s.status == SiteStatus.active).length;
    final onHoldSites = _filteredSites.where((s) => s.status == SiteStatus.onHold).length;
    final totalIncluded = _filteredSites.fold<int>(0, (sum, s) => sum + s.patientCount);
    final totalTarget = _filteredSites.fold<int>(0, (sum, s) => sum + s.targetPatients);

    return Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Sites',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                FilledButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Add site dialog...')),
                    );
                  },
                  icon: const Icon(Icons.add),
                  label: const Text('Add Site'),
                ),
              ],
            ),

            const SizedBox(height: 24),

            StatsBar(
              stats: [
                StatCard(value: '$totalSites', label: 'Total', color: Colors.grey),
                StatCard(value: '$activeSites', label: 'Active', color: Colors.green),
                StatCard(value: '$onHoldSites', label: 'On Hold', color: Colors.orange),
                StatCard(value: '$totalIncluded/$totalTarget', label: 'Recruitment', color: Colors.blue),
              ],
            ),

            const SizedBox(height: 24),

            Row(
              children: [
                SizedBox(
                  width: 250,
                  child: TextField(
                    controller: _searchController,
                    onChanged: (_) => _applyFilters(),
                    decoration: InputDecoration(
                      hintText: 'Search sites...',
                      prefixIcon: const Icon(Icons.search),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                SizedBox(
                  width: 150,
                  child: DropdownButtonFormField<SiteStatus?>(
                    value: _statusFilter,
                    decoration: InputDecoration(
                      labelText: 'Status',
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All')),
                      ...SiteStatus.values.map((status) {
                        return DropdownMenuItem(value: status, child: Text(status.label));
                      }),
                    ],
                    onChanged: (value) {
                      _statusFilter = value;
                      _applyFilters();
                    },
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

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
                          _TableHeader('Site #', flex: 1),
                          _TableHeader('Name', flex: 2),
                          _TableHeader('PI', flex: 2),
                          _TableHeader('Status', flex: 1),
                          _TableHeader('Activation', flex: 1),
                          _TableHeader('Progress', flex: 2),
                          _TableHeader('FPI', flex: 1),
                          _TableHeader('Actions', flex: 1),
                        ],
                      ),
                    ),
                    Expanded(
                      child: ListView.separated(
                        itemCount: _filteredSites.length,
                        separatorBuilder: (_, __) => Divider(height: 1, color: Colors.grey[800]),
                        itemBuilder: (context, index) {
                          final site = _filteredSites[index];
                          return _SiteRow(
                            site: site,
                            dateFormat: _dateFormat,
                            onEdit: () => _showEditDialog(site),
                            onDelete: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Delete ${site.siteNumber}?')),
                              );
                            },
                            onTapSiteNumber: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => SiteDetailScreen(site: site),
                                ),
                              );
                            },
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
  final double? width;
  final int? flex;

  const _TableHeader(this.text, {this.width, this.flex});

  @override
  Widget build(BuildContext context) {
    final child = Text(text, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12));
    if (width != null) return SizedBox(width: width, child: child);
    return Expanded(flex: flex ?? 1, child: child);
  }
}

class _SiteRow extends StatelessWidget {
  final StudySite site;
  final DateFormat dateFormat;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  final VoidCallback onTapSiteNumber;

  const _SiteRow({
    required this.site,
    required this.dateFormat,
    required this.onEdit,
    required this.onDelete,
    required this.onTapSiteNumber,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Expanded(
            flex: 1,
            child: InkWell(
              onTap: onTapSiteNumber,
              child: Text(
                site.siteNumber ?? '-',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(site.siteName ?? '-', overflow: TextOverflow.ellipsis),
          ),
          Expanded(
            flex: 2,
            child: Text(site.principalInvestigator ?? '-', style: const TextStyle(fontSize: 12), overflow: TextOverflow.ellipsis),
          ),
          Expanded(
            flex: 1,
            child: Align(
              alignment: Alignment.centerLeft,
              child: StatusBadge(status: site.status),
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              site.activationDate != null ? dateFormat.format(site.activationDate!) : '-',
              style: const TextStyle(fontSize: 12),
            ),
          ),
          Expanded(
            flex: 2,
            child: Row(
              children: [
                Text(
                  '${site.patientCount}/${site.targetPatients}',
                  style: TextStyle(color: Color(site.progressColor), fontWeight: FontWeight.w500),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(right: 16),
                    child: LinearProgressIndicator(
                      value: site.recruitmentProgress.clamp(0.0, 1.0),
                      backgroundColor: Colors.grey[800],
                      color: Color(site.progressColor),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            flex: 1,
            child: Text(
              site.firstPatientDate != null ? dateFormat.format(site.firstPatientDate!) : '-',
              style: const TextStyle(fontSize: 12),
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

class _SiteEditDialog extends StatefulWidget {
  final StudySite site;

  const _SiteEditDialog({required this.site});

  @override
  State<_SiteEditDialog> createState() => _SiteEditDialogState();
}

class _SiteEditDialogState extends State<_SiteEditDialog> {
  late TextEditingController _piController;
  late TextEditingController _targetController;
  late SiteStatus _status;

  @override
  void initState() {
    super.initState();
    _piController = TextEditingController(text: widget.site.principalInvestigator ?? '');
    _targetController = TextEditingController(text: widget.site.targetPatients.toString());
    _status = widget.site.status;
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Edit Site ${widget.site.siteNumber}'),
      content: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: _piController, decoration: const InputDecoration(labelText: 'Principal Investigator')),
            const SizedBox(height: 16),
            DropdownButtonFormField<SiteStatus>(
              value: _status,
              decoration: const InputDecoration(labelText: 'Status'),
              items: SiteStatus.values.map((status) => DropdownMenuItem(value: status, child: Text(status.label))).toList(),
              onChanged: (value) {
                if (value != null) setState(() => _status = value);
              },
            ),
            const SizedBox(height: 16),
            TextField(controller: _targetController, decoration: const InputDecoration(labelText: 'Recruitment Target'), keyboardType: TextInputType.number),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: () {
            Navigator.pop(context);
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Site updated!')));
          },
          child: const Text('Save'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _piController.dispose();
    _targetController.dispose();
    super.dispose();
  }
}
