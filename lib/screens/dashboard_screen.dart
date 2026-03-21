import 'package:flutter/material.dart';
import '../models/study.dart';
import '../models/patient.dart';
import '../models/site.dart';
import '../screens/sites_screen.dart';

class DashboardScreen extends StatelessWidget {
  final Study study;

  const DashboardScreen({super.key, required this.study});

  @override
  Widget build(BuildContext context) {
    // Stats calculees
    final totalPatients = demoPatients.length;
    final screeningCount = demoPatients.where((p) => p.status == PatientStatus.screening).length;
    final includedCount = demoPatients.where((p) => p.status == PatientStatus.included).length;
    final completedCount = demoPatients.where((p) => p.status == PatientStatus.completed).length;

    final totalSites = demoSites.length;
    final activeSites = demoSites.where((s) => s.status == SiteStatus.active).length;
    final totalTarget = demoSites.fold<int>(0, (sum, s) => sum + s.targetPatients);

    return SingleChildScrollView(
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
                        study.name,
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          _InfoChip(label: study.number, icon: Icons.tag),
                          const SizedBox(width: 12),
                          _InfoChip(label: 'Phase ${study.phase ?? "-"}', icon: Icons.science),
                          const SizedBox(width: 12),
                          _InfoChip(label: study.sponsor ?? '-', icon: Icons.business),
                          const SizedBox(width: 12),
                          _InfoChip(label: study.pathology ?? '-', icon: Icons.medical_services),
                        ],
                      ),
                    ],
                  ),
                ),
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
                      Text(study.status, style: const TextStyle(color: Colors.green, fontWeight: FontWeight.w500)),
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
                  // Colonne gauche - Sites recents
                  Expanded(
                    child: _DashboardSection(
                      title: 'Sites Overview',
                      action: TextButton(
                        onPressed: () {},
                        child: const Text('View All'),
                      ),
                      child: Column(
                        children: demoSites.take(4).map((site) => _SiteListItem(site: site)).toList(),
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
                      child: Column(
                        children: demoPatients.take(5).map((patient) => _PatientListItem(patient: patient)).toList(),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
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
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: Color(site.status.color),
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
                style: TextStyle(color: Color(site.progressColor), fontWeight: FontWeight.w500),
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
