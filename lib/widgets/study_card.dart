import 'package:flutter/material.dart';
import '../models/study.dart';

/// Carte d'étude pour la landing page
class StudyCard extends StatelessWidget {
  final Study study;
  final VoidCallback? onTap;

  const StudyCard({
    super.key,
    required this.study,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Container(
          width: 300,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header: numéro + badge phase
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    study.number,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[400],
                    ),
                  ),
                  _PhaseBadge(phase: study.phase ?? '-', color: study.phaseColor),
                ],
              ),

              const SizedBox(height: 12),

              // Nom de l'étude
              Text(
                study.name,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 8),

              // Sponsor & pathologie
              Text(
                study.sponsor ?? '-',
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey[400],
                ),
              ),
              Text(
                study.pathology ?? '-',
                style: const TextStyle(fontSize: 13),
              ),

              const Divider(height: 24),

              // Stats
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _StatChip(
                    icon: Icons.person,
                    label: '${study.patientCount} patients',
                    color: Colors.blue,
                  ),
                  _StatChip(
                    icon: Icons.location_on,
                    label: '${study.siteCount} sites',
                    color: Colors.green,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Badge de phase coloré
class _PhaseBadge extends StatelessWidget {
  final String phase;
  final int color;

  const _PhaseBadge({required this.phase, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: Color(color),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        'Phase $phase',
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    );
  }
}

/// Chip de statistique avec icône
class _StatChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _StatChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
