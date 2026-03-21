import 'package:flutter/material.dart';
import '../models/site.dart';

/// Badge de statut coloré
class StatusBadge extends StatelessWidget {
  final SiteStatus status;

  const StatusBadge({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 70,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: Color(status.color),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        status.label,
        textAlign: TextAlign.center,
        style: const TextStyle(
          fontSize: 11,
          color: Colors.white,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
