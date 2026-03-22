import 'package:flutter/material.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../models/site.dart';
import '../services/database_service.dart';
import '../services/excel_export_service.dart';
import '../services/file_download_service.dart';

class DashboardScreen extends StatefulWidget {
  final Study study;

  const DashboardScreen({super.key, required this.study});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<Patient> _patients = [];
  List<StudySite> _sites = [];
  bool _isLoading = true;
  bool _isExporting = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final patients = await DatabaseService.getPatients(widget.study.id!);
      final sites = await DatabaseService.getStudySites(widget.study.id!);
      setState(() {
        _patients = patients;
        _sites = sites;
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

  Future<void> _exportToExcel() async {
    setState(() => _isExporting = true);
    try {
      final bytes = await ExcelExportService.exportStudy(widget.study);
      final fileName = '${widget.study.studyNumber}_export.xlsx';
      FileDownloadService.downloadFile(bytes, fileName);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Exported: $fileName')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export error: $e')),
        );
      }
    } finally {
      setState(() => _isExporting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    // Stats calculees
    final totalPatients = _patients.length;
    final screeningCount = _patients.where((p) => p.status == PatientStatus.screening).length;
    final includedCount = _patients.where((p) => p.status == PatientStatus.included).length;
    final completedCount = _patients.where((p) => p.status == PatientStatus.completed).length;

    final totalSites = _sites.length;
    final activeSites = _sites.where((s) => s.status == SiteStatus.active).length;
    final totalTarget = _sites.fold<int>(0, (sum, s) => sum + s.targetPatients);

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // En-tete etude
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.study.name,
                          style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            _InfoChip(label: widget.study.number, icon: Icons.tag),
                            const SizedBox(width: 12),
                            _InfoChip(label: 'Phase ${widget.study.phase ?? "-"}', icon: Icons.science),
                            const SizedBox(width: 12),
                            _InfoChip(label: widget.study.sponsor ?? '-', icon: Icons.business),
                            const SizedBox(width: 12),
                            _InfoChip(label: widget.study.pathology ?? '-', icon: Icons.medical_services),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  // Bouton Export Excel
                  FilledButton.icon(
                    onPressed: _isExporting ? null : _exportToExcel,
                    icon: _isExporting
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Icon(Icons.download),
                    label: Text(_isExporting ? 'Exporting...' : 'Export Excel'),
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.green[700],
                    ),
                  ),
                  const SizedBox(width: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.green.withAlpha(50),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.circle, size: 10, color: Colors.green),
                        const SizedBox(width: 8),
                        Text(widget.study.status, style: const TextStyle(color: Colors.green, fontWeight: FontWeight.w500)),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 32),

              // Cartes de stats principales
              Row(
                children: [
                  Expanded(child: _DashboardCard(
                    title: 'Recruitment',
                    value: '$includedCount / $totalTarget',
                    subtitle: '${(totalTarget > 0 ? (includedCount / totalTarget * 100) : 0).toStringAsFixed(0)}% of target',
                    icon: Icons.people,
                    color: Colors.blue,
                    progress: totalTarget > 0 ? includedCount / totalTarget : 0,
                  )),
                  const SizedBox(width: 24),
                  Expanded(child: _DashboardCard(
                    title: 'Sites',
                    value: '$activeSites / $totalSites',
                    subtitle: 'Active sites',
                    icon: Icons.location_on,
                    color: Colors.green,
                  )),
                  const SizedBox(width: 24),
                  Expanded(child: _DashboardCard(
                    title: 'Screening',
                    value: '$screeningCount',
                    subtitle: 'Patients in screening',
                    icon: Icons.hourglass_empty,
                    color: Colors.orange,
                  )),
                  const SizedBox(width: 24),
                  Expanded(child: _DashboardCard(
                    title: 'Completed',
                    value: '$completedCount',
                    subtitle: 'Patients completed',
                    icon: Icons.check_circle,
                    color: Colors.purple,
                  )),
                ],
              ),

              const SizedBox(height: 32),

              // Deux colonnes
              IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Colonne gauche - Sites
                    Expanded(
                      child: _DashboardSection(
                        title: 'Sites Overview',
                        action: TextButton(
                          onPressed: () {},
                          child: const Text('View All'),
                        ),
                        child: _sites.isEmpty
                            ? Center(child: Text('No sites', style: TextStyle(color: Colors.grey[500])))
                            : Column(
                                children: _sites.take(4).map((site) => _SiteListItem(site: site)).toList(),
                              ),
                      ),
                    ),
                    const SizedBox(width: 24),
                    // Colonne droite - Patients recents
                    Expanded(
                      child: _DashboardSection(
                        title: 'Recent Patients',
                        action: TextButton(
                          onPressed: () {},
                          child: const Text('View All'),
                        ),
                        child: _patients.isEmpty
                            ? Center(child: Text('No patients', style: TextStyle(color: Colors.grey[500])))
                            : Column(
                                children: _patients.take(5).map((patient) => _PatientListItem(patient: patient)).toList(),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final String label;
  final IconData icon;

  const _InfoChip({required this.label, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.grey[850],
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.grey[400]),
          const SizedBox(width: 6),
          Text(label, style: TextStyle(fontSize: 13, color: Colors.grey[300])),
        ],
      ),
    );
  }
}

class _DashboardCard extends StatelessWidget {
  final String title;
  final String value;
  final String subtitle;
  final IconData icon;
  final Color color;
  final double? progress;

  const _DashboardCard({
    required this.title,
    required this.value,
    required this.subtitle,
    required this.icon,
    required this.color,
    this.progress,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 175,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: TextStyle(fontSize: 14, color: Colors.grey[400])),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withAlpha(50),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 20, color: color),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(subtitle, style: TextStyle(fontSize: 12, color: Colors.grey[500])),
          const Spacer(),
          if (progress != null) ...[
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: progress!.clamp(0.0, 1.0),
              backgroundColor: Colors.grey[800],
              color: color,
            ),
          ],
        ],
      ),
    );
  }
}

class _DashboardSection extends StatelessWidget {
  final String title;
  final Widget? action;
  final Widget child;

  const _DashboardSection({
    required this.title,
    this.action,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              if (action != null) action!,
            ],
          ),
          const Divider(height: 24),
          child,
        ],
      ),
    );
  }
}

class _SiteListItem extends StatelessWidget {
  final StudySite site;

  const _SiteListItem({required this.site});

  @override
  Widget build(BuildContext context) {
    final statusColor = site.status == SiteStatus.active ? Colors.green : Colors.orange;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: statusColor,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(site.siteName ?? '-', style: const TextStyle(fontWeight: FontWeight.w500)),
                Text('Site ${site.siteNumber ?? "-"}', style: TextStyle(fontSize: 12, color: Colors.grey[500])),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${site.patientCount}/${site.targetPatients}',
                style: TextStyle(
                  color: site.patientCount >= site.targetPatients ? Colors.green : Colors.orange,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(site.status.label, style: TextStyle(fontSize: 11, color: Colors.grey[500])),
            ],
          ),
        ],
      ),
    );
  }
}

class _PatientListItem extends StatelessWidget {
  final Patient patient;

  const _PatientListItem({required this.patient});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: Color(patient.status.color).withAlpha(50),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Center(
              child: Text(
                patient.initials ?? '?',
                style: TextStyle(
                  color: Color(patient.status.color),
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(patient.patientNumber, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text('Site ${patient.siteId ?? "-"}', style: TextStyle(fontSize: 12, color: Colors.grey[500])),
              ],
            ),
          ),
          Container(
            width: 85,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Color(patient.status.color),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              patient.status.label,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }
}
